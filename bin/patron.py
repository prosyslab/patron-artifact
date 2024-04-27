#!/usr/bin/env python3
import config
import os
from logger import log, INFO, ERROR, WARNING
import subprocess
import json
import csv
import datetime
from threading import Thread
from time import sleep
import time

expriment_ready_to_go = {
    "patron": [
        "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13",
        "14", "15", "16", "17", "18", "19", "20"
    ],
    "patchweave": [
        "1", "2-1", "3", "4", "6", "7", "8", "9-1", "10",
        "12-1", "13", "17", "19", "21", "22", "24"
    ]
    }
level = ""
donor_list = []
jobs_finished = []

def manage_patch_status(out_dir, current_job, job_cnt):
    global jobs_finished
    log(INFO, "Status Manager is Running!")
    with open(os.path.join(out_dir, "status.tsv"), 'a') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(["Donee Name", "Donor Benchmark", "Donor #", "Donee #", "Pattern Type","Correct?", "Diff"])
        f.flush()
        while current_job == "" and not jobs_finished[job_cnt]:
                time.sleep(10)
        dir_cache = os.listdir(out_dir)
        while not jobs_finished[job_cnt]:
            if len(dir_cache) != len(os.listdir(out_dir)):
                new_files = set(os.listdir(out_dir)) - set(dir_cache)
                for file in new_files:
                    if file.endswith('.patch'):
                        diff = ""
                        while diff == "":
                            with open(os.path.join(out_dir, file), 'r') as df:
                                diff = df.read()
                                if diff == "" and not jobs_finished[job_cnt]:
                                    continue
                                else:
                                    file_parsed = file.split('.')[0].split('_')
                                    donee_num = file_parsed[1].strip()
                                    for infof in os.listdir(out_dir):
                                        if infof.endswith('.c') and donee_num in infof:
                                            parsed_info = infof.split('_')[1:]
                                            tmp_list = parsed_info[0].split('-')
                                            benchmark = tmp_list[0].strip()
                                            donor_num = tmp_list[1].strip()
                                            pattern = "ALT" if parsed_info[-1].strip() == "1" else "NORMAL"
                                            writer.writerow([current_job, benchmark, donor_num, donee_num, pattern, "-", diff])
                                            f.flush()
                                    break
            else:
                time.sleep(10)

def run_patron(cmd, job_cnt):
    os.chdir(config.configuration["PATRON_ROOT_PATH"])
    current_job = os.path.basename(cmd[2])
    sub_out_dir = cmd[-1]
    status_manager = Thread(target=manage_patch_status, args=(sub_out_dir, current_job, job_cnt))
    status_manager.start()
    log(INFO, f"Running patron with {cmd}")
    return status_manager, subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        

def mk_worklist():
    base_cmd = [config.configuration["PATRON_BIN_PATH"]]
    worklist = []
    cnt = 0
    for donee in config.configuration["DONEE_LIST"]:
        package = donee.split('/')[-1]
        sub_out = os.path.join(config.configuration["OUT_DIR"], package)
        db_opt = ["--db", os.path.join(config.configuration["DB_PATH"])]
        if not os.path.exists(sub_out):
            os.mkdir(sub_out)
        else:
            os.mkdir(sub_out + "_" + str(cnt))
            sub_out = sub_out + "_" + str(cnt)
        out_opt = ["-o", sub_out]
        worklist.append(base_cmd + ['patch', donee] + db_opt + out_opt)
        cnt += 1
    return worklist

def run_sparrow():
    log(WARNING, f"Running sparrow to construct databse from scratch...")
    os.chdir(config.configuration["EXP_ROOT_PATH"])
    log(INFO, "Detailed log will be saved in {}".format(os.path.join(config.configuration["EXP_ROOT_PATH"], 'out')))
    log(INFO, "Running sparrow for patchweave benchmarks...")
    result_patchweave = subprocess.Popen(['python3', 'bin/run.py', '-sparrow', 'patchweave', '-p'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result_patchweave.wait()
    if result_patchweave.returncode != 0:
        log(ERROR, f"Failed to run sparrow for patchweave.")
        log(ERROR, result_patchweave.stderr.read().decode('utf-8'))
        exit(1)
    log(INFO, "Running sparrow for patron benchmarks...")
    result_patron = subprocess.Popen(['python3', 'bin/run.py', '-sparrow', 'patron', '-p'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result_patron.wait()
    if result_patron.returncode != 0:
        log(ERROR, f"Failed to run sparrow for patron.")
        log(ERROR, result_patron.stderr.read().decode('utf-8'))
        exit(1)
    
def check_donee(donees):
    for donee in donees:
        if not os.path.exists(donee):
            log(ERROR, f"{donee} does not exist.")
            return False
        c_files = [f for f in os.listdir(donee) if f.endswith('.c')]
        if len(c_files) == 0 or len(c_files) > 1:
            log(ERROR, f"Either there is no donee file or more than one exist in {donee}.")
            return False
        if not os.path.exists(os.path.join(donee, 'sparrow-out')):
            log(ERROR, f"sparrow-out does not exist in {donee}.")
            return False
    return True

def check_sparrow():
    global donor_list
    patron_bench_path = os.path.join(config.configuration["BENCHMARK_PATH"], "patron")
    patchweave_bench_path = os.path.join(config.configuration["BENCHMARK_PATH"], "patchweave")
    for file in os.listdir(patron_bench_path):
        if file.endswith('.sh'):
            continue
        if file in expriment_ready_to_go["patron"]:
            if not os.path.exists(os.path.join(patron_bench_path, file, 'bug', 'sparrow-out')):
                log(ERROR, f"sparrow-out for {file} does not exist in {patron_bench_path}")
                return False
            donor_list.append(os.path.join(patron_bench_path, file))
    for file in os.listdir(patchweave_bench_path):
        if file in expriment_ready_to_go["patchweave"]:
            if not os.path.exists(os.path.join(patchweave_bench_path, file, 'donor', 'bug', 'sparrow-out')):           
                log(ERROR, f"sparrow-out for {file} does not exist in {patchweave_bench_path}")
                return False
            donor_list.append(os.path.join(patchweave_bench_path, file, 'donor'))
    return True            

def mk_database():
    tsv_file = open(os.path.join(config.configuration["OUT_DIR"], "database_{}.tsv".format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))), 'a')
    writer = csv.writer(tsv_file, delimiter='\t')
    writer.writerow(["BENCHMARK", "ID", "STATUS"])
    tsv_file.flush()
    log(WARNING, f"Creating patron-DB from scratch...")
    os.chdir(config.configuration["PATRON_ROOT_PATH"])
    if os.path.join(config.configuration["PATRON_ROOT_PATH"], 'patron-DB'):
        subprocess.run(['rm', '-rf', 'patron-DB'])
    cmd = [config.configuration["PATRON_BIN_PATH"], "db"]
    for donor in donor_list:
        log(INFO, f"Creating patron-DB for {donor} ...")
        if donor.endswith('donor'):
            label = os.path.join(donor, '..', 'label.json')
            with open(label, 'r') as f:
                data = json.load(f)
                try:
                    true_alarm = data["DONOR"]["TRUE-ALARM"]["ALARM-DIR"][0]
                except IndexError:
                    log(ERROR, f"Failed to get true alarm for {donor}")
                    continue
        else:
            label = os.path.join(donor, 'label.json')
            with open(label, 'r') as f:
                data = json.load(f)
                try:
                    true_alarm = data["TRUE-ALARM"]["ALARM-DIR"][0]
                except IndexError:
                    log(ERROR, f"Failed to get true alarm for {donor}")
                    continue
        result = subprocess.Popen(cmd + [donor, true_alarm], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result.wait()
        if result.returncode != 0:
            log(ERROR, f"Failed to create patron-DB for {donor}")
            log(ERROR, result.stderr.read().decode('utf-8'))
            writer.writerow([donor.split('/')[-2], donor.split('/')[-1], "X"])
            tsv_file.flush()
        else:
            log(INFO, f"Successfully created patron-DB for {donor}")
            writer.writerow([donor.split('/')[-2], donor.split('/')[-1], "O"])
    log(INFO, "Successfully finished making patron-DB.")
    tsv_file.close()
    
def check_database():
    if not os.path.exists(os.path.join(config.configuration["PATRON_ROOT_PATH"], 'patron-DB')):
        log(ERROR, "patron-DB does not exist.")
        return False
    return True

def construct_database():
    check_sparrow()
    run_sparrow()
    mk_database()                      

def collect_job_results(PROCS, work_cnt):
    global jobs_finished
    for j in range(len(PROCS)):
        cmd, work_id, m, proc = PROCS[j]
        if proc.poll() is not None:
            jobs_finished[work_id] = True
            m.join()
            work_cnt -= 1
            if proc.returncode != 0:
                log(ERROR, f"Failed to run patron with {cmd}")
                log(ERROR, proc.stderr.read().decode('utf-8'))
            else:
                log(INFO, f"Successfully ran patron with {cmd}")
            PROCS.pop(j)
            break
    return PROCS, work_cnt

def main():
    global level
    global jobs_finished
    level = "PATRON"
    config.setup(level)
    if config.configuration["DATABASE_ONLY"]:
        construct_database()
        return    
    if not check_sparrow():
        run_sparrow()
    if not check_database():
        mk_database()
    if not check_donee(config.configuration["DONEE_LIST"]):
        log(ERROR, "DONEE is not ready.")
        exit(1)
    worklist = mk_worklist()
    work_cnt = 0
    PROCS = []
    for i in range(len(worklist)):
        jobs_finished.append(False)
        log(INFO, f"Worklist: {worklist[i]}")
        manager, p = run_patron(worklist[i], i)
        PROCS.append((worklist[i], i, manager, p))
        time.sleep(5)
        work_cnt += 1
        if work_cnt >= config.configuration["ARGS"].process:
            log(WARNING, "Waiting for the current jobs to finish...")
        while work_cnt >= config.configuration["ARGS"].process:
            PROCS, work_cnt = collect_job_results(PROCS, work_cnt)
            time.sleep(5)
    while PROCS != []:
        PROCS, work_cnt = collect_job_results(PROCS, work_cnt)
        time.sleep(5)


    log(INFO, "All jobs are finished.")
    log(INFO, "Please check the status.tsv file for the results.")
    
if __name__ == '__main__':
    main()
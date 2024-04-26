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

expriment_ready_to_go = {
    "patron": [
        "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13",
        "14", "15", "16", "17", "18", "19", "20"
    ],
    "patchweave": [
        "1", "2-1", "3", "4", "6", "7", "8", "9-1", "10",
        "12-1", "13", "17", "19", "21", "22", "23", "24"
    ]
    }
level = ""
donor_list = []
jobs_finished = False
current_job = ""

def run_patron(worklist):
    global current_job
    tsv_file = open(os.path.join(config.configuration["OUT_DIR"], "patron_{}.tsv".format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))), 'a')
    writer = csv.writer(tsv_file, delimiter='\t')
    writer.writerow(["PROJECT", "ALARM_ID", "STATUS"])
    tsv_file.flush()
    os.chdir(config.configuration["PATRON_ROOT_PATH"])
    process_cnt = 0
    for cmd in worklist:
        current_job = cmd[2]
        log(INFO, f"Running patron with {cmd}")
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process_cnt += 1
        if process_cnt <= config.configuration["ARGS"].process:
            result.wait()
            process_cnt -= 1
        if result.returncode != 0:
            log(ERROR, f"Failed to run patron with {cmd}")
            log(ERROR, result.stderr.read().decode('utf-8'))
            writer.writerow([cmd[1].split('/')[-1], cmd[2], "X"])
            tsv_file.flush()
        else:
            log(INFO, f"Successfully ran patron with {cmd}")
            writer.writerow([cmd[1].split('/')[-1], cmd[2], "O"])
            tsv_file.flush()
        

def mk_worklist():
    base_cmd = [config.configuration["PATRON_BIN_PATH"]]
    worklist = []
    for donee in config.configuration["DONEE_LIST"]:
        package = donee.split('/')[-1]
        sub_out = os.path.join(config.configuration["OUT_DIR"], package)
        if not os.path.exists(sub_out):
            os.mkdir(sub_out)
        out_opt = ["-o", sub_out]
        worklist.append(base_cmd + ['patch', donee] + out_opt)
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

def manage_patch_status():
    global jobs_finished
    global current_job
    log(INFO, "Status Manager is Running!")
    with open(os.path.join(config.configuration["OUT_DIR"], "status.tsv"), 'a') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(["Donee Name", "Donor Benchmark", "Donor #", "Donee #", "Pattern Type","Correct?", "Diff"])
        f.flush()
        while not jobs_finished:
            if current_job == "":
                time.sleep(10)
                continue
            dir_cache = os.listdir(config.configuration["OUT_DIR"])
            time.sleep(10)
            if dir_cache != os.listdir(config.configuration["OUT_DIR"]):
                new_files = set(os.listdir(config.configuration["OUT_DIR"])) - set(dir_cache)
                for file in new_files:
                    if file.endswith('.patch'):
                        with open(os.path.join(config.configuration["OUT_DIR"], file), 'r') as df:
                            diff = df.read()
                            if diff == "":
                                continue
                            else:
                                file_parsed = file.split('.')[0].split('_')
                                donee_num = file_parsed[1].strip()
                                for infof in os.listdir(config.configuration["OUT_DIR"]):
                                    if infof.endswith('.c') and donee_num in infof:
                                        parsed_info = infof.split('_')[1:]
                                        tmp_list = parsed_info[0].split('-')
                                        benchmark = tmp_list[0].strip()
                                        donor_num = tmp_list[1].strip()
                                        pattern = "ALT" if parsed_info[-1].strip() == "1" else "NORMAL"
                                        writer.writerow([current_job, benchmark, donor_num, donee_num, pattern, "-", diff])
                                        f.flush()
                                        
 
def main():
    global jobs_finished
    global level
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
    status_manager = Thread(target=status_manager, args=())
    status_manager.start()
    run_patron(mk_worklist())
    jobs_finished = True
    status_manager.join()
    log(INFO, "All jobs are finished.")
    log(INFO, "Please check the status.tsv file for the results.")
    
if __name__ == '__main__':
    main()
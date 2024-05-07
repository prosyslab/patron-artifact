#!/usr/bin/env python3
import config
import os
from logger import log, INFO, ERROR, WARNING
import subprocess
import json
import csv
import datetime
import multiprocessing
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
global_stat_out = None
global_stat_cnt = 0
global_line_cnt = 0
global_stat = None
global_writer = None

# def open_global_tsv():
#     global global_stat, global_writer, global_stat_cnt, global_line_cnt
#     if not os.path.exists(global_stat_out):
#         os.mkdir(global_stat_out)
#     global_stat = open(os.path.join(global_stat_out, '{}_combined_stat.tsv'.format(str(global_stat_cnt))), 'a')
#     global_writer = csv.writer(global_stat, delimiter='\t')
#     global_writer.writerow(["Donee Name", "Donor Benchmark", "Donor #", "Donee #", "Pattern Type","Correct?", "Diff"])
#     global_stat.flush()
#     global_stat_cnt += 1
#     global_line_cnt = 0
#     return


def manage_patch_status(path, stat_out, out_dir, current_job, job_cnt, jobs_finished):
    patches = []
    log(INFO, "Status Manager is Running!")
    with open(os.path.join(out_dir, "status.tsv"), 'a') as f:
        with open(os.path.join(stat_out, current_job + '_status.tsv'), 'a') as global_stat:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(["Donee Name", "Donor Benchmark", "Donor #", "Donee #", "Pattern Type","Correct?", "Diff"])
            gwriter = csv.writer(global_stat, delimiter='\t')
            gwriter.writerow(["Donee Name", "Donor Benchmark", "Donor #", "Donee #", "Pattern Type","Correct?", "Diff", path])
            f.flush()
            global_stat.flush()
            while not jobs_finished[job_cnt]:
                new_patches = []
                if not os.path.exists(out_dir):
                    break
                try:
                    for file in os.listdir(out_dir):
                        if file.endswith('.patch') and file not in patches and file not in new_patches:
                            patches.append(file)
                            new_patches.append(file)
                except OSError as e:
                    log(ERROR, f"Failed to read {out_dir}: {e}")
                    time.sleep(10)
                    continue
                if new_patches == []:
                    time.sleep(5)
                    continue
                for file in new_patches:
                    diff = ""
                    while diff == "" and not jobs_finished[job_cnt]:
                        with open(os.path.join(out_dir, file), 'r') as df:
                            diff = df.read()
                            if diff == "" and not jobs_finished[job_cnt]:
                                continue
                            elif diff == "" and jobs_finished[job_cnt]:
                                break
                            else:
                                file_parsed = file.split('.')[0].split('_')
                                donor_num = file_parsed[1].strip()
                                donee_num = file_parsed[2].strip()
                                unique_str = '_' + donor_num + '_' + donee_num + '_'
                                if not os.path.exists(out_dir):
                                    break
                                for infof in os.listdir(out_dir):
                                    if infof.endswith('.c') and unique_str in infof and infof.startswith('patch_'):
                                        parsed_info = infof.split('_')[1:]
                                        tmp_list = parsed_info[0].split('-')
                                        if "patron" in tmp_list[0]:
                                            benchmark = "patron"
                                            donor_num = tmp_list[1].strip()
                                        else:
                                            benchmark = "patchweave"
                                            donor_num = tmp_list[0].strip()
                                        pattern = "ALT" if parsed_info[-1].strip() == "1" else "NORMAL"
                                        writer.writerow([current_job, benchmark, donor_num, donee_num, pattern, "-", diff])
                                        f.flush()
                                        gwriter.writerow([current_job, benchmark, donor_num, donee_num, pattern, "-", diff])
                                        global_stat.flush()
    is_patched = False
    for file in os.listdir(out_dir):
        if file.endswith('.patch'): 
            is_patched = True
            break
    if not is_patched:
        log(INFO, f"No patch is generated for {current_job}")
        log(INFO, f"Removing {out_dir}")
        subprocess.run(['rm', '-rf', out_dir])
        log(INFO, f"Removing {os.path.join(stat_out, current_job + '_status.tsv')}")
        subprocess.run(['rm', os.path.join(stat_out, current_job + '_status.tsv')])
        

def run_patron(stat_out, cmd, path, job_cnt, jobs_finished):
    os.chdir(config.configuration["PATRON_ROOT_PATH"])
    current_job = os.path.basename(cmd[2])
    if not check_donee(cmd[2]):
        log(ERROR, f"{cmd[2]} is not ready.")
        return None, None
    sub_out_dir = cmd[-1]
    if not os.path.exists(sub_out_dir):
        os.mkdir(sub_out_dir)
    with open(os.path.join(sub_out_dir, "donee_path.txt"), 'w') as f:
        f.write(path)
    status_manager = multiprocessing.Process(target=manage_patch_status, args=(cmd[2], stat_out, sub_out_dir, current_job, job_cnt, jobs_finished))
    status_manager.start()
    log(INFO, f"Running patron with {cmd}")
    return status_manager, subprocess.Popen(cmd)




def mk_worklist():
    base_cmd = [config.configuration["PATRON_BIN_PATH"]]
    worklist = []
    cnt = 0
    for donee, path in config.configuration["DONEE_LIST"]:
        package = donee.split('/')[-1]
        sub_out = os.path.join(config.configuration["OUT_DIR"], package)
        db_opt = ["--db", os.path.join(config.configuration["DB_PATH"])]
        if os.path.exists(sub_out):
            sub_out = sub_out + "_" + str(cnt)
        out_opt = ["-o", sub_out]
        worklist.append((base_cmd + ['patch', donee] + db_opt + out_opt, path))
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

def check_donee(donee):
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
    if not os.path.exists(os.path.join(config.configuration["ROOT_PATH"], 'patron-DB')):
        log(ERROR, "patron-DB does not exist.")
        return False
    return True

def construct_database():
    check_sparrow()
    run_sparrow()
    mk_database()

def collect_job_results(PROCS, work_cnt, jobs_finished):
    for j in range(len(PROCS)):
        cmd, work_id, m, proc = PROCS[j]
        if proc.poll() is not None and not jobs_finished[work_id]:
            if proc.returncode != 0:
                log(ERROR, f"Failed to run patron with {cmd}")
                log(ERROR, proc.stderr.read().decode('utf-8'))
            else:
                log(INFO, f"Successfully ran patron with {cmd}")
            jobs_finished[work_id] = True
            log(INFO, f"Waiting for manager to finish the leftover writings.")
            if m.is_alive():
                m.join()
            work_cnt -= 1
            
            break
    return PROCS, work_cnt

def main():
    global level
    # global global_stat_out, global_stat
    level = "PATRON"
    config.setup(level)
    stat_out = os.path.join(config.configuration["OUT_DIR"], 'stat')
    if not os.path.exists(stat_out):
        os.mkdir(stat_out)
    if config.configuration["DATABASE_ONLY"]:
        construct_database()
        return
    if not check_database():
        if not check_sparrow():
            run_sparrow()
        mk_database()
    worklist = mk_worklist()
    work_cnt = 0
    PROCS = []
    # open_global_tsv()
    jobs_finished = multiprocessing.Manager().list(range(len(worklist)))
    try:
        for i in range(len(worklist)):
            jobs_finished[i] = False
            work, path = worklist[i]
            log(INFO, f"Work: {work}")
            manager, p = run_patron(stat_out, work, path, i, jobs_finished)
            if manager is None and p is None:
                continue
            PROCS.append((work, i, manager, p))
            time.sleep(5)
            work_cnt += 1
            if work_cnt >= config.configuration["ARGS"].process:
                log(WARNING, "Waiting for the current jobs to finish...")
            while work_cnt >= config.configuration["ARGS"].process:
                PROCS, work_cnt = collect_job_results(PROCS, work_cnt, jobs_finished)
                time.sleep(5)
        all_finished = False
        while not all_finished:
            PROCS, work_cnt = collect_job_results(PROCS, work_cnt, jobs_finished)
            if False not in jobs_finished:
                all_finished = True
            else:
                time.sleep(5)   
    except Exception as e:
        log(ERROR, f"Exception occurred: {e}")
        log(ERROR, "Terminating all the jobs...")
        for p in PROCS:
            cmd, work_id, m, proc = p
            proc.terminate()
            jobs_finished[work_id] = True
        for p in PROCS:
            cmd, work_id, m, proc = p
            m.terminate()

    # global_stat.close()
    log(INFO, "All jobs are finished.")
    log(INFO, "Please check the status.tsv file for the results.")

if __name__ == '__main__':
    main()

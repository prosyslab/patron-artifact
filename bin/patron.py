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
global_stat = None
global_writer = None
stat_out = ""
def parse_time(line):
    # parse time from [20240611-06:36:10][INFO] Making facts from 14th alarm all in seconds
    time_str = line.split('[')[1].split(']')[0]
    return datetime.datetime.strptime(time_str, '%Y%m%d-%H:%M:%S')
    
    
def write_out_results(path, out_dir, current_job, is_failed):
    patches = []
    log(INFO, "Writing out the results for {}...".format(current_job))
    stat_file_name = os.path.join(stat_out, current_job + '_status_')
    file_cnt = 0
    while os.path.exists(stat_file_name + str(file_cnt) + '.tsv'):
        file_cnt += 1
    with open(stat_file_name + str(file_cnt) + '.tsv', 'a') as local_stat:
        local_writer = csv.writer(local_stat, delimiter='\t')
        local_writer.writerow(["Donee Name", "Donor Benchmark", "Donor #", "Donee #", "Pattern Type", "Time" "Correct?", "Diff"])
        local_stat.flush()
        log_data = ""
        for file in os.listdir(out_dir):
            if file.endswith('.patch'):
                patches.append(file)
            if file == 'log.txt':
                log_data = file
        for patch_file in patches:
            diff = ""
            df = open(os.path.join(out_dir, patch_file), 'r')
            diff = df.read()
            df.close()
            lf = open(os.path.join(out_dir, log_data), 'r')
            log = lf.readlines()
            lf.close()
            without_ext = patch_file.split('.')[0]
            log_target = without_ext.replace('result_', '').replace('_diff', '')
            for i in range(len(log)):
                if log_target in log[i]:
                    idx = i
                    break
            end_time = parse_time(log[idx])
            tokens = log[idx].split(' ')
            for i in range(len(tokens)):
                if 'for' in tokens[i]:
                    num = tokens[i+1]
                    break
            for line in log[:i].reverse():
                if 'Making facts from ' + num in line:
                    start_time = parse_time(line)
                    break
            elapsed = end_time - start_time
            elapsed = str(elapsed.total_seconds())
            file_parsed = without_ext.split('_')
            donor_num = file_parsed[1].strip()
            donee_num = file_parsed[2].strip()
            unique_str = '_' + donor_num + '_' + donee_num + '_'
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
                    if '_' in current_job:
                        current_job = current_job.split('_')[-2]
                    if '-' in current_job:
                        current_job = current_job.split('-')[0] + '-' + current_job.split('-')[1]
                    for line in log_data:
                        if current_job + '\'' in line:
                            break
                    local_writer.writerow([current_job, benchmark, donor_num, donee_num, pattern, elapsed, "-", diff])
                    local_stat.flush()
                    global_writer.writerow([current_job, benchmark, donor_num, donee_num, pattern, elapsed, "-", diff])
                    global_stat.flush()
        if is_failed:
            msg = '----------PATRON STOPPED DUE TO UNEXPECTED ERROR----------'
            local_writer.writerow([current_job, msg, "-", "-", "-", "-", "-", "-"])
            local_stat.flush()
            global_writer.writerow([current_job, msg, "-", "-", "-", "-" ,"-", "-"])
            global_stat.flush()
    is_patched = False
    for file in os.listdir(out_dir):
        if file.endswith('.patch'): 
            is_patched = True
            break
    if not is_patched:
        log(INFO, f"No patch is generated for {current_job}")
        

def run_patron(cmd, path, job_cnt, jobs_finished):
    os.chdir(config.configuration["PATRON_ROOT_PATH"])
    current_job = os.path.basename(cmd[2])
    if not check_donee(cmd[2]):
        log(ERROR, f"{cmd[2]} is not ready.")
        return None
    sub_out_dir = cmd[-1]
    if not os.path.exists(sub_out_dir):
        os.mkdir(sub_out_dir)
    with open(os.path.join(sub_out_dir, "donee_path.txt"), 'w') as f:
        f.write(path)
    log(INFO, f"Running patron with {cmd}")
    return subprocess.Popen(cmd)

def mk_worklist():
    base_cmd = [config.configuration["PATRON_BIN_PATH"]]
    worklist = []
    cnt = 0
    for donee, path in config.configuration["DONEE_LIST"]:
        sp = donee.split('/')
        for i in range(len(sp)):
            if 'analysis_target' in sp[i]:
                package = '-'.join(sp[i:])
                break
        package = donee.split('/')[-1]
        sub_out = os.path.join(config.configuration["OUT_DIR"], package)
        db_opt = ["--db", os.path.join(config.configuration["DB_PATH"])]
        if os.path.exists(sub_out):
            sub_out = sub_out + "_" + str(cnt)
        out_opt = ["-o", sub_out]
        worklist.append((base_cmd + ['patch', donee] + db_opt + out_opt, path))
        cnt += 1
    return worklist

def run_sparrow(patchweave_worklist, patron_worklist, mk_full_db=True):
    log(WARNING, f"Running sparrow to construct databse ...")
    os.chdir(config.configuration["EXP_ROOT_PATH"])
    log(INFO, "Detailed log will be saved in {}".format(os.path.join(config.configuration["EXP_ROOT_PATH"], 'out')))
    log(INFO, "Running sparrow for patchweave benchmarks...")
    # print(patchweave_worklist)
    result_patchweave = subprocess.Popen(['python3', 'bin/run.py', '-sparrow', 'patchweave', '-p', '-id'] + patchweave_worklist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result_patchweave.wait()
    if result_patchweave.returncode != 0:
        log(ERROR, f"Failed to run sparrow for patchweave.")
        log(ERROR, result_patchweave.stderr.read().decode('utf-8'))
        exit(1)
    log(INFO, "Running sparrow for patron benchmarks...")
    result_patron = subprocess.Popen(['python3', 'bin/run.py', '-sparrow', 'patron', '-p', '-id'] + patron_worklist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
    patchweave_missing_list = []
    patron_missing_list = []
    for file in os.listdir(patron_bench_path):
        if file.endswith('.sh'):
            continue
        if file in expriment_ready_to_go["patron"]:
            if not os.path.exists(os.path.join(patron_bench_path, file, 'bug', 'sparrow-out')):
                log(ERROR, f"sparrow-out for {file} does not exist in {patron_bench_path}")
                patron_missing_list.append(str(file))
            donor_list.append(os.path.join(patron_bench_path, file))
    for file in os.listdir(patchweave_bench_path):
        if file in expriment_ready_to_go["patchweave"]:
            if not os.path.exists(os.path.join(patchweave_bench_path, file, 'donor', 'bug', 'sparrow-out')):
                log(ERROR, f"sparrow-out for {file} does not exist in {patchweave_bench_path}")
                patchweave_missing_list.append(str(file))
            donor_list.append(os.path.join(patchweave_bench_path, file, 'donor'))
    return patchweave_missing_list, patron_missing_list

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
    patchweave_works, patron_works = check_sparrow()
    if len(patchweave_works) > 0 or len(patron_works) > 0:
        run_sparrow(patchweave_works, patron_works)
    mk_database()

def collect_job_results(PROCS, work_cnt, jobs_finished):
    for j in range(len(PROCS)):
        cmd, work_id, proc = PROCS[j]
        if proc.poll() is not None and not jobs_finished[work_id]:
            if proc.returncode != 0:
                log(ERROR, f"Failed to run patron with {cmd}")
                is_failed = True
            else:
                log(INFO, f"Successfully ran patron with {cmd}")
                is_failed = False
            jobs_finished[work_id] = True
            work_cnt -= 1
            write_out_results(cmd[2], cmd[-1], os.path.basename(cmd[2]), is_failed)
            break
    return PROCS, work_cnt

def main(from_top=False):
    global level, global_stat, global_writer, stat_out
    if from_top:
        level = "PATRON_PIPE"
    else:
        level = "PATRON"
    config.setup(level)
    stat_out = os.path.join(config.configuration["OUT_DIR"], 'stat')
    if not os.path.exists(stat_out):
        os.mkdir(stat_out)
    if config.configuration["DATABASE_ONLY"]:
        construct_database()
        return
    if not check_database():
        patchweave_works, patron_works = check_sparrow()
        if len(patchweave_works) > 0 or len(patron_works) > 0:
            run_sparrow(patchweave_works, patron_works)
        mk_database()
    worklist = mk_worklist()
    work_cnt = 0
    total_work_cnt = 0
    PROCS = []
    global_stat = open(os.path.join(stat_out, 'status.tsv'), 'a')
    global_writer = csv.writer(global_stat, delimiter='\t')
    global_writer.writerow(["Donee Name", "Donor Benchmark", "Donor #", "Donee #", "Pattern Type","Correct?", "Diff"])
    global_stat.flush()
    jobs_finished = multiprocessing.Manager().list(range(len(worklist)))
    try:
        for i in range(len(worklist)):
            jobs_finished[i] = False
            work, path = worklist[i]
            log(INFO, f"Work: {work}")
            p = run_patron(work, path, i, jobs_finished)
            if p is None:
                continue
            PROCS.append((work, i, p))
            time.sleep(5)
            work_cnt += 1
            total_work_cnt += 1
            if work_cnt >= config.configuration["PROCESS_LIMIT"]:
                log(INFO, "{}".format(len(worklist)-total_work_cnt) + " jobs are left.")
                log(WARNING, "Waiting for the current jobs to finish...")
            while work_cnt >= config.configuration["PROCESS_LIMIT"]:
                log(INFO, "{}".format(len(worklist)-total_work_cnt) + " jobs are left.")
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
        log(ERROR, f"Exception occurred:")
        log(ERROR, e)
        log(ERROR, "Terminating all the jobs...")
        for p in PROCS:
            cmd, work_id, proc = p
            proc.terminate()
            jobs_finished[work_id] = True

    global_stat.close()
    log(INFO, "All jobs are finished.")
    log(INFO, "Please check the status.tsv file for the results.")

if __name__ == '__main__':
    main()

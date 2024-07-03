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
import measure_time
import copy

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

level = "PATRON"
donor_list = []
global_stat = None
global_writer = None
stat_out = ""
time_record = dict()

'''
Function that writes out the combined patch results
The results are written as .tsv file at out/combined_results directory
copy the .tsv files to Google Sheet for easier analysis

Input: str (output directory), str (current job(the donee file name)), bool (is failed)
Output: None
'''
def write_out_results(out_dir:str, current_job:str, is_failed:bool, time:str) -> None:
    time_tsv_path = os.path.join(config.configuration["OUT_DIR"], 'time.tsv')
    with open(time_tsv_path, 'a') as time_tsv:
        time_writer = csv.writer(time_tsv, delimiter='\t')
        time_writer.writerow([current_job, time])
        time_tsv.flush()
    patches = []
    log(INFO, "Writing out the results for {}...".format(current_job))
    stat_file_name = os.path.join(stat_out, current_job + '_status_')
    file_cnt = 0
    while os.path.exists(stat_file_name + str(file_cnt) + '.tsv'):
        file_cnt += 1
    with open(stat_file_name + str(file_cnt) + '.tsv', 'a') as local_stat:
        local_writer = csv.writer(local_stat, delimiter='\t')
        local_writer.writerow(["Donee Name", "Donor Benchmark", "Donor #", "Donee #", "Pattern Type","Correct?", "Diff"])
        local_stat.flush()
        for file in os.listdir(out_dir):
            if file.endswith('.patch'):
                patches.append(file)
        for patch_file in patches:
            diff = ""
            df = open(os.path.join(out_dir, patch_file), 'r')
            diff = df.read()
            df.close()
            file_parsed = patch_file.split('.')[0].split('_')
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
                    local_writer.writerow([current_job, benchmark, donor_num, donee_num, pattern, "-", diff])
                    local_stat.flush()
                    global_writer.writerow([current_job, benchmark, donor_num, donee_num, pattern, "-", diff])
                    global_stat.flush()
        if is_failed:
            msg = '----------PATRON STOPPED DUE TO UNEXPECTED ERROR----------'
            local_writer.writerow([current_job, msg, "-", "-", "-", "-", "-"])
            local_stat.flush()
            global_writer.writerow([current_job, msg, "-", "-", "-", "-" ,"-"])
            global_stat.flush()
    is_patched = False
    for file in os.listdir(out_dir):
        if file.endswith('.patch'): 
            is_patched = True
            break
    if not is_patched:
        log(INFO, f"No patch is generated for {current_job}")
    # measure_time.run_from_top(config.configuration["OUT_DIR"], measure_time.PATCH_MODE)
        
'''
Function that runs Patron backend engine

Input: list (command), str (path for output path)
Output: subprocess.Popen
'''
def run_patron(cmd:list, path:str) -> subprocess.Popen:
    global time_record
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
    # get current time
    time_record[cmd] = time.time()
    return subprocess.Popen(cmd)

'''
Function that generates cmds

Input: bool (from_top), str (package) -> if from_top is False, package can be ignored
Output: list (command)
'''
def mk_worklist(from_top:bool, package:str) -> list:
    base_cmd = [config.configuration["PATRON_BIN_PATH"]]
    worklist = []
    cnt = 0
    if package == []:
        target_donee = config.configuration["DONEE_LIST"]
    else:
        target_donee = config.get_patron_target_files(package)
    for donee, path in target_donee:
        package = donee.split('/')[-1]
        sub_out = os.path.join(config.configuration["OUT_DIR"], package)
        db_opt = ["--db", os.path.join(config.configuration["DB_PATH"])]
        if os.path.exists(sub_out):
            sub_out = sub_out + "_" + str(cnt)
        out_opt = ["-o", sub_out]
        worklist.append((base_cmd + ['patch', donee] + db_opt + out_opt, path))
        cnt += 1
    return worklist

'''
Function that runs Sparrow to get the analysis results, which is pre-requisite for DB construction
This function is fitted to make DB out of RQ1, RQ2 benchmark dataset

Input: list (patchweave_worklist), list (patron_worklist), bool (mk_full_db)
Output: None (It handles the process itself)
'''
def run_sparrow_defualt(patchweave_worklist:list, patron_worklist:list, mk_full_db:bool=True):
    log(WARNING, f"Running sparrow to construct databse ...")
    os.chdir(config.configuration["EXP_ROOT_PATH"])
    log(INFO, "Detailed log will be saved in {}".format(os.path.join(config.configuration["EXP_ROOT_PATH"], 'out')))
    log(INFO, "Running sparrow for patchweave benchmarks...")
    result_patchweave = subprocess.Popen(['python3', 'bin/run.py', '-sparrow', 'patchweave', '-p', '-id'] + patchweave_worklist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result_patchweave.wait()
    if result_patchweave.returncode != 0:
        log(ERROR, f"Failed to run sparrow for patchweave.")
        log(ERROR, result_patchweave.stderr.read().decode('utf-8'))
        config.patron_exit("PATRON")
    log(INFO, "Running sparrow for patron benchmarks...")
    result_patron = subprocess.Popen(['python3', 'bin/run.py', '-sparrow', 'patron', '-p', '-id'] + patron_worklist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result_patron.wait()
    if result_patron.returncode != 0:
        log(ERROR, f"Failed to run sparrow for patron.")
        log(ERROR, result_patron.stderr.read().decode('utf-8'))
        config.patron_exit("PATRON")

'''
Function that creates Sparrow CMD for custom DB construction

Input: str (label_path), str (curr_path)
Output: list (str)(command)
'''
def mk_sparrow_cmd(label_path:str, curr_path:str) -> list:
    with open(label_path, 'r') as f:
        data = json.load(f)
    bug_type = data["TYPE"].lower()
    bug_flag = [ "-" + bug_type ]
    loc_flag = [ "-target_loc", data["TRUE-ALARM"]['ALARM-LOC'][0] ]
    default_flags = ["-taint", "-unwrap_alloc", "-remove_cast", "-patron", "-extract_datalog_fact_full"]
    if bug_type != "bo":
        default_flags.append("-no_bo")
    target = ""
    for file in os.listdir(curr_path):
        if file.endswith('.c') and 'cil_' in file:
            target = file
            break
    if target == "":
        log(ERROR, f"Target file not found in {curr_path}")
        return []
    cmd = [config.configuration["SPARROW_BIN_PATH"], target] + default_flags + bug_flag + loc_flag
    return cmd

'''
Function that runs Sparrow to get the analysis results, which is pre-requisite for DB construction
This function is for custom DB construction
Donor programs must be under the specific directory structrue
For example, if donor programs are under /path/to/donor, the directory structure must be like:
/path/to/donor
        |-- 1
        |   |- bug
        |   |   `- program.c
        |   `- patch
        |       `- program.c
        |-- 2
        |   |- bug
        |   ...
        ...
        `-- ...
        
Input: list (paths of programs that are not analyzed by Sparrow)
Output: None (It handles the process itself)
'''
def run_sparrow(missing_list:list) -> None:
    log(WARNING, f"Running sparrow to construct databse ...")
    work_list = []
    proc_list = []
    rest = []
    run_cnt = 0
    for path in missing_list:
        if os.path.exists(os.path.join(os.path.dirname(file), 'sparrow-out')):
            os.system(f'rm -rf {os.path.join(os.path.dirname(file), "sparrow-out")}')
        cmd = mk_sparrow_cmd(os.path.join(path, '..', 'label.json'), path)
        work_list.append(cmd)
    rest = copy.deepcopy(work_list)
    i = 0
    while run_cnt < config.configuration["PROCESS_LIMIT"] and len(rest) > 0:
        log(INFO, f"Running sparrow for {work_list[i]} ...")
        os.chdir(os.path.dirname(work_list[i][1]))
        sparrow_log = open('sparrow_log', 'w')
        proc = subprocess.Popen(work_list[i], stdout=sparrow_log, stderr=subprocess.STDOUT)
        proc_list.append((work_list[i], proc, sparrow_log))
        rest.remove(work_list[i])
        run_cnt += 1
        i += 1
        if run_cnt >= config.configuration["PROCESS_LIMIT"] or i >= len(work_list):
            for cmd, proc, sparrow_log in proc_list:
                try:
                    stdout, stderr = proc.communicate(timeout=900)
                except subprocess.TimeoutExpired:
                    log(ERROR, f"Timeout for {cmd}")
                    proc.terminate()
                    sparrow_log.close()
                    run_cnt -= 1
                sparrow_log.close()
                if proc.returncode != 0:
                    log(ERROR, f"Failed to run sparrow for {cmd}")
                else:
                    log(INFO, f"Successfully ran sparrow for {cmd}")
                run_cnt -= 1
                i -= 1
                proc_list.remove((cmd, proc, sparrow_log))
                work_list.remove(cmd)
    log(INFO, "Successfully finished running sparrow.")
        
'''
This function inistially made to check to ensure that the donee file is analyzed by Sparrow before Patron
However, maybe useless because this is already done by previous steps

Input: str (donee)
Output: bool (True: donee is ready, False: donee is not ready)
'''
def check_donee(donee) -> bool:
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

'''
Function that check the analysis results, which is pre-requisite for DB construction
This function is for our benchmark dataset
Since, patchweave dataset and patron dataset have different directory structure, this function is needed
        
Input: None
Output: list (patchweave_missing_list), list (patron_missing_list)
'''
def check_sparrow_default() -> list:
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
                log(WARNING, f"sparrow-out for {file} does not exist in {patron_bench_path}")
                patron_missing_list.append(str(file))
            donor_list.append(os.path.join(patron_bench_path, file))
    for file in os.listdir(patchweave_bench_path):
        if file in expriment_ready_to_go["patchweave"]:
            if not os.path.exists(os.path.join(patchweave_bench_path, file, 'donor', 'bug', 'sparrow-out')):
                log(WARNING, f"sparrow-out for {file} does not exist in {patchweave_bench_path}")
                patchweave_missing_list.append(str(file))
            donor_list.append(os.path.join(patchweave_bench_path, file, 'donor'))
    return patchweave_missing_list, patron_missing_list

'''
Function that check the analysis results, which is pre-requisite for DB construction
This function is for custom DB construction and for custom Donor programs
Please make sure to have donor program structure as the description in run_sparrow function
or README.md
        
Input: None
Output: list (missing_list)
'''
def check_sparrow() -> list:
    global donor_list
    missing_list = []
    donors = [ os.path.join(config.configuration["DONOR_PATH"], f) for f in os.listdir(config.configuration["DONOR_PATH"]) ]
    for donor in donors:
        target = os.path.join(donor, 'bug')
        if not os.path.exists(os.path.join(target, 'sparrow-out')):
            log(WARNING, f"sparrow-out for {donor} does not exist.")
            missing_list.append(target)
        donor_list.append(donor)
    return missing_list

'''
Function that makes database from scratch

Input: None (Path details are stored in config.py)
Output: None
'''
def mk_database():
    tsv_file = open(os.path.join(config.configuration["OUT_DIR"], "database_{}.tsv".format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))), 'a')
    writer = csv.writer(tsv_file, delimiter='\t')
    writer.writerow(["BENCHMARK", "ID", "STATUS"])
    tsv_file.flush()
    log(WARNING, "Creating {} from scratch...".format(config.configuration["DB_PATH"]))
    os.chdir(config.configuration["PATRON_ROOT_PATH"])
    db_name = os.path.basename(config.configuration["DB_PATH"])
    if os.path.exists(os.path.join(config.configuration["PATRON_ROOT_PATH"], db_name)):
        subprocess.run(['rm', '-rf', db_name])
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
            log(ERROR, f"Failed to create DB for {donor}")
            log(ERROR, result.stderr.read().decode('utf-8'))
            writer.writerow([donor.split('/')[-2], donor.split('/')[-1], "X"])
            tsv_file.flush()
        else:
            log(INFO, f"Successfully created DB for {donor}")
            writer.writerow([donor.split('/')[-2], donor.split('/')[-1], "O"])
    log(INFO, "Successfully finished making DB.")
    log(INFO, "Copying the database to the root directory as {}...".format(os.path.basename(config.configuration["DB_PATH"])))
    os.system('cp -r {} {}'.format(os.path.join(config.configuration["PATRON_ROOT_PATH"], os.path.basename(config.configuration["DB_PATH"])), os.path.join(config.configuration["ROOT_PATH"], os.path.basename(config.configuration["DB_PATH"]))))
    tsv_file.close()

'''
Function that checks if the target database exists

Input: None
Output: bool (True: database exists, False: database does not exist)
'''
def check_database() -> bool:
    if not os.path.exists(os.path.join(config.configuration["DB_PATH"])):
        log(ERROR, "{} does not exist.".format(config.configuration["DB_PATH"]))
        return False
    return True

'''
High level function that makes database from scratch

Input: None (Path details are stored in config.py)
Output: None
'''
def construct_database() -> None:
    log(INFO, 'Checking If all donors in {} are analyzed by Sparrow...'.format(config.configuration["DONOR_PATH"]))
    if config.configuration["DONOR_PATH"] == "benchmark":
        patchweave_works, patron_works = check_sparrow_default()
        if len(patchweave_works) > 0 or len(patron_works) > 0:
            run_sparrow_defualt(patchweave_works, patron_works)
    else:
        works = check_sparrow()
        if len(works) > 0:
            run_sparrow(works)
    mk_database()

'''
This function collects the patch results from each job directory everytime each process finishes

Input: list (PROCS)[command, process_id, Popen], int (work_cnt), list (boolean list to track which process is finished)
Output: list (PROCS), int (work_cnt) -> updated
'''
def collect_job_results(PROCS, work_cnt, jobs_finished):
    global time_record
    for j in range(len(PROCS)):
        cmd, work_id, proc = PROCS[j]
        if proc.poll() is not None and not jobs_finished[work_id]:
            if proc.returncode != 0:
                log(ERROR, f"Failed to run patron with {cmd}")
                is_failed = True
            else:
                log(INFO, f"Successfully ran patron with {cmd}")
                is_failed = False
                end_time = time.time()
                start_time = time_record[cmd]
                elapsed_time = end_time - start_time
                time_in_str_insec = str(datetime.timedelta(seconds=elapsed_time))
            jobs_finished[work_id] = True
            work_cnt -= 1
            write_out_results(cmd[-1], os.path.basename(cmd[2]), is_failed, time_in_str_insec)
            break
    return PROCS, work_cnt

'''
patron.py has two different procedures
1) Constructing database from scratch
2) Running Patron with the constructed database
It can be run from four different sources
1) oss_exp.py -patron <analysis_target_dir>
2) oss_exp.py -fullpipe
2) run.py -oss
3) patron.py -db /path/to/db -d /path/to/donee -p <number_of_processes>

Input: Optional (bool) -> to check where this program is run from, 
Optional (str) -> to specify the package name if run pipe
Output: None
'''
def main(from_top:bool=False, package:list=[]) -> None:
    global level, global_stat, global_writer, stat_out
    if not from_top:
        config.setup(level)
    stat_out = os.path.join(config.configuration["OUT_DIR"], 'results_combined')
    if not os.path.exists(stat_out):
        os.mkdir(stat_out)
    if config.configuration["DATABASE_ONLY"]:
        log(INFO, 'Entering Database-Only mode...')
        construct_database()
        return
    if not check_database():
        patchweave_works, patron_works = check_sparrow()
        if len(patchweave_works) > 0 or len(patron_works) > 0:
            run_sparrow(patchweave_works, patron_works)
        mk_database()
    worklist = mk_worklist(from_top, package)
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
            p = run_patron(work, path)
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
    print('YOU ARE RUNNING PATRON.PY AS A SCRIPT DIRECTLY.')
    main()

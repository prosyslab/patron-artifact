#!/usr/bin/env python3
import config
import os
from logger import log, INFO, ERROR, WARNING, ALL
import subprocess
import json
import csv
import datetime
import multiprocessing
from time import sleep
import time
import copy
import threading
from queue import Queue
import progressbar

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
work_stack = Queue()
patch_work_size = None
patch_work_cnt = 0
patch_bar = None

'''
Function that writes out the combined patch results
This function mostly contains patch parsing logic.
The results are written as .tsv file at out/combined_results directory
copy the .tsv files to Google Sheet for easier analysis

Input: str (output directory), str (current job(the donee file name)), bool (is failed)
Output: None
'''
def write_out_results(out_dir:str, current_job_path:str, is_failed:bool, time:str) -> None:
    current_job = os.path.basename(current_job_path)
    package = "-"
    path_split = current_job_path.split('/')
    for i in range(len(path_split)-1, -1, -1):
        if path_split[i].startswith('_'):
            package = path_split[i][1:]
            break
    alarm_num = len(os.listdir(os.path.join(current_job_path, 'sparrow-out', 'taint', 'datalog'))) - 1
    time_tsv_path = os.path.join(config.configuration["OUT_DIR"], 'time.tsv')
    try:
        with open(time_tsv_path, 'a') as time_tsv:
            time_writer = csv.writer(time_tsv, delimiter='\t')
            if alarm_num == 0 or alarm_num == -1 or time == "Failed":
                time_writer.writerow([package, current_job, time, alarm_num, "-"])
            else:
                if 'day' in str(time):
                    day_in_sec = float(time.split(' ')[0]) * 86400
                    rest_time = time.split(' ')[-1]
                    time_in_sec = float(rest_time.split(':')[0]) * 3600 + float(rest_time.split(':')[1]) * 60 + float(rest_time.split(':')[2]) + day_in_sec
                else:
                    time_in_sec = float(time.split(':')[0]) * 3600 + float(time.split(':')[1]) * 60 + float(time.split(':')[2])
                time_writer.writerow([package, current_job, time, alarm_num, str(float(time_in_sec)/alarm_num)])
                time_tsv.flush()
    except Exception as e:
        log(ERROR, f"Failed to write out time.tsv: {e}")
    patches = []
    log(INFO, "Writing out the results for {}...".format(current_job))
    stat_file_name = os.path.join(stat_out, current_job + '_status_')
    file_cnt = 0
    while os.path.exists(stat_file_name + str(file_cnt) + '.tsv'):
        file_cnt += 1
    with open(stat_file_name + str(file_cnt) + '.tsv', 'a') as local_stat:
        local_writer = csv.writer(local_stat, delimiter='\t')
        local_writer.writerow(["Package", "Donee Name", "Donor Benchmark", "Donor #", "Donee #", "Pattern Type","Correct?", "Diff"])
        local_stat.flush()
        for file in os.listdir(out_dir):
            if file.endswith('.patch'):
                patches.append(file)
        for patch_file in patches:
            diff = ""
            df = open(os.path.join(out_dir, patch_file), 'r')
            diff = df.read()
            df.close()
            file_wo_ext = patch_file.split('_diff.')[0]
            for i in range(len(file_wo_ext)-1, -1, -1):
                if file_wo_ext[i] == '_':
                    donee_num = file_wo_ext[i+1:]
                    donee_begin_idx = i
                    break
            donor_num = file_wo_ext[7:donee_begin_idx]
            unique_str = '_' + donor_num + '_' + donee_num + '_'
            for infof in os.listdir(out_dir):
                if infof.endswith('.c') and unique_str in infof and infof.startswith('patch_'):
                    parsed_info = infof.split('_')[1:]
                    if "patron" in infof:
                        benchmark = "patron"
                    elif "-donor" in infof:
                        benchmark = "patchweave"
                    elif "OSS" in infof:
                        benchmark = "OSS"
                    else:
                        benchmark = "Custom"
                    pattern = "ALT" if parsed_info[-1].strip() == "1" else "NORMAL"
                    local_writer.writerow([package, current_job, benchmark, donor_num, donee_num, pattern, "-", diff])
                    local_stat.flush()
                    global_writer.writerow([package, current_job, benchmark, donor_num, donee_num, pattern, "-", diff])
                    global_stat.flush()
        if is_failed:
            msg = '----------PATRON STOPPED DUE TO UNEXPECTED ERROR----------'
            local_writer.writerow([package, current_job, msg, "-", "-", "-", "-", "-"])
            local_stat.flush()
            global_writer.writerow([package, current_job, msg, "-", "-", "-", "-" ,"-"])
            global_stat.flush()
    is_patched = False
    for file in os.listdir(out_dir):
        if file.endswith('.patch'): 
            is_patched = True
            break
    if not is_patched:
        log(INFO, f"No patch is generated for {current_job}")
        
'''
Function that runs Patron backend engine

Input: list (command), str (path for output path)
Output: subprocess.Popen
'''
def run_patron(cmd:list, path:str) -> subprocess.Popen:
    global time_record, patch_work_cnt, patch_bar
    if not config.configuration["VERBOSE"]:
        patch_work_cnt += 1
        patch_bar.update(patch_work_cnt)
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
    time_record[' '.join(cmd)] = time.time()
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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
    log(ALL, "Running sparrow for patchweave benchmarks...")
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
        if file.endswith('.c'):
            target = os.path.join(curr_path, file)
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
        if os.path.exists(os.path.join(os.path.dirname(path), 'sparrow-out')):
            os.system(f'rm -rf {os.path.join(os.path.dirname(path), "sparrow-out")}')
        cmd = mk_sparrow_cmd(os.path.join(path, '..', 'label.json'), path)
        work_list.append(cmd)
    rest = copy.deepcopy(work_list)
    i = 0
    work_size = len(work_list)
    work_cnt = 0
    bar = progressbar.ProgressBar(widgets=[' [', 'Running Analysis for DB...', progressbar.Percentage(), '] ', progressbar.Bar(), ' (', progressbar.ETA(), ') ',], maxval=work_size).start()
    while run_cnt < config.configuration["PROCESS_LIMIT"] and len(rest) > 0:
        if 0 == len(work_list[i]):
            continue
        log(INFO, f"Running sparrow for {work_list[i]} ...")
        work_cnt += 1
        if config.configuration["VERBOSE"]:
                log(INFO, "Working on {}/{} ...".format(work_cnt, work_size))
        else:
            bar.update(work_cnt)
        path = os.path.dirname(work_list[i][1])
        os.chdir(path)
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
                # label = os.path.join(os.path.dirname(os.path.dirname(path)), "label.json")
                # with open(label, 'r') as f:
                #     data = json.load(f)
                #     try:
                #         true_alarm = data["TRUE-ALARM"]["ALARM-DIR"][0]
                #     except IndexError:
                #         log(ERROR, f"Failed to get true alarm for {path}")
                #         return
                # for dirs in os.path.join(os.path.dirname(path), "sparrow-out", "taint", "datalog"):
                #     if dirs != true_alarm and dirs != "Alarm.map":
                #         os.system(f'rm -rf {os.path.join(os.path.dirname(path), "sparrow-out", "taint", "datalog", dirs)}')
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
            if config.configuration["OVERWRITE_SPARROW"]:
                if os.path.exists(os.path.join(patron_bench_path, file, 'sparrow-out')):
                    os.system(f'rm -rf {os.path.join(patron_bench_path, file, "sparrow-out")}')
                patron_missing_list.append(str(file))
            elif not os.path.exists(os.path.join(patron_bench_path, file, 'bug', 'sparrow-out')):
                log(WARNING, f"sparrow-out for {file} does not exist in {patron_bench_path}")
                patron_missing_list.append(str(file))
            donor_list.append(os.path.join(patron_bench_path, file))
    for file in os.listdir(patchweave_bench_path):
        if file in expriment_ready_to_go["patchweave"]:
            if config.configuration["OVERWRITE_SPARROW"]:
                if os.path.exists(os.path.join(patchweave_bench_path, file, 'sparrow-out')):
                    os.system(f'rm -rf {os.path.join(patchweave_bench_path, file, "sparrow-out")}')
                patchweave_missing_list.append(str(file))
            elif not os.path.exists(os.path.join(patchweave_bench_path, file, 'donor', 'bug', 'sparrow-out')):
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
        if not os.path.isdir(donor):
            continue
        target = os.path.join(donor, 'bug')
        if config.configuration["OVERWRITE_SPARROW"]:
            if os.path.exists(os.path.join(target, 'sparrow-out')):
                os.system(f'rm -rf {os.path.join(target, "sparrow-out")}')
            missing_list.append(target)
        elif not os.path.exists(os.path.join(target, 'sparrow-out')):
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
    if os.path.exists(os.path.join(config.configuration["PATRON_ROOT_PATH"], 'patron-DB')):
        log(WARNING, "Removing existing patron-DB...")
        subprocess.run(['rm', '-rf', 'patron-DB'])
    cmd = [config.configuration["PATRON_BIN_PATH"], "db"]
    work_size = len(donor_list)
    work_cnt = 0
    bar = progressbar.ProgressBar(widgets=[' [', 'Constructing DB...', progressbar.Percentage(), '] ', progressbar.Bar(), ' (', progressbar.ETA(), ') ',], maxval=work_size).start()
    for donor in donor_list:
        log(INFO, f"Creating patron-DB for {donor} ...")
        work_cnt += 1
        if config.configuration["VERBOSE"]:
                log(INFO, "Working on {}/{} ...".format(work_cnt, work_size))
        else:
            bar.update(work_cnt)
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
            try:
                with open(label, 'r') as f:
                    data = json.load(f)
                    try:
                        true_alarm = data["TRUE-ALARM"]["ALARM-DIR"][0]
                    except IndexError:
                        log(ERROR, f"Failed to get true alarm for {donor}")
                        continue
            except FileNotFoundError:
                alarm_dir = os.path.join(donor, 'bug', 'sparrow-out', 'taint', 'datalog')
                ls = os.listdir(alarm_dir)
                if len(ls) != 2:
                    log(ERROR, f"Failed to get true alarm for {donor}")
                    continue
                for f in ls:
                    if f != 'Alarm.map':
                        true_alarm = f
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
    db_dest = os.path.join(config.configuration["ROOT_PATH"], os.path.basename(config.configuration["DONOR_PATH"]) + "-DB")
    dest_cnt = 1
    while os.path.exists(db_dest):
        db_dest = os.path.join(config.configuration["ROOT_PATH"], os.path.basename(config.configuration["DONOR_PATH"]) + "-DB" + str(dest_cnt))
        dest_cnt += 1
    log(INFO, "Copying the database to the root directory as {}...".format(db_dest))
    db_src = os.path.join(config.configuration["PATRON_ROOT_PATH"], 'patron-DB')
    os.system('cp -r {} {}'.format(db_src, db_dest))
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
    if config.configuration["OVERWRITE_SPARROW"]:
        log(WARNING, 'Overwriting the existing Sparrow results...')
    else:
        log(INFO, 'Checking If all donors in {} are analyzed by Sparrow...'.format(config.configuration["DONOR_PATH"]))
    if "benchmark" in config.configuration["DONOR_PATH"]:
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
def collect_job_results(work, tries):
    global time_record
    cmd, proc = work
    if proc.poll() is not None:
        if proc.returncode != 0:
            log(ERROR, f"Failed to run patron with {cmd}")
            is_failed = True
            time_in_str_insec = "Failed"
        else:
            log(INFO, f"Successfully ran patron with {cmd}")
            is_failed = False
            end_time = time.time()
            start_time = time_record[' '.join(cmd)]
            elapsed_time = end_time - start_time
            time_in_str_insec = str(datetime.timedelta(seconds=elapsed_time))
        write_out_results(cmd[-1], cmd[2], is_failed, time_in_str_insec)
    else:
        log(ERROR, f"Process {cmd} is still running...")
        if tries > 5:
            log(ERROR, f"Process {cmd} is still running after 5 tries. Terminating...")
            proc.terminate()
        tries += 1
        log(ERROR, f"Try recollecting the results...{tries}tries")
        time.sleep(5)
        collect_job_results(work, tries)
'''
Thread worker.
This function is run parallelly to run Patron processes until the work_stack is empty

Input: None
Output: None
'''
def work_manager() -> None:
    global work_stack, patch_work_cnt, patch_patch_bar
    while not work_stack.empty():
        work = work_stack.get()
        log(INFO, f"{work_stack.qsize()} jobs are left.")
        cmd, path = work
        try:
            p = run_patron(cmd, path)
            if p is None:
                continue
            p.communicate(timeout=(3600*3))
        except subprocess.TimeoutExpired:
            log(ERROR, f"Timeout! 3 hours passed for {cmd}")
            if not p is None and p.poll() is None:
                p.terminate()
        except Exception as e:
            log(ERROR, f"Failed to run patron with {cmd}: {e}")
            if not p is None and p.poll() is None:
                p.terminate()
        proc = (cmd, p)
        collect_job_results(proc, 0)


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
    global level, global_stat, global_writer, stat_out, work_stack
    if not from_top:
        try:
            config.setup(level)
        except Exception as e:
            print('Invalid argument given')
            config.patron_usage()
            exit(1)
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
    global_writer.writerow(["Package", "Donee Name", "Donor Benchmark", "Donor #", "Donee #", "Pattern Type","Correct?", "Diff"])
    global_stat.flush()
    jobs_finished = multiprocessing.Manager().list(range(len(worklist)))
    time_tsv_path = os.path.join(config.configuration["OUT_DIR"], 'time.tsv')
    with open(time_tsv_path, 'a') as time_tsv:
        time_writer = csv.writer(time_tsv, delimiter='\t')
        time_writer.writerow(['Package', 'Binary' 'Total Time', '# Alarm', "Avg. Time per Alarm"])
        time_tsv.flush()
    for work in worklist:
        work_stack.put(work)
    managers = []
    global patch_work_size, patch_bar
    patch_work_size = work_stack.qsize()
    patch_bar = progressbar.ProgressBar(widgets=[' [', 'Patron Running...', progressbar.Percentage(), '] ', progressbar.Bar(), ' (', progressbar.ETA(), ') ',], maxval=patch_work_size).start()
    try:
        for i in range(config.configuration["PROCESS_LIMIT"]):
            manager = threading.Thread(target=work_manager, args=())
            manager.start()
            managers.append(manager)
        for manager in managers:
            manager.join()
    except KeyboardInterrupt:
        log(ERROR, "Keyboard Interrupted")
        log(ERROR, "Terminating all the jobs...")
        for manager in managers:
            manager.terminate()
        exit(1)

    global_stat.close()
    log(INFO, "All jobs are finished.")
    log(INFO, "Please check the status.tsv file for the results.")

if __name__ == '__main__':
    config.openings()
    print('YOU ARE RUNNING PATRON.PY AS A SCRIPT DIRECTLY.')
    try:
        main()
        config.happy_ending(config.configuration["OUT_DIR"])
    except KeyboardInterrupt:
        print('Keyboard Interrupted')
        exit(1)

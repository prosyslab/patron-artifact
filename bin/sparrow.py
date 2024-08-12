#!/usr/bin/env python3
import sys
import os
import csv
import config
import datetime
import subprocess
from logger import log, INFO, ERROR, WARNING
from typing import TextIO
import copy
import time
SPARROW_LOG_DIR = os.path.join(config.configuration['OUT_DIR'], 'sparrow_logs')
IS_SOLO_SPARROW = False

'''
Function that actually runs Sparrow
default options are set in config.py

Input: str (package name)
Output: tuple (TextIO, subprocess.Popen)
'''
def run_sparrow(file: str) -> tuple[TextIO, subprocess.Popen]:
    os.chdir(os.path.dirname(file))
    sparrow_log = open('sparrow_log', 'w')
    if os.path.exists(os.path.join(os.path.dirname(file), 'sparrow-out')):
        os.system(f'rm -rf {os.path.join(os.path.dirname(file), "sparrow-out")}')
    if IS_SOLO_SPARROW or config.configuration["USER_SPARROW_OPT"] == []:
        cmd = [config.configuration["SPARROW_BIN_PATH"], file] + config.configuration["DEFAULT_SPARROW_OPT"] + config.configuration["ADDITIONAL_SPARROW_OPT"]
    else:
        cmd = [config.configuration["SPARROW_BIN_PATH"], file] + config.configuration["USER_SPARROW_OPT"] + config.configuration["ADDITIONAL_SPARROW_OPT"]
    log(INFO, f"Running sparrow with {cmd}")
    return sparrow_log, subprocess.Popen(cmd,
                                 stdout=sparrow_log,
                                 stderr=subprocess.STDOUT)

'''
Function that controls the Sparrow process (log, timeout, etc.)

Input: str (package name), list (list of file paths)
Output: bool (True: success, False: fail)
'''
def sparrow(package:str, files:list) -> bool:
    start_time = time.time()
    time_record = dict()
    SPARROW_PKG_DIR = os.path.join(SPARROW_LOG_DIR, package)
    if not os.path.exists(SPARROW_LOG_DIR):
        os.mkdir(SPARROW_LOG_DIR)
    if not os.path.exists(SPARROW_PKG_DIR):
        os.mkdir(SPARROW_PKG_DIR)
    tsvfile = open(os.path.join(SPARROW_LOG_DIR, '{}_sparrow_stat.tsv'.format(package)), 'a')
    writer = csv.writer(tsvfile, delimiter='\t')
    writer.writerow(['Package', 'Status'])
    tsvfile.flush()
    success_cnt = 0
    proc_cnt = 0
    procs = []
    rest_files = copy.deepcopy(files)
    i = 0
    while len(rest_files) > 0 and proc_cnt < config.configuration["PROCESS_LIMIT"]:
        log(INFO, f"Running sparrow for {files[i]} ...")
        time_record[files[i]] = dict()
        time_record[files[i]]['start'] = time.time()
        sparrow_log, process = run_sparrow(files[i])
        proc_cnt += 1
        procs.append((files[i], process, sparrow_log))
        rest_files.remove(files[i])
        i += 1
        if proc_cnt > config.configuration["PROCESS_LIMIT"] or i >= len(files):
            for file, process, sparrow_log in procs:
                try:
                    stdout, stderr = process.communicate(timeout=3600)
                except subprocess.TimeoutExpired:
                    log(ERROR, f"Timeout for {file}.")
                    time_record[file]['end'] = 0
                    import signal
                    os.killpg(process.pid, signal.SIGTERM)
                    writer.writerow([file, 'X'])
                    tsvfile.flush()
                    sparrow_log.close()
                    proc_cnt -= 1
                    continue
                sparrow_log.close()
                if process.returncode == 0:
                    log(INFO, f"{file} is successfully analyzed.")
                    time_record[file]['end'] = time.time()
                    writer.writerow([file, 'O'])
                    success_cnt += 1
                else:
                    log(ERROR, f"Failed to analyze {file}.")
                    time_record[file]['end'] = 0
                    log(ERROR, f"Check {os.path.join(os.path.dirname(file), 'sparrow_log')} for more information.")
                    writer.writerow([file, 'X'])
                tsvfile.flush()
                proc_cnt -= 1
                i -= 1
                procs.remove((file, process, sparrow_log))
                files.remove(file)
        tsvfile.flush()
    tsvfile.close()
    if success_cnt == 0:
        log(ERROR, f"No file is successfully analyzed.")
        return False
    time_lst = []
    with open(os.path.join(SPARROW_PKG_DIR, f'{package}_time_summary.txt'), 'w') as f:
        for file in time_record:
            # check if 'end' key exists
            if 'end' not in time_record[file] or time_record[file]['end'] == 0:
                f.write(f"{file}: Timeout or Error\n")
            else:
                time_lst.append(time_record[file]['end'] - time_record[file]['start'])
                f.write(f"{file}: {time_record[file]['end'] - time_record[file]['start']}\n")
        if len(time_lst) != 0:
            f.write(f"Average: {sum(time_lst)/len(time_lst)}\n")
        f.write(f"Total time: {time.time() - start_time}\n")
    log(INFO, f"{success_cnt} files are successfully analyzed.")
    return True

'''
Function called from -pipe option of bin/oss_exp.py

Input: str (package name), TextIO (tsvfile), csv.writer
Output: bool (True: success, False: fail)
'''
def sparrow_pipe(package:str, tsvfile:TextIO, writer:csv.writer) -> bool:
    global SPARROW_LOG_DIR
    SPARROW_LOG_DIR = os.path.join(config.configuration['OUT_DIR'], 'sparrow_logs')
    if not os.path.exists(SPARROW_LOG_DIR):
        os.mkdir(SPARROW_LOG_DIR)
    target_dir = os.path.join(config.configuration["ANALYSIS_DIR"], package)
    if not os.path.exists(target_dir):
        log(ERROR, f"{target_dir} does not exist.")
        writer.writerow([package, 'O', 'O', 'X', '-', "dir not found"])
        tsvfile.flush()
        return False
    c_files = []
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.c'):
                c_files.append(os.path.join(root, file))
    if len(c_files) == 0:
        log(ERROR, f"No .c files found in {target_dir}.")
        writer.writerow([package, 'O', 'O', 'X', '-', "no .c file found"])
        tsvfile.flush()
        return False
    log(INFO, f"Found {len(c_files)} .c files in {target_dir}.")
    return sparrow(package, c_files)
                
                
'''
Run this script directly with -f option (target directory(s))
-f argument must have one or more .c files for Sparrow to analyze
and add the following options
-io: Integer Overflow
-dz: Division by Zero
-tio: Times Integer Overflow
-mio: Minus Integer Overflow
-pio: Plus Integer Overflow
-sio: Shift Integer Overflow
-bo: Buffer Overflow
-no_bo: No Buffer Overflow(because buffer overflow alrams are too noisy)

If none of these alram flags are given, it runs on a default setting

Input: str (package name), TextIO (tsvfile), csv.writer
Output: bool (True: success, False: fail)
'''
def main():
    IS_SOLO_SPARROW = True
    config.setup("SPARROW")
    log(INFO, "You are running sparrow.py script directly.")
    log(INFO, "This script only runs on the first argument of -f option.")
    target_files = []
    if not os.path.exists(config.configuration["ARGS"].files[0]):
        log(ERROR, f"{config.configuration['ARGS'].files[0]} does not exist.")
        config.patron_exit("SPARROW")
    for root, dirs, files in os.walk(config.configuration["ARGS"].files[0]):
        for file in files:
            if file.endswith('.c'):
                target_files.append(os.path.abspath(os.path.join(root, file)))
    print(config.configuration["ARGS"].files[0])
    sparrow("top", target_files)

if __name__ == '__main__':
    main()

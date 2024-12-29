#!/usr/bin/env python3
import sys
import os
import csv
import config
import datetime
import subprocess
from logger import log, INFO, ERROR, WARNING, ALL
from typing import TextIO
import copy
import time
'''
Function that actually runs Sparrow
default options are set in config.py

Input: str (package name)
Output: tuple (TextIO, subprocess.Popen)
'''


def run_sparrow(file: str) -> tuple[TextIO, subprocess.Popen]:
    os.chdir(os.path.dirname(file))
    match config.configuration["PURPOSE"]:
        case "PREPROCESS":
            if os.path.exists(
                    os.path.join(os.path.dirname(file),
                                 'sparrow-out')) and not config.configuration["OVERWRITE_SPARROW"]:
                log(ALL, f"{os.path.join(os.path.dirname(file), 'sparrow-out')} already exists.")
                return None, None
            else:
                try:
                    os.system(f'rm -rf {os.path.join(os.path.dirname(file), "sparrow-out")}')
                except:
                    log(ERROR,
                        f"Failed to remove {os.path.join(os.path.dirname(file), 'sparrow-out')}")
                    return None, None
                sparrow_log = open('sparrow_log', 'w')
            cmd = [config.configuration["SPARROW_BIN_PATH"], file
                   ] + config.preprocess_configuration[
                       "DEFAULT_SPARROW_OPT"] + config.preprocess_configuration["USER_SPARROW_OPT"]
        case "SPARROW":
            if os.path.exists(os.path.join(
                    os.path.dirname(file),
                    'sparrow-out')) and not config.sparrow_configuration["OVERWRITE_SPARROW"]:
                log(ALL, f"{os.path.join(os.path.dirname(file), 'sparrow-out')} already exists.")
                return None, None
            else:
                try:
                    os.system(f'rm -rf {os.path.join(os.path.dirname(file), "sparrow-out")}')
                except:
                    log(ERROR,
                        f"Failed to remove {os.path.join(os.path.dirname(file), 'sparrow-out')}")
                    return None, None
                sparrow_log = open('sparrow_log', 'w')
            cmd = [config.configuration["SPARROW_BIN_PATH"], file] + config.sparrow_configuration[
                "DEFAULT_SPARROW_OPT"] + config.sparrow_configuration["USER_SPARROW_OPT"]
    log(INFO, f"Running sparrow with {cmd}")
    return sparrow_log, subprocess.Popen(cmd, stdout=sparrow_log, stderr=subprocess.STDOUT)


'''
Function that controls the Sparrow process (log, timeout, etc.)

Input: str (package name), list (list of file paths)
Output: bool (True: success, False: fail)
'''


def sparrow(package: str, files: list) -> bool:
    start_time = time.time()
    time_record = dict()
    SPARROW_PKG_DIR = os.path.join(config.configuration["SPARROW_LOG_DIR"], package)
    if not os.path.exists(SPARROW_PKG_DIR):
        os.mkdir(SPARROW_PKG_DIR)
    tsvfile = open(
        os.path.join(config.configuration["SPARROW_LOG_DIR"],
                     '{}_sparrow_stat.tsv'.format(package)), 'a')
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
        if sparrow_log is None or process is None:
            log(ALL, f"Skipping {files[i]} ...")
            rest_files.remove(files[i])
            i += 1
            continue
        proc_cnt += 1
        procs.append((files[i], process, sparrow_log))
        rest_files.remove(files[i])
        i += 1
        if proc_cnt > config.configuration["PROCESS_LIMIT"] or i >= len(files):
            for file, process, sparrow_log in procs:
                try:
                    stdout, stderr = process.communicate(timeout=3600 * 6)
                except subprocess.TimeoutExpired:
                    log(ERROR, f"Timeout for {file}.")
                    time_record[file]['end'] = 0
                    import signal
                    log(ERROR, f"Killing the process for {file} ...")
                    try:
                        os.killpg(process.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        log(ERROR, f"process for {file} already exited.")
                    writer.writerow([file, 'X'])
                    tsvfile.flush()
                    sparrow_log.close()
                    proc_cnt -= 1
                    continue
                sparrow_log.close()
                if process.returncode == 0:
                    log(ALL, f"{file} is successfully analyzed.")
                    time_record[file]['end'] = time.time()
                    writer.writerow([file, 'O'])
                    success_cnt += 1
                else:
                    log(ERROR, f"Failed to analyze {file}.")
                    time_record[file]['end'] = 0
                    log(
                        ERROR,
                        f"Check {os.path.join(os.path.dirname(file), 'sparrow_log')} for more information."
                    )
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
            if 'end' not in time_record[file] or time_record[file]['end'] == 0:
                f.write(f"{file}: Finished too quickly or Timeout or Error\n")
            else:
                time_lst.append(time_record[file]['end'] - time_record[file]['start'])
                f.write(f"{file}: {time_record[file]['end'] - time_record[file]['start']}\n")
        if len(time_lst) != 0:
            f.write(f"Average: {sum(time_lst)/len(time_lst)}\n")
        f.write(f"Total time: {time.time() - start_time}\n")
    log(ALL, f"{success_cnt} files are successfully analyzed.")
    log(ALL, f"Output for analysis is saved in {SPARROW_PKG_DIR}")
    return True


def mk_worklist(targets):
    log(ALL, "Looking for .c files in the target directories ...")
    target_files = []
    for target in targets:
        for root, dirs, files in os.walk(target):
            for file in files:
                if file.endswith('.c'):
                    target_files.append(os.path.abspath(os.path.join(root, file)))
    log(ALL, f"Found {len(target_files)} .c files for the analysis target.")
    target_sorted = dict()
    for target in target_files:
        if_found_package_name = False
        for tok in target.split('/'):
            if tok.startswith('_'):
                target_sorted[tok] = [
                    target
                ] if tok not in target_sorted else target_sorted[tok] + [target]
                if_found_package_name = True
                break
        if not if_found_package_name:
            target_sorted['UNKNOWN'] = [
                target
            ] if 'UNKNOWN' not in target_sorted else target_sorted['UNKNOWN'] + [target]
    return target_sorted


def execute_worklist(worklist):
    log(
        ALL,
        f"@@@WARNING: ANALYSIS PROCESS MIGHT TAKE UNEXPECTEDLY LONG TIME DEPENDING ON THE # ALARMS@@@"
    )
    for key in worklist:
        log(ALL, f"Analyzing on {key}, # of files: {len(worklist[key])}")
        sparrow(key, worklist[key])


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
    for d in config.configuration["ARGS"].target_directory:
        if not os.path.exists(d):
            log(ERROR, f"Given directory: {d} does not exist.")
            config.bad_ending(config.configuration["OUT_DIR"])
    worklist = mk_worklist(config.configuration["ARGS"].target_directory)
    execute_worklist(worklist)
    config.happy_ending(config.configuration["OUT_DIR"])


if __name__ == '__main__':
    config.setup_sparrow()
    main()

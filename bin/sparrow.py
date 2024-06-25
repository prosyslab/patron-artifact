#!/usr/bin/env python3
import sys
import os
import csv
import config
import datetime
import subprocess
from logger import log, INFO, ERROR, WARNING

SPARROW_LOG_DIR = os.path.join(config.configuration['OUT_DIR'], 'sparrow_logs')

def run_sparrow(file):
    os.chdir(os.path.dirname(file))
    sparrow_log = open('sparrow_log', 'w')
    if os.path.exists(os.path.join(os.path.dirname(file), 'sparrow-out')):
        os.system(f'rm -rf {os.path.join(os.path.dirname(file), "sparrow-out")}')
    cmd = [config.configuration["SPARROW_BIN_PATH"], file] + config.configuration["DEFAULT_SPARROW_OPT"] + config.configuration["USER_SPARROW_OPT"]
    log(INFO, f"Running sparrow with {cmd}")
    return sparrow_log, subprocess.Popen(cmd,
                                 stdout=sparrow_log,
                                 stderr=subprocess.STDOUT)

def sparrow(package, files):
    tsvfile = open(os.path.join(SPARROW_LOG_DIR, '{}_sparrow_stat.tsv'.format(package)), 'a')
    writer = csv.writer(tsvfile, delimiter='\t')
    writer.writerow(['Package', 'Status'])
    tsvfile.flush()
    success_cnt = 0
    for file in files:
        log(INFO, f"Running sparrow for {file} ...")
        sparrow_log, process = run_sparrow(file)
        try:
            stdout, stderr = process.communicate(timeout=3600)
        except subprocess.TimeoutExpired:
            log(ERROR, f"Timeout for {file}.")
            process.kill()
            writer.writerow([file, 'X'])
            tsvfile.flush()
            sparrow_log.close()
            continue
        sparrow_log.close()
        if process.returncode == 0:
            log(INFO, f"{file} is successfully analyzed.")
            writer.writerow([file, 'O'])
            success_cnt += 1
        else:
            log(ERROR, f"Failed to analyze {file}.")
            log(ERROR, f"Check {os.path.join(os.path.dirname(file), 'sparrow_log')} for more information.")
            writer.writerow([file, 'X'])
        tsvfile.flush()
    tsvfile.close()
    if success_cnt == 0:
        log(ERROR, f"No file is successfully analyzed.")
        return False
    log(INFO, f"{success_cnt} files are successfully analyzed.")
    return True

def sparrow_pipe(package, tsvfile, writer):
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
                
                

def main():
    config.setup("SPARROW")
    log(INFO, "You are running sparrow.py script directly.")
    target_files = []
    for file in config.configuration["ARGS"].files:
        if not os.path.exists(file):
            log(ERROR, f"{file} does not exist.")
            main_usage()
            exit(1)
        target_files.append(os.path.abspath(file))
    sparrow(target_files)

if __name__ == '__main__':
    main()

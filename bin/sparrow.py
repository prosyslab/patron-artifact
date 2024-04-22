#!/usr/bin/env python3
import sys
import os
import csv
import config
import datetime
import subprocess
from logger import log, INFO, ERROR, WARNING

def run_sparrow(file):
    os.chdir(os.path.dirname(file))
    log = open('sparrow_log', 'w')
    print(file)
    return log, subprocess.Popen([config.configuration["SPARROW_BIN_PATH"], file] + config.configuration["DEFAULT_SPARROW_OPT"] + config.configuration["USER_SPARROW_OPT"],
                                 stdout=log,
                                 stderr=subprocess.STDOUT)

def sparrow(files):
    tsvfile = open(os.path.join(config.configuration['OUT_DIR'], 'sparrow_stat_{}.tsv'.format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))), 'a')
    writer = csv.writer(tsvfile, delimiter='\t')
    writer.writerow(['Package', 'Status'])
    tsvfile.flush()
    for file in files:
        log(INFO, f"Running sparrow for {file} ...")
        sparrow_log, process = run_sparrow(file)
        process.wait()
        sparrow_log.close()
        if process.returncode == 0:
            log(INFO, f"{file} is successfully analyzed.")
            writer.writerow([file, 'O'])
        else:
            log(ERROR, f"Failed to analyze {file}.")
            writer.writerow([file, 'X'])
        tsvfile.flush()
    tsvfile.close()
    
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
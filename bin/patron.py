#!/usr/bin/env python3
import config
import os
from logger import log, INFO, ERROR, WARNING
import subprocess

expriment_ready_to_go = {
    "patron": [
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13",
        "14", "15", "16", "17", "18", "19", "20"
    ],
    "patchweave": [
        "1", "2-1", "2-2", "3", "4", "5", "6", "7", "8", "9-1", "9-2", "10",
        "12-1", "12-2", "12-3", "13", "17", "19", "21", "22", "23", "24"
    ]
    }
level = ""
donor_list = []

def run_patron(worklist):
    for cmd in worklist:
        log(INFO, f"Running patron with {cmd}")
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result.wait()
        if result.returncode != 0:
            log(ERROR, f"Failed to run patron with {cmd}")
            log(ERROR, result.stderr.read().decode('utf-8'))
        log(INFO, f"Successfully ran patron with {cmd}")

def mk_worklist():
    base_cmd = [config.configuration["PATRON_BIN_PATH"]]
    out_opt = ["-o", config.configuration["OUT_DIR"]]
    worklist = []
    for donee in config.configuration["DONEE_LIST"]:
        for donor in donor_list:
            worklist.append(base_cmd + [donee, donor] + out_opt)
    return worklist

def setup_database():
    log(WARNING, f"Running sparrow to construct databse from scratch...")
    os.chdir(config.configuration["EXP_ROOT_PATH"])
    log(INFO, "Detailed log is saved in {}".format(os.path.join(config.configuration["EXP_ROOT_PATH"], 'out')))
    result_patchweave = subprocess.Popen(['python3', 'bin/run.py', '-sparrow', 'patchweave'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result_patron = subprocess.Popen(['python3', 'bin/run.py', '-sparrow', 'patron'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result_patchweave.wait()
    result_patron.wait()
    if result_patchweave.returncode != 0:
        log(ERROR, f"Failed to run sparrow for patchweave.")
        log(ERROR, result_patchweave.stderr.read().decode('utf-8'))
        exit(1)
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

def check_database():
    global donor_list
    patron_bench_path = os.path.join(config.configuration["BENCHMARK_PATH"], "patron")
    patchweave_bench_path = os.path.join(config.configuration["BENCHMARK_PATH"], "patchweave")
    for file in os.listdir(patron_bench_path):
        if not os.path.exists(os.path.join(patchweave_bench_path, file, 'bug', 'sparrow-out')):
            if file in expriment_ready_to_go["patron"]:
                log(ERROR, f"sparrow-out for {file} does not exist in {patron_bench_path}")
                return False
        donor_list.append(os.path.join(patchweave_bench_path, file))
    for file in os.listdir(patchweave_bench_path):
        if not os.path.exists(os.path.join(patchweave_bench_path, file, 'donor', 'bug', 'sparrow-out')):
            if file in expriment_ready_to_go["patchweave"]:
                log(ERROR, f"sparrow-out for {file} does not exist in {patchweave_bench_path}")
                return False
        donor_list.append(os.path.join(patchweave_bench_path, file, 'donor'))
    return True            
            
def main():
    global level
    level = "PATRON"
    config.setup(level)
    if not check_database():
        setup_database()
    if not check_donee(config.configuration["DONEE_LIST"]):
        log(ERROR, "DONEE is not ready.")
        exit(1)
    run_patron(mk_worklist())

if __name__ == '__main__':
    main()
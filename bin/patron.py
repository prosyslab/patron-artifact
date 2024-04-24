#!/usr/bin/env python3
import config
import os
from logger import log, INFO, ERROR, WARNING
import subprocess
import json
import csv
import datetime

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
    tsv_file = open(os.path.join(config.configuration["OUT_DIR"], "patron_{}.tsv".format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))), 'a')
    writer = csv.writer(tsv_file, delimiter='\t')
    write.writerow(["PROJECT", "ALARM_ID", "STATUS"])
    tsv_file.flush()
    os.chdir(config.configuration["PATRON_ROOT_PATH"])
    for cmd in worklist:
        log(INFO, f"Running patron with {cmd}")
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result.wait()
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
    out_opt = ["-o", config.configuration["OUT_DIR"]]
    worklist = []
    for donee in config.configuration["DONEE_LIST"]:
        worklist.append(base_cmd + ['patch' + donee] + out_opt)
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
        if not os.path.exists(os.path.join(patron_bench_path, file, 'bug', 'sparrow-out')):
            if file in expriment_ready_to_go["patron"]:
                log(ERROR, f"sparrow-out for {file} does not exist in {patron_bench_path}")
                return False
        donor_list.append(os.path.join(patron_bench_path, file))
    for file in os.listdir(patchweave_bench_path):
        if not os.path.exists(os.path.join(patchweave_bench_path, file, 'donor', 'bug', 'sparrow-out')):
            if file in expriment_ready_to_go["patchweave"]:
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

def main():
    global level
    level = "PATRON"
    config.setup(level)
    if not check_sparrow():
        run_sparrow()
    if not check_database():
        mk_database()
    if not check_donee(config.configuration["DONEE_LIST"]):
        log(ERROR, "DONEE is not ready.")
        exit(1)
    run_patron(mk_worklist())

if __name__ == '__main__':
    main()
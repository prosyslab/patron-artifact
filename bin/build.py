#!/usr/bin/env python3
import os
import sys
import subprocess
import datetime
import csv
import config
import combine
import sparrow
from logger import log, INFO, ERROR, WARNING

BIN_DIR = os.path.dirname(os.path.realpath(__file__))
PKG_DIR = os.path.join(os.path.dirname(BIN_DIR), 'package')
LIST_DIR = os.path.join(PKG_DIR, 'debian_lists')

def mk_category_dict():
    categories = dict()
    if config.configuration["PIPE_MODE"]:
        packages = config.configuration["ARGS"].pipe
    else:
        packages = config.configuration["ARGS"].build
    if packages[0] == "all" and len(packages) == 1:
        log(INFO, "Building all packages ...")
        for file in os.listdir(LIST_DIR):
            if file.endswith(".txt"):
                category = str(file).split('.')[0]
                with open(os.path.join(LIST_DIR, file), 'r') as f:
                    categories[category] = [ line.strip() for line in f.readlines()]
        return categories
    else:
        packages = [os.path.join(LIST_DIR, os.path.basename(package)) for package in packages]
        log(INFO, "Building selected package categories {}".format(packages))
        for package in packages:
            category_name = os.path.basename(package).split('.')[0]
            if not os.path.exists(os.path.join(package)):
                log(WARNING, f"{category_name} is not found in the package list.")
                continue
            with open(os.path.join(package), 'r') as f:
                categories[category_name] = [ line.strip() for line in f.readlines()]
        return categories

def crawl():
    log(INFO, "Retrieving the list of Debian packages from web ...")
    if os.path.exists(LIST_DIR):
        log(WARNING, "The package list directory already exists. Skip crawling.")
        return
    status = subprocess.run(
        [sys.executable,
        os.path.join(PKG_DIR, 'debian_crawler.py')],
        check=True, capture_output=True)
    if status.returncode != 0:
        log(ERROR, "Failed to retrieve the list of packages.")
        exit(1)
    log(INFO, "Package Lists are created at {}.".format(os.path.join(PKG_DIR, 'debian_lists')))

def check_smake_result(path):
    if not os.path.exists(path):
        log(ERROR, f"{path} does not exist.")
        return False
    os.chdir(path)
    status = subprocess.run(['ls', '-al'], check=True, capture_output=True)
    output = status.stdout.decode('utf-8')
    status = subprocess.run(['wc', '-l'], input=output.encode('utf-8'), check=True, capture_output=True)
    output = status.stdout.decode('utf-8').strip()
    if output == '8' or (output.isdigit() and int(output) < 9):
        log(WARNING, f"{path} is empty.")
        return False
    log(INFO, f"{path} is not empty: it is a good sign.")
    return True

def kill_processes():
    log(INFO, "Building process Timed out! Assuming there is a lock on apt process. Killing the apt process ...")
    try:
        ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
        grep = subprocess.Popen(['grep', 'apt'], stdin=ps.stdout, stdout=subprocess.PIPE)
        ps.stdout.close() 

        awk = subprocess.Popen(['awk', '{print $2}'], stdin=grep.stdout, stdout=subprocess.PIPE)
        grep.stdout.close() 

        process_ids, _ = awk.communicate()
        process_ids = process_ids.decode('utf-8').split()
        
        if not process_ids:
            log(INFO, "No apt process running.")
            return False

        kill = subprocess.Popen(['xargs', 'kill', '-9'], stdin=subprocess.PIPE)
        kill.communicate(input='\n'.join(process_ids).encode('utf-8'))

        if kill.returncode == 0:
            log(INFO, f"Killed processes: {process_ids}")
            return True
        else:
            log(WARNING, f"Failed to kill apt parocess. Return code: {kill.returncode}")
            return False

    except Exception as e:
        log(ERROR, f"An error occurred while killing apt process: {e}")
        return False
        

def smake_pipe(category, package, tsvfile, writer, smake_out_dir, tries):
    log(INFO, f"Building {package} ...")
    BUILD_LOG_PATH = os.path.join(config.configuration['OUT_DIR'], "build_logs")
    if not os.path.exists(BUILD_LOG_PATH):
        os.mkdir(BUILD_LOG_PATH)
    proc = None
    out = None
    err = None
    try:
        proc = subprocess.Popen([os.path.join(PKG_DIR, 'build-deb.sh'), package, str(category)],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate(timeout=900)
    except subprocess.TimeoutExpired:
        log(ERROR, f"building {package} has timed out")
        if tries < 4 and kill_processes():
            tries = tries + 1
            log(INFO, f"Retrying building {package} ... ({tries} time(s))")
            return smake_pipe(category, package, tsvfile, writer, smake_out_dir, tries)
        log(ERROR, f"Failed to build {package} after {tries} retries.")
        if proc != None:
            proc.kill()
        writer.writerow([package, 'X', '-', '-', '-','timeout'])
        tsvfile.flush()
        with open(os.path.join(BUILD_LOG_PATH, package + '_build_log.txt'), 'w') as f:
            if out != None:
                f.write(out.decode('utf-8'))
            if err != None:
                f.write(err.decode('utf-8'))
    except Exception as e:
        log(ERROR, e)
        if proc != None:
            proc.kill()
        try:
            with open(os.path.join(BUILD_LOG_PATH, package + '_build_log.txt'), 'w') as f:
                if out != None:
                    f.write(out.decode('utf-8'))
                if err != None:
                    f.write(err.decode('utf-8'))
            log(ERROR, f"building {package} has failed")
            parsed_errors = e.stderr.decode('utf-8').split('\n')
            for error in parsed_errors[-10:]:
                log(ERROR, error)
            writer.writerow([package, 'X', '-', '-', '-', parsed_errors[-2]])
            tsvfile.flush()
            return False, []
        except Exception as e:
            log(ERROR, f"building {package} has failed: Unexpected Exit!!")
            log(ERROR, e)
            return False, []
    with open(os.path.join(BUILD_LOG_PATH, package + '_build_log.txt'), 'w') as f:
        if out != None:
            f.write(out.decode('utf-8'))
        if err != None:
            f.write(err.decode('utf-8'))
    log(INFO, f"building {package} has succeeded")
    if not check_smake_result(os.path.join(smake_out_dir, str(category), package)):
        log(WARNING, f"{package} has no .i files")
        writer.writerow([package, 'X', '-', '-', '-', "no .i files"])
        tsvfile.flush()
        return False, []
    log(INFO, f"{package} has .i files!... continue to next step")
    next_args = [os.path.join(smake_out_dir, str(category), package)]
    return True, next_args
            
        
def smake(tries):
    packages = mk_category_dict()
    smake_out_dir = os.path.join(PKG_DIR, 'smake_out')
    if not os.path.exists(smake_out_dir):
        os.mkdir(smake_out_dir)
    for category in packages.keys():
        if not os.path.exists(os.path.join(smake_out_dir, str(category))):
            os.mkdir(os.path.join(smake_out_dir, str(category)))
        packages = packages[ str(category) ]
        tsvfile = open(os.path.join(config.configuration['OUT_DIR'], '{}_build_stat_{}.tsv'.format(category, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))), 'a')
        writer = csv.writer(tsvfile, delimiter='\t')
        writer.writerow(['Package', 'Status', '.i files?', 'Error Msg'])
        tsvfile.flush()
        os.chdir(PKG_DIR)
        for package in packages:
            package = package.strip()
            log(INFO, f"Building {package} ...")
            try:
                proc = subprocess.Popen([os.path.join(PKG_DIR, 'build-deb.sh'), package, str(category)],
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                proc = proc.communicate(timeout=900)
            except subprocess.TimeoutExpired:
                log(ERROR, f"building {package} has timed out")
                if tries < 4 and kill_processes():
                    tries = tries + 1
                    log.INFO(f"Retrying building {package} ... ({tries} time(s))")
                    return smake_pipe(category, package, tsvfile, writer, smake_out_dir, tries)
                log(ERROR, f"Failed to build {package} after {tries} retries.")
                proc.kill()
                log(ERROR, f"building {package} has timed out")
                writer.writerow([package, 'X', '-', 'timeout'])
                tsvfile.flush()
            except Exception as e:
                proc.kill()
                try:
                    log(ERROR, f"building {package} has failed")
                    parsed_errors = e.stderr.decode('utf-8').split('\n')
                    for error in parsed_errors[-10:]:
                        log(ERROR, error)
                    writer.writerow([package, 'X', '-', parsed_errors[-2]])
                    tsvfile.flush()
                except Exception as e:
                    continue
            log(INFO, f"building {package} has succeeded")
            is_smake_out = check_smake_result(os.path.join(smake_out_dir, str(category), package))
            is_smake_out = 'O' if is_smake_out else 'X'
            writer.writerow([package, 'O', is_smake_out, '-'])
            tsvfile.flush()
def run():
    crawl()
    smake()

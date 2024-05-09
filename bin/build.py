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
PKG_DIR = os.path.join(os.path.dirname(BIN_DIR), 'pkg')
LIST_DIR = os.path.join(PKG_DIR, 'lists')

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
    status = subprocess.run(
        [sys.executable,
        os.path.join(PKG_DIR, 'debian_crawler.py')],
        check=True, capture_output=True)
    if status.returncode != 0:
        log(ERROR, "Failed to retrieve the list of packages.")
        exit(1)
    log(INFO, "Package Lists are created at {}.".format(os.path.join(PKG_DIR, 'lists')))

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
    log(INFO, f"{path} is not empty.")
    return True

def smake_pipe():
    tsvfile = open(os.path.join(config.configuration['OUT_DIR'], 'pipe_stat_{}.tsv'.format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))), 'a')
    writer = csv.writer(tsvfile, delimiter='\t')
    writer.writerow(['Package', 'Build', 'Combine', 'Sparrow','Error Msg'])
    tsvfile.flush()
    packages = mk_category_dict()
    i_files_dir = os.path.join(PKG_DIR, 'i_files')
    if not os.path.exists(i_files_dir):
            os.mkdir(i_files_dir)
    for category in packages.keys():
        if not os.path.exists(os.path.join(i_files_dir, str(category))):
            os.mkdir(os.path.join(i_files_dir, str(category)))
        packages = packages[ str(category) ]
        os.chdir(PKG_DIR)
        for package in packages:
            package = package.strip()
            log(INFO, f"Building {package} ...")
            try:
                proc = subprocess.Popen([os.path.join(PKG_DIR, 'build-deb.sh'), package, str(category)],
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = proc.communicate(timeout=900)
            except subprocess.TimeoutExpired:
                proc.kill()
                log(ERROR, f"building {package} has timed out")
                writer.writerow([package, 'X', '-', '-', '-','timeout'])
                tsvfile.flush()
            except Exception as e:
                proc.kill()
                try:
                    log(ERROR, f"building {package} has failed")
                    parsed_errors = e.stderr.decode('utf-8').split('\n')
                    for error in parsed_errors[-10:]:
                        log(ERROR, error)
                    writer.writerow([package, 'X', '-', '-', '-', parsed_errors[-2]])
                    tsvfile.flush()
                except Exception as e:
                    continue
            log(INFO, f"building {package} has succeeded")
            is_i_files = check_smake_result(os.path.join(i_files_dir, str(category), package))
            if not is_i_files:
                log(WARNING, f"{package} has no .i files")
                writer.writerow([package, 'X', '-', '-', '-', "no .i files"])
                tsvfile.flush()
                continue
            log(INFO, f"{package} has .i files!... continue to next step")
            is_success = combine.combine_pipe([os.path.join(i_files_dir, str(category), package)])
            if not is_success:
                writer.writerow([package, 'O', 'X', '-', '-', "combine error"])
                tsvfile.flush()
                continue
            is_success = sparrow.sparrow_pipe(package)
            if not is_success:
                writer.writerow([package, 'O', 'O', 'X', '-', "sparrow error"])
                tsvfile.flush()
                continue
            writer.writerow([package, 'O', 'O', 'O', 'O', '-'])
            
        
def smake():
    packages = mk_category_dict()
    i_files_dir = os.path.join(PKG_DIR, 'i_files')
    if not os.path.exists(i_files_dir):
        os.mkdir(i_files_dir)
    for category in packages.keys():
        if not os.path.exists(os.path.join(i_files_dir, str(category))):
            os.mkdir(os.path.join(i_files_dir, str(category)))
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
            is_i_files = check_smake_result(os.path.join(i_files_dir, str(category), package))
            is_i_files = 'O' if is_i_files else 'X'
            writer.writerow([package, 'O', is_i_files, '-'])
            tsvfile.flush()
def run():
    crawl()
    smake()

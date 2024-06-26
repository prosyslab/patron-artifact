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
import find_duplicate_pkg
from typing import TextIO

BIN_DIR = os.path.dirname(os.path.realpath(__file__))
PKG_DIR = os.path.join(os.path.dirname(BIN_DIR), 'package')
LIST_DIR = os.path.join(PKG_DIR, 'debian_lists')

'''
Function that generates worklist that is a dictionary of package categories.

Input: None
Output: Dictionary (key: category, value: list of packages)
'''
def mk_smake_worklist() -> dict:
    categories = dict()
    if config.configuration["PIPE_MODE"]:
        packages = config.configuration["ARGS"].pipe
    else:
        packages = config.configuration["ARGS"].build
    if packages[0] == "all" and len(packages) == 1:
        packages = [os.path.join(LIST_DIR, 'test.txt')]
    else:
        packages = [os.path.join(LIST_DIR, os.path.basename(package)) for package in packages]
    log(INFO, "Building selected package categories {} (default:experiment_setup.txt)".format(packages))
    for package in packages:
        category_name = os.path.basename(package).split('.')[0]
        if not os.path.exists(os.path.join(package)):
            log(WARNING, f"{category_name} is not found in the package list.")
            continue
        with open(os.path.join(package), 'r') as f:
            categories[category_name] = [ line.strip() for line in f.readlines()]
    return categories
    
'''
Function that runs package/debian_crawler.py
Check crawl() function for more details

Input: None
Output: Boolean (True: Package list is retrieved, False: Package list is not retrieved)
'''
def get_package_list_from_web() -> bool:
    if os.path.exists(LIST_DIR):
        log(WARNING, "The package list directory already exists. Skip crawling.")
        return False
    status = subprocess.run(
        [sys.executable,
        os.path.join(PKG_DIR, 'debian_crawler.py')],
        check=True, capture_output=True)
    if status.returncode != 0:
        log(ERROR, "Failed to retrieve the list of packages.")
        exit(1)
    return True
        
'''
Function that crawls the Debian package list from the bookworm and save them based on the project category.
This function is called when -crawl option is given.
It has two parts:
1) Retrieve the list of Debian packages from web and save them in the package/debian_lists directory
2) Check duplicated packages within each category and remove them
This is because packages with different web names can actually be the same package.
This function prematurely exits if the package list directory already exists.
Delete the directory if you want to crawl again.

Input: None
Output: None
'''
def crawl() -> None:
    # log(INFO, "Retrieving the list of Debian packages from web ...")
    # if not get_package_list_from_web():
    #     return
    # log(INFO, "Packages are retrieved.")
    # log(INFO, "Checking duplicated packages ...")
    find_duplicate_pkg.run([os.path.join(LIST_DIR, file) for file in os.listdir(LIST_DIR) if file.endswith(".txt")])
    log(INFO, "Crawling Summary:")
    for file in os.listdir(os.path.join(PKG_DIR, 'debian_lists')):
        if file.endswith(".txt"):
            with open(os.path.join(LIST_DIR, file), 'r') as f:
                log(INFO, f"{file} has {len(f.readlines())} packages.")
    log(INFO, "Package Lists are created at {}.".format(os.path.join(PKG_DIR, 'debian_lists')))

'''
Function that checks if the smake result is successfully generated.
Otherwise, pipeline doesn't have to waste resources trying the next steps
Smake sometimes weirdly fails to generate .i files.
There are various reasons for this, but this function will check if the package has .i files.

Input: None
Output: Boolean (True: Smake result is successfully generated, False: Smake result is not successfully generated)
'''
def check_smake_result(path:str) -> bool:
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

'''
Function that kills apt processes.
apt-related processes often gets locked.
This is caused by two main reasons.
1) smake() function is run parallelly, or other process on your OS is occupying apt (Separate containers still does this).
2) Sometimes, apt causes random bugs.
For this matter, this function kills the locked ones for retry.(this is related to "tries" argument in smake() function)

Input: None
Output: Boolean (True: killing is successful, False: killing is not successful)
'''
def kill_processes() -> bool:
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
        
'''
Function that procedure of running package/build-deb.sh within the pipeline.
For more detail about smake, check smake() function.

Input: category(category of the package), package(name of the package), 
       tsvfile(file object to write the result), writer(csv.writer object), 
       smake_out_dir(directory to save the smake result), tries(number of tries (default=0))
Output: Boolean (True: Building is successful, False: Building is not successful), List (List of arguments for the next step)
'''
def smake_pipe(category: str, package: str, tsvfile: TextIO, writer: csv.writer, smake_out_dir: str, tries: int) -> tuple[bool, list]:
    log(INFO, f"Building {package} ...")
    if smake(category, package, tsvfile, writer, smake_out_dir, tries):
        next_args = [os.path.join(smake_out_dir, str(category), package)]
        return True, next_args
    else:
        return False, []
    
'''
Function that runs package/build-deb.sh on non-pipeline mode.
For more detail about smake, check smake() function.

Input: tries(number of tries (default=0))
Output: None(Not interested in build_only mode.(check the log for the result))
'''       
def smake_sep(tries:int) -> None:
    packages = mk_smake_worklist()
    smake_out_dir = os.path.join(PKG_DIR, 'smake_out')
    if not os.path.exists(smake_out_dir):
        os.mkdir(smake_out_dir)
    for category in packages.keys():
        if not os.path.exists(os.path.join(smake_out_dir, str(category))):
            os.mkdir(os.path.join(smake_out_dir, str(category)))
        packages = packages[ str(category) ]
        tsvfile = open(os.path.join(config.configuration['OUT_DIR'], '{}_build_stat_{}.tsv'.format(category, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))), 'a')
        writer = csv.writer(tsvfile, delimiter='\t')
        writer.writerow(['Package', 'Build', 'Combine', 'Sparrow','Error Msg'])
        tsvfile.flush()
        tsvfile.flush()
        os.chdir(PKG_DIR)
        for package in packages:
            package = package.strip()
            log(INFO, f"Building {package} ...")
            smake(category, package, tsvfile, writer, smake_out_dir, tries)

'''
Function that runs package/build-deb.sh.
build-deb.sh is sequence of smake procedure.
smake is a tool that generates .i files from the source code.
Given Makefile of a package, smake extracts all linked files and generates .i files for each executable binary.
This is an essential procedure for Sparrow, the static analyzer.

Input: category(category of the package), package(name of the package), 
       tsvfile(file object to write the result), writer(csv.writer object), 
       smake_out_dir(directory to save the smake result), tries(number of tries (default=0))
Output: Boolean (True: Building is successful, False: Building is not successful)
'''
def smake(category: str, package: str, tsvfile: TextIO, writer: csv.writer, smake_out_dir: str, tries: int) -> bool:
    proc = None
    out = None
    err = None
    BUILD_LOG_PATH = os.path.join(config.configuration['OUT_DIR'], "build_logs")
    if not os.path.exists(BUILD_LOG_PATH):
        os.mkdir(BUILD_LOG_PATH)
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
            return False
        except Exception as e:
            log(ERROR, f"building {package} has failed: Unexpected Exit!!")
            log(ERROR, e)
            return False
    with open(os.path.join(BUILD_LOG_PATH, package + '_build_log.txt'), 'w') as f:
        try:
            if out != None:
                f.write(out.decode('utf-8'))
            if err != None:
                f.write(err.decode('utf-8'))
        except UnicodeDecodeError as e:
            log(ERROR, "could not write {}, due to decoding".format(package + '_build_log.txt'))
    if not check_smake_result(os.path.join(smake_out_dir, str(category), package)):
        log(WARNING, f"{package} has no .i files")
        writer.writerow([package, 'X', '-', '-', '-', "build error, find log at {}".format(os.path.join(BUILD_LOG_PATH, package + '_build_log.txt'))])
        tsvfile.flush()
        log(ERROR, f"building {package} has failed because of no .i files")
        return False
    log(INFO, f"building {package} has succeeded")
    log(INFO, f"{package} has .i files!... continue to next step")
    return True
    
def run():
    crawl()
    smake_sep(0)

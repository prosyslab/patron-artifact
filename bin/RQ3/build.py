#!/usr/bin/env python3
import os
import sys
import subprocess
import datetime
import time
import csv
import config
import combine
import sparrow
from logger import log, INFO, ERROR, WARNING, ALL
import find_duplicate_pkg
from typing import TextIO


'''
Function that gets the target list from the configuration data.
If the target list is "all", it reads all the default target package list (113 packages).

Input: None
Output: list of package names
'''

def get_target_list():
    target_list = config.configuration["ARGS"].projects
    if len(target_list) == 1 and target_list[0] == "all":
        target_list = open(configuration["DEFAULT_TARGET_LIST_PATH"], 'r').readlines()
    return target_list

'''
Function that checks if the smake result is successfully generated.
Otherwise, pipeline doesn't have to waste resources trying the next steps
Smake sometimes weirdly fails to generate .i files.
There are various reasons for this, but this function will check if the package has .i files.

Input: path (path to the package)
Output: Boolean (True: Smake result is successfully generated, False: Smake result is not successfully generated)
'''

def check_smake_result(path: str) -> bool:
    if not os.path.exists(path):
        log(ERROR, f"{path} does not exist.")
        print(1)
        return False
    os.chdir(path)
    cmd = ["find", path, "-type", "f", "-name", "*.i", "-print", "-quit"]
    output = subprocess.run(cmd, capture_output=True, text=True)
    if not output.stdout.strip():
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
    log(
        ALL,
        "Building process Timed out! Assuming there is a lock on apt process. Killing the apt process ..."
    )
    try:
        ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
        grep = subprocess.Popen(['grep', 'apt'], stdin=ps.stdout, stdout=subprocess.PIPE)
        ps.stdout.close()
        awk = subprocess.Popen(['awk', '{print $2}'], stdin=grep.stdout, stdout=subprocess.PIPE)
        grep.stdout.close()
        process_ids, _ = awk.communicate()
        process_ids = process_ids.decode('utf-8').split()
        if not process_ids:
            log(ALL, "No apt process running.")
            return False
        kill = subprocess.Popen(['xargs', 'kill', '-9'], stdin=subprocess.PIPE)
        kill.communicate(input='\n'.join(process_ids).encode('utf-8'))
        if kill.returncode == 0:
            log(ALL, f"Killed processes: {process_ids}")
            return True
        else:
            log(WARNING, f"Failed to kill apt parocess. Return code: {kill.returncode}")
            return False
    except Exception as e:
        log(ERROR, f"An error occurred while killing apt process: {e}")
        return False


'''
Prep function for smake() function.

Input: packages(list of package names)
Output: tuple (list of boolean values, list of package paths)
'''


def run_smake(packages: list) -> tuple:
    smake_out_dir = os.path.join(config.configuration['PKG_DIR'], 'smake_out')
    if not os.path.exists(smake_out_dir):
        os.mkdir(smake_out_dir)
    BUILD_LOG_PATH = os.path.join(config.configuration['OUT_DIR'], "smake_infos")
    if not os.path.exists(BUILD_LOG_PATH):
        os.mkdir(BUILD_LOG_PATH)
    tsvfile = open(
        os.path.join(BUILD_LOG_PATH,
                     'smake_stat_{}.tsv'.format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))),
        'a')
    writer = csv.writer(tsvfile, delimiter='\t')
    writer.writerow(['Package', 'Build Time', 'Error Msg'])
    tsvfile.flush()
    success_list = []
    pkg_path_list = []
    for package in packages:
        package = package.strip()
        PKG_PATH = os.path.join(smake_out_dir, package)
        if not os.path.exists(PKG_PATH):
            os.mkdir(PKG_PATH)
        os.chdir(config.configuration['PKG_DIR'])
        log(ALL, f"Acquiring {package} from Debian ...")
        is_success = smake(package, tsvfile, writer, smake_out_dir)
        pkg_path_list.append(PKG_PATH)
        success_list.append(is_success)
    tsvfile.close()
    log(INFO, "Building is done.")
    return success_list, pkg_path_list


'''
Function that runs data/RQ3/DebianBench/build-deb.sh.
build-deb.sh is a sequence of smake procedures.
smake is a tool that generates .i files from the source code.
Given Makefile of a package, smake extracts all linked files and generates .i files for each executable binary.
This is an essential procedure for Sparrow, the static analyzer.

Input: package(name of the package), 
       tsvfile(file object to write the result), writer(csv.writer object), 
       smake_out_dir(directory to save the smake result), tries(number of tries (default=0))
Output: Boolean (True: Building is successful, False: Building is not successful)
'''


def smake(package: str, tsvfile: TextIO, writer: csv.writer, smake_out_dir: str) -> bool:
    start_time = time.time()
    proc = None
    out = None
    err = None
    BUILD_LOG_PATH = os.path.join(config.configuration['OUT_DIR'], "smake_infos")
    if not os.path.exists(BUILD_LOG_PATH):
        os.mkdir(BUILD_LOG_PATH)
    BUILD_PKG_PATH = os.path.join(BUILD_LOG_PATH, package)
    if not os.path.exists(BUILD_PKG_PATH):
        os.mkdir(BUILD_PKG_PATH)
    try:
        proc = subprocess.Popen(
            [os.path.join(config.configuration['PKG_DIR'], 'build-deb.sh'), package],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        out, err = proc.communicate(timeout=900)
    except subprocess.TimeoutExpired:
        log(ERROR, f"smake for {package} has timed out")
        log(ERROR, f"Failed to build {package} due to timeout.")
        if proc != None:
            proc.kill()
        writer.writerow([package, 'X', 'timeout'])
        tsvfile.flush()
        with open(os.path.join(BUILD_PKG_PATH, package + '_time_summary.txt'), 'w') as f:
            end_time = time.time()
            f.write(f"Start Time: {datetime.datetime.fromtimestamp(start_time)}\n")
            f.write(f"End Time: {datetime.datetime.fromtimestamp(end_time)}\n")
            f.write(f"Time Elapsed: {datetime.timedelta(seconds=end_time - start_time)}\n")
            f.write(f"TimeOut occurred at {datetime.datetime.now()}")
        with open(os.path.join(BUILD_PKG_PATH, package + '_build_log.txt'), 'w') as f:
            if out != None:
                f.write(out.decode('utf-8'))
            if err != None:
                f.write(err.decode('utf-8'))
    except Exception as e:
        log(ERROR, e)
        if proc != None:
            proc.kill()
        try:
            with open(os.path.join(BUILD_PKG_PATH, package + '_time_summary.txt'), 'w') as f:
                f.write(f"Start Time: {datetime.datetime.fromtimestamp(start_time)}\n")
                f.write(f"End Time: {datetime.datetime.fromtimestamp(end_time)}\n")
                f.write(f"Time Elapsed: {datetime.timedelta(seconds=time.time() - start_time)}\n")
                f.write(f"Error occurred at {datetime.datetime.now()}\n")
            with open(os.path.join(BUILD_PKG_PATH, package + '_build_log.txt'), 'w') as f:
                if out != None:
                    f.write(out.decode('utf-8'))
                if err != None:
                    f.write(err.decode('utf-8'))
            log(ERROR, f"smake for {package} has failed")
            parsed_errors = e.stderr.decode('utf-8').split('\n')
            for error in parsed_errors[-10:]:
                log(ERROR, error)
            writer.writerow([package, 'X', parsed_errors[-2]])
            tsvfile.flush()
            return False
        except Exception as e:
            log(ERROR, f"smake for {package} has failed: Unexpected Exit!!")
            log(ERROR, e)
            return False
    if not os.path.exists(BUILD_PKG_PATH):
        os.mkdir(BUILD_PKG_PATH)
    with open(os.path.join(BUILD_PKG_PATH, package + '_time_summary.txt'), 'w') as f:
        end_time = time.time()
        f.write(f"Start Time: {datetime.datetime.fromtimestamp(start_time)}\n")
        f.write(f"End Time: {datetime.datetime.fromtimestamp(end_time)}\n")
        f.write(f"Time Elapsed: {datetime.timedelta(seconds=end_time - start_time)}\n")
    with open(os.path.join(BUILD_PKG_PATH, package + '_build_log.txt'), 'w') as f:
        try:
            if out != None:
                f.write(out.decode('utf-8'))
            if err != None:
                f.write(err.decode('utf-8'))
        except UnicodeDecodeError as e:
            log(ERROR, "could not write {}, due to decoding".format(package + '_build_log.txt'))
    if not check_smake_result(os.path.join(smake_out_dir, package)):
        writer.writerow([
            package, 'X', "build error, find log at {}".format(
                os.path.join(BUILD_PKG_PATH, package + '_build_log.txt'))
        ])
        tsvfile.flush()
        log(ERROR, f"smake for {package} has failed because of no .i files")
        return False
    log(ALL, f"smake for {package} has succeeded")
    writer.writerow([package, 'O', ''])
    log(INFO, f"{package} has .i files!...")
    return True


def print_build_summary(results: tuple) -> None:
    success_list, pkg_path_list = results
    for i, success in enumerate(success_list):
        if success:
            log(
                ALL,
                f"smake for {pkg_path_list[i].split('/')[-1]} was successfully done and saved at {pkg_path_list[i]}."
            )
        else:
            log(WARNING, f"smake was not successful for {pkg_path_list[i]}.")


def print_combine_summary(combine_results: tuple) -> None:
    is_success, packages = combine_results
    if not is_success or len(packages) == 0:
        log(ERROR, f"combine was not successful for {packages}.")
    for package in packages:
        log(ALL, f"{package} was successfully built, and the .c file was saved at {package}.")


def run():
    projects = get_target_list()
    success_list, path_list = run_smake(projects)
    print_build_summary((success_list, path_list))
    print_combine_summary(combine.combine(path_list))
    config.happy_ending(config.configuration["OUT_DIR"])


if __name__ == "__main__":
    config.setup_build()
    run()

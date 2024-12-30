#!/usr/bin/env python3
import config
from logger import log, INFO, ERROR, WARNING, ALL
import os
import subprocess
import re
from pathlib import Path
import csv
import datetime
from typing import TextIO
import time

COMBINE_LOG_PATH = os.path.join(config.configuration['OUT_DIR'], "combine_logs")
COMBINE_TIME_TRACK = []
'''
Separate logging function to record shell stdout and stderr.

Input: String (log path), String (contents (msg))
Output: None
'''


def write_combine_log(log_path: str, contents: str) -> None:
    with open(log_path, 'a') as f:
        f.write(contents)
        f.write('\n')


'''
Function with various filtering strategy
This function makes sure that the filtered candidate is combinable.

Input: String (target path), String (log path), TextIO (tsvfile), csv.writer, String (category), String (package)
Output: bool (True: success, False: fail), String (file name), list of Strings (path list)
'''


def filter_combine_candidate(log_path: str, candidate: str, target_path: str, file_stack: list,
                             tsvfile: TextIO, writer: csv.writer,
                             package: str) -> tuple[bool, str, list]:
    file_path = candidate.split(':')[0]
    full_path = os.path.dirname(os.path.join(target_path, file_path))

    path_split = file_path.split('/')
    if len(path_split) <= 1:
        return False, "", []
    file_name = path_split[-2]
    path_list = []
    for i in range(len(path_split) - 1):
        if path_split[i] == '.libs':
            path_list = path_split[i + 1:-1]
            break
    if path_list == []:
        path_list = path_split[:-1]
    path_list = [package] + path_list
    log(INFO, 'Attempting to filter {}'.format(file_name))
    # strat1
    if 'sparrow' in path_split:
        log(WARNING, f"{file_path} is not a candidate for combining.(sparrow duplicate)")
        write_combine_log(log_path,
                          f"{file_path} is not a candidate for combining.(sparrow duplicate)")
        return False, "", []
    if not re.match(r'^[0-9a-f]{1,3}\.(.*?)\.i$', path_split[-1]):
        log(WARNING, f"{path_split[-1]} is not in the correct format.")
        write_combine_log(log_path, f"{path_split[-1]} is not in the correct format.")
        return False, "", []
    elif file_name in file_stack:
        log(WARNING, f"{file_name} is already combined. Skipping it.")
        write_combine_log(log_path, f"{file_name} is already combined. Skipping it.")
        return False, "", []
    # strat3
    ii_files = [f for f in os.listdir(full_path) if f.endswith(".ii")]
    if len(ii_files) != 0:
        log(ERROR, f".ii(.cpp) files found in {file_name}. Skipping it.")
        write_combine_log(log_path, f".ii(.cpp) files found in {file_name}. Skipping it.")
        writer.writerow([package, '/'.join(path_list), 'X', 'cpp'])
        tsvfile.flush()
        return False, "", []
    if not find_err_files(full_path):
        log(WARNING, f"bin/find_error_file.sh failed. This could cause a problem when combining.")
    return True, file_name, path_list


'''
Function that runs bin/grep.sh script
This is to find main functions in each binary
Some *.i files do not have main functions, and we need to filter them out because Sparrow
cannot analyze main-less program.

Input: String (target path), String (log path), TextIO (tsvfile), csv.writer, String (category), String (package)
Output: bool (True: success, False: fail)
'''


def run_grep_to_find_main(target_path: str, log_path: str, tsvfile: TextIO, writer: csv.writer,
                          package: str) -> tuple[bool, str]:
    os.chdir(target_path)
    command = ["bash", os.path.join(config.configuration["FILE_PATH"], "grep.sh")]
    log(INFO, f"Running {command}.")
    write_combine_log(log_path, f"Running {command}.")
    try:
        result = subprocess.run(command, capture_output=True, check=True)
        output = result.stdout.decode("utf-8").splitlines()
        write_combine_log(log_path, result.stdout.decode("utf-8"))
    except subprocess.CalledProcessError as e:
        log(ERROR, f"Failed to run {command}.")
        log(ERROR, e)
        write_combine_log(log_path, e.stderr.decode("utf-8"))
        writer.writerow([package, 'all', 'X', 'grep error'])
        tsvfile.flush()
        return False, ""
    except Exception as e:
        log(ERROR, f"Failed to run {command}. (unexpected error)")
        log(ERROR, e)
        write_combine_log(log_path, e)
        writer.writerow([package, 'all', 'X', 'unexpected grep error'])
        tsvfile.flush()
        return False, ""
    if output == "":
        log(ERROR, f"main function not found in {package}.")
        write_combine_log(log_path, "main function not found.")
        log(WARNING, f"Skipping {package} ...")
        writer.writerow([package, 'all', 'X', 'grep:no main'])
        tsvfile.flush()
        return False, output
    return True, output


'''
Function that runs bin/combine_pipe.sh script
This script includes 2 main steps:
1) apply 5 different heuristics to get rid of CIL parsing errors (for example, replace const str assignment to strcpy)
2) combine *.i files to one .c file using Sparrow -il option

Input: String (original path (at package/smake_out/), String (file name (without extension)), list of Strings (path list to the file)
Output: bool (True: success, False: fail)
'''


def run_combine_pipeline(orig_path: str, file_name: str, path_list: list) -> bool:
    os.chdir(orig_path)
    path = config.configuration["ANALYSIS_DIR"]
    cnt = 0
    for p in path_list:
        if cnt == 0:
            path = os.path.join(path, '_' + p)
        else:
            path = os.path.join(path, p)
        cnt += 1
        if not os.path.exists(path):
            os.makedirs(path)
    cmd = ["bash", os.path.join(config.configuration["FILE_PATH"], "combine_pipe.sh")]
    try:
        log(INFO, f"Running {cmd}.")
        result = subprocess.run(cmd, capture_output=True, check=True, timeout=900)
    except subprocess.CalledProcessError as e:
        log(ERROR, f"Failed to run {cmd}.")
        log(ERROR, e.stderr.decode("utf-8"))
        return False
    except subprocess.TimeoutExpired as e:
        log(ERROR, f"Failed to run {cmd}. (timeout)")
        return False
    except Exception as e:
        log(ERROR, f"Failed to run {cmd}. (unexpected error)")
        return False
    log(INFO, result.stdout.decode("utf-8"))
    return True


'''
Function that runs bin/find_error_file.sh script
As one of the filtering strategies, we first run CIL parser via Sparrow to find un-parseable files

Input: String (full path of directory where *.i files are)
Output: bool (True: success, False: fail)
'''


def find_err_files(full_path: str) -> bool:
    os.chdir(full_path)
    cmd = ["bash", os.path.join(config.configuration["FILE_PATH"], "find_error_file.sh"), full_path]
    try:
        log(INFO, f"Running {cmd}.")
        reulst = subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        log(ERROR, f"Failed to run {cmd}.")
        log(ERROR, e.stderr.decode("utf-8"))
        return False
    except Exception as e:
        log(ERROR, f"Failed to run {cmd}. (unexpected error)")
        return False
    return True


'''
Function that controls the whole process of combining *.i files into .c files
This process is needed to generate one Cil file (.c) that can be analyzed by Sparrow
and diff-computable by Patron.
This process consists of 3 steps:
1) Find separate binaries that can be combined (shown as *.i files -> contains linked files for each binary)
2) Filter all the un-combinable *.i files (.ii is cpp, and some formats are unstable. We put various heuristics to filter them out.)
3) Combine the binaries into one file using Sparrow -il option (CIL Parser)
This function is kept unfunctional and long to keep in mind that the filtering strategies are supposed to be in this order.
Here, the package top directory name has _(underscore) prefix to avoid conflict with the original package name.

Input: list of tuples (category, package)
Output: bool (True: success, False: fail) and list of Strings (success packages)
'''


def combine(package_paths: list) -> tuple[bool, list]:
    global COMBINE_LOG_PATH, COMBINE_TIME_TRACK
    start_time = time.time()
    COMBINE_TIME_TRACK = []
    success_packages = []
    COMBINE_LOG_PATH = os.path.join(config.configuration['OUT_DIR'], "combine_logs")
    if not os.path.exists(COMBINE_LOG_PATH):
        os.mkdir(COMBINE_LOG_PATH)
    tsvfile = open(
        os.path.join(COMBINE_LOG_PATH, '{}_combine_stat.tsv'.format(
            datetime.datetime.now().strftime("%Y%m%d%H%M%S"))), 'a')
    writer = csv.writer(tsvfile, delimiter='\t')
    writer.writerow(['Package', 'File', 'Combined', 'Note'])
    tsvfile.flush()
    out_dir = config.configuration["ANALYSIS_DIR"]
    pkg_success_cnt = 0
    for package_path in package_paths:
        package = package_path.split('/')[-1]
        COMBINE_PKG_PATH = os.path.join(COMBINE_LOG_PATH, package)
        if not os.path.exists(COMBINE_PKG_PATH):
            os.mkdir(COMBINE_PKG_PATH)
        file_info = dict()
        log_path = os.path.join(COMBINE_PKG_PATH, f"{package}_combine_log.txt")
        time_path = os.path.join(COMBINE_PKG_PATH, f"{package}_time_summary.txt")
        log(ALL, f"Beginning to Combine smake results from <{package}> ...")
        if not os.path.exists(package_path):
            log(
                ERROR,
                f"{package_path} does not exist. This is because smake was not run or failed in the previous step"
            )
            writer.writerow([package, 'all', 'X', 'not exist'])
            continue
        is_success, output = run_grep_to_find_main(package_path, log_path, tsvfile, writer, package)
        if not is_success:
            continue
        success_cnt = 0
        file_stack = []
        write_combine_log(log_path, f"Found {len(output)} main functions.")
        for candidate in output:
            write_combine_log(log_path, f"candidates:{candidate}")
            is_success, file_name, path_list = filter_combine_candidate(
                log_path, candidate, package_path, file_stack, tsvfile, writer, package)
            if is_success:
                file_info[file_name] = (os.path.join(
                    package_path, '/'.join(candidate.split(':')[0].split('/')[:-1])), path_list)
                file_stack.append(file_name)
        log(INFO,
            f"{len(output)} main functions got filtered down to {len(file_stack)} candidates.")
        filter_end_time = time.time()
        write_combine_log(time_path, f"Start Time: {datetime.datetime.fromtimestamp(start_time)}")
        write_combine_log(
            time_path,
            f"{len(file_stack)} binaries are combined.\nFilter Elapsed Time: {datetime.timedelta(seconds=filter_end_time - start_time)}\n"
        )

        for file_name, (orig_path, path_list) in file_info.items():
            if not run_combine_pipeline(orig_path, file_name, path_list):
                writer.writerow([package, '/'.join(path_list), 'X', 'combine error'])
                tsvfile.flush()
                write_combine_log(time_path, f"Combine Error on a binary: {file_name}")
                continue
            end_time = time.time()
            combine_time = datetime.timedelta(seconds=end_time - filter_end_time)
            write_combine_log(time_path, f"Combining {file_name}: {combine_time}\n")
            COMBINE_TIME_TRACK.append(combine_time)
            c_files = [f for f in os.listdir(orig_path) if f.endswith(".c")]
            if len(c_files) == 0:
                log(ERROR, f"No .c file found in {orig_path}.")
                writer.writerow([package, '/'.join(path_list), 'X', 'no .c'])
                tsvfile.flush()
                continue
            log(
                WARNING,
                f"cp {os.path.join(orig_path, c_files[0])} {os.path.join(config.configuration['ANALYSIS_DIR'], '/'.join(path_list), c_files[0])}"
            )
            os.system(
                f"cp {os.path.join(orig_path, c_files[0])} {os.path.join(config.configuration['ANALYSIS_DIR'], '_' + '/'.join(path_list), c_files[0])}"
            )
            # checking strats
            cnt = 0
            for p in path_list:
                if cnt == 0:
                    file_path = os.path.join(config.configuration["ANALYSIS_DIR"], '_' + p)
                else:
                    file_path = os.path.join(file_path, p)
                cnt += 1
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
            c_files = [f for f in os.listdir(file_path) if f.endswith(".c")]
            if len(c_files) == 0:
                log(ERROR, f"No .c file found in {file_path}.")
                writer.writerow([package, '/'.join(path_list), 'X', 'no .c'])
                tsvfile.flush()
                continue
            with open(os.path.join(file_path, c_files[0]), 'r') as f:
                line_cnt = 0
                for line in f:
                    line_cnt += 1
                    if line_cnt >= 3:
                        break
                if line_cnt < 3:
                    log(ERROR, f"Combine error on {c_files[0]}.")
                    writer.writerow([
                        package, '/'.join(path_list), 'X',
                        'Combine Error. Check {}'.format(log_path)
                    ])
                    tsvfile.flush()
                    continue
            log(
                INFO,
                f"Combining {file_name} was successful. The combined .c file is saved at {file_path}."
            )
            writer.writerow([package, '/'.join(path_list), 'O', "-"])
            tsvfile.flush()
            success_cnt += 1
        if success_cnt == 0:
            log(ERROR, f"Failed to combine {package}. No combine was successful.")
            writer.writerow([package, 'all', 'X', 'no success'])
            tsvfile.flush()
            continue
        saved_path = os.path.join(config.configuration["ANALYSIS_DIR"], '_' + package)
        log(ALL, f"Combining {package} was successful. {success_cnt} files were combined.")
        log(ALL, f"Files for {package} are saved at {saved_path}")
        success_packages.append(package)
        tsvfile.flush()
        pkg_success_cnt += 1
    combine_time_sum = 0
    if len(COMBINE_TIME_TRACK) != 0:
        for i in range(len(COMBINE_TIME_TRACK)):
            combine_time_sum += COMBINE_TIME_TRACK[i].total_seconds()
        write_combine_log(
            time_path,
            f"Average Combine Time per binary: {datetime.timedelta(seconds=combine_time_sum / len(COMBINE_TIME_TRACK))}"
        )
    else:
        write_combine_log(time_path, "No binary was combined.")
    write_combine_log(
        time_path, f"Total Elapsed Time: {datetime.timedelta(seconds=time.time() - start_time)}")
    COMBINE_TIME_TRACK = []
    tsvfile.close()
    if pkg_success_cnt == 0:
        log(ERROR, "No package was combined.")
        return False, []
    return True, saved_path

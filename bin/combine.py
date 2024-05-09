#!/usr/bin/env python3
import config
from logger import log, INFO, ERROR, WARNING
import os
import subprocess
import re
from pathlib import Path
import csv
import datetime

def run_combine_pipeline():
    cmd = ["bash", os.path.join(config.configuration["FILE_PATH"], "combine_pipe.sh")]
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        log(ERROR, f"Failed to run {cmd}.")
        log(ERROR, e.stderr.decode("utf-8"))
        return False
    except Exception as e:
        log(ERROR, f"Failed to run {cmd}. (unexpected error)")
        return False
    return True
    

def find_err_files():
    cmd = ["bash", os.path.join(config.configuration["FILE_PATH"], "find_error_file.sh")]
    try:
        reulst = subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        log(ERROR, f"Failed to run {cmd}.")
        log(ERROR, e.stderr.decode("utf-8"))
        return False
    except Exception as e:
        log(ERROR, f"Failed to run {cmd}. (unexpected error)")
        return False
    return True
    

def run(tups):
    tsvfile = open(os.path.join(config.configuration['OUT_DIR'], 'combine_stat_{}.tsv'.format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))), 'a')
    writer = csv.writer(tsvfile, delimiter='\t')
    writer.writerow(['Category', 'Package',	'Combined', 'Note'])
    tsvfile.flush()
    out_dir = config.configuration["ANALYSIS_DIR"]
    success_cnt = 0
    for category, package in tups:
        reason = ""
        target_path = os.path.join(config.configuration["I_FILES_DIR"], category, package)
        log(INFO, f"Combining {package} of {category} category ...")
        if not os.path.exists(target_path):
            log(ERROR, f"{target_path} does not exist.")
            writer.writerow([category, package, 'X', 'not exist'])
            continue
        os.chdir(target_path)
        command = ["bash", os.path.join(config.configuration["FILE_PATH"], "grep.sh")]
        try:
            result = subprocess.run(command, capture_output=True, check=True)
            output = result.stdout.decode("utf-8").splitlines()         
        except subprocess.CalledProcessError as e:
            log(ERROR, f"Failed to run {command}.")
            log(ERROR, e.stderr.decode("utf-8"))
            writer.writerow([category, package, 'X', 'grep error'])
            tsvfile.flush()
            continue
        except Exception as e:
            log(ERROR, f"Failed to run {command}. (unexpected error)")
            writer.writerow([category, package, 'X', 'unexpected error'])
            tsvfile.flush()
            continue
            
        if output == "":
            log(ERROR, f"main function not found in {package}.")
            log(WARNING, f"Skipping {package} ...")
            writer.writerow([category, package, 'X', 'no main'])
            tsvfile.flush()
            continue
        file_stack = []
        dir_stack = []
        success_cnt = 0
        for candidate in output:
            file_path = candidate.split(':')[0]
            dir_path = os.path.dirname(os.path.join(target_path, file_path))
            file_name = file_path.split('/')[-1] if '/' in file_path else "."
            if file_name != ".":
                dir_name = file_path.split('/')[-2]
            if not re.match(r'^[0-9a-f]{1,3}\.(.*?)\.i$', file_name):
                log(WARNING, f"{file_name} is not in the correct format.")
                continue
            elif dir_name in dir_stack:
                log(WARNING, f"{dir_name} is already combined.")
                continue
            dir_stack.append(dir_name)
            os.chdir(dir_path)
            # list all files in the directory and check if it has any file that ends with .ii files, other do not matter.
            files = os.listdir()
            ii_files = [f for f in files if f.endswith(".ii")]
            if len(ii_files) != 0:
                log(ERROR, f".ii files found in {dir_name}.")
                writer.writerow([category, package, 'X', 'cpp'])
                tsvfile.flush()
                continue
            if not find_err_files():
                dir_stack.remove(dir_name)
                continue
            if not run_combine_pipeline():
                dir_stack.remove(dir_name)
                continue
            log(INFO, f"Combining {dir_name} was successful.")
            success_cnt += 1
        if success_cnt == 0:
            log(ERROR, f"Failed to combine {package}.")
            writer.writerow([category, package, 'X', 'no success'])
            tsvfile.flush()
            continue
        os.chdir(out_dir)
        package_out = os.path.join(out_dir, package)
        if not os.path.exists(package_out):
            os.makedirs(package_out)
        for dir_name in dir_stack:
            if dir_name == package:
                continue
            # check if mv is successful
            result = subprocess.run(["mv", dir_name, package_out])
            if result.returncode != 0:
                log(ERROR, f"Failed to move {dir_name} to {package_out}.")
                continue
        writer.writerow([category, package, 'O', "-"])
        log(INFO, f"Combining {package} was successful. {success_cnt} files were combined.")
        tsvfile.flush()
        success_cnt += 1
    tsvfile.close()
    if success_cnt == 0:
        log(ERROR, "No package was combined.")
        return False
    return True
        

def process_top_level_call(dirs):
    if dirs == ["all"]:
        log(ERROR, "Combining all packages is not supported yet.")
        exit(1)
    tups = []
    for dir_path in dirs:
        if not os.path.exists(os.path.abspath(dir_path)):
            log(ERROR, f"{dir_path} does not exist.")
            continue
        sp = dir_path.split('/')
        if sp[-1].strip() == "":
            package = sp[-2]
            category = sp[-3]
        else:
            package = sp[-1]
            category = sp[-2]
        tups.append((category, package))
    return tups

def combine_pipe(dirs):
    tups = process_top_level_call(dirs)
    if tups == []:
        log(ERROR, "No valid package found.")
        return False
    return run(tups)
    
def oss_main():
    run(process_top_level_call(config.configuration["ARGS"].combine))

def main():
    config.setup("COMBINE")
    with open(config.configuration["ARGS"].file, 'r') as f:
        # file must be in category\tpackage format
        packages = f.readlines()
        tups = []
        for package in packages:
            package = package.split('\t')
            package = (package[0].strip(), package[1].strip())
            tups.append(package)
    run(tups)
    
if __name__ == '__main__':
    main()
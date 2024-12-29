#!/usr/bin/env python3
import sys
import os
import subprocess
import csv
import logger
from logger import log, INFO, ERROR, WARNING
import config

FILE_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.abspath(os.path.join(FILE_PATH, '..'))

# def recursive_search(package_map):
#     remove_list = []
#     is_clean = True
#     for i in range(len(package_map)):
#         package, target_dir = package_map[i]
#         for j in range(i+1, len(package_map)):
#             package2, target_dir2 = package_map[j]
#             if target_dir == target_dir2:
#                 log(INFO, f"Found duplicate package: {package} and {package2}")
#                 remove_list.append((package2, target_dir2))
#                 is_clean = False
#         if remove_list != []:
#             break
#     for package, target_dir in remove_list:
#         package_map.remove((package, target_dir))
#     if is_clean:
#         return package_map
#     return recursive_search(package_map)


def find_duplicate(package_map, package, target_dir):
    for p, t in package_map:
        if t == target_dir:
            log(INFO, f"Found duplicate package: {package} and {p}")
            log(INFO, f"previously: {target_dir}\tDuplicated: {t}")
            return True
    return False


'''
Function that checks duplicate packages in the package list
It follows the following steps:
1) Run apt source for each package in the package list
2) Check if the source directory is the same for two packages
3) If the source directory is the same, remove one of the packages
4) Write the updated package list to the file
Input: List of File Names
Output: None
'''


def run(package_lists):
    OUT_DIR = os.path.join(FILE_PATH, '..', 'out')
    LIST_DIR = os.path.join(FILE_PATH, '..', 'package', "debian_lists")
    for package_list in package_lists:
        with open(package_list, 'r') as f:
            packages = f.readlines()
        package_map = []
        packages = [x.strip() for x in packages]
        tmp_dir = os.path.join(FILE_PATH, 'tmp_dir')
        if os.path.exists(tmp_dir):
            os.system('rm -rf ' + tmp_dir)
        os.mkdir(tmp_dir)
        os.chdir(tmp_dir)
        out = open(os.path.join(ROOT_PATH, package_list.replace('.txt', '_dups.txt')), 'w')
        work_size = len(packages)
        cnt = 0
        for package in packages:
            cnt += 1
            log(INFO, f"Processing {package} ({cnt}/{work_size})")
            try:
                proc = subprocess.run(['apt', 'source', package], cwd=tmp_dir, check=True)
                if proc.returncode != 0:
                    log(ERROR, f"Failed to run apt source for {package}.")
                    if proc.stdout:
                        log(ERROR, proc.stdout)
                    if proc.stderr:
                        log(ERROR, proc.stderr)
                    continue
                ls = os.listdir()
                target_dir = None
                for l in ls:
                    if os.path.isdir(l):
                        target_dir = l
                        break
                if target_dir is None:
                    log(ERROR, f"Failed to find source directory for {package}.")
                    continue
                is_duplicate = find_duplicate(package_map, package, target_dir)
                if is_duplicate:
                    log(INFO, f"Found duplicate package: {package}")
                    os.system('rm -rf *')
                    continue
                log(INFO, f"{package}\t{target_dir}")
                package_map.append((package, target_dir))
                os.system('rm -rf *')
                log(INFO, f"Finished apt source for {package}.")
                out.write(f"{package}\t{target_dir}\n")
                out.flush()
            except Exception as e:
                log(ERROR, e)
                os.chdir(tmp_dir)
                os.system('rm -rf *')
                continue
    out.close()


# TODO: use config.setup
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python find_duplicate_pkg.py <package_list1.txt> <package_list2> <package_list3> ..."
        )
        sys.exit(1)
    logger.logger = config.__get_logger("FIND_DUPS")
    package_list = sys.argv[1:]
    run(package_list)

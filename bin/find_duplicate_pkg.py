#!/usr/bin/env python3
import sys
import os
import subprocess
import csv

FILE_PATH = os.path.dirname(os.path.abspath(__file__))
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
        with open(os.path.join(LIST_DIR, package_list), 'r') as f:
            packages = f.readlines()
        package_map = []
        try:
            packages = [x.strip() for x in packages]
            tmp_dir = os.path.join(FILE_PATH, 'tmp_dir')
            if os.path.exists(tmp_dir):
                os.system('rm -rf '+ tmp_dir)
            os.mkdir(tmp_dir)    
            os.chdir(tmp_dir)
            for package in packages:
                proc = subprocess.run(['apt', 'source', package], cwd=tmp_dir, check=True)
                if proc.returncode != 0:
                    print(f"Failed to run apt source for {package}.")
                    continue
                ls = os.listdir()
                target_dir = None
                for l in ls:
                    if os.path.isdir(l):
                        target_dir = l
                        break
                package_map.append((package, target_dir))
                os.system('rm -rf *')
        except Exception as e:
            os.system('rm -rf '+ tmp_dir)    
        os.system('cp '+ os.path.join(LIST_DIR, package_list) + ' ' + os.path.join(LIST_DIR, 'ORIG_' + package_list))
        with open(os.path.join(LIST_DIR, package_list), 'w') as f:
            for package, target_dir in package_map:
                for package2, target_dir2 in package_map:
                    if target_dir == target_dir2:
                        package_map.remove((package2, target_dir2))
            for package, target_dir in package_map:
                f.write(f"{package}\n")
            
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python find_duplicate_pkg.py <package_list1.txt> <package_list2> <package_list3> ...")
        sys.exit(1)
    package_list = sys.argv[1:]
    run(package_list)
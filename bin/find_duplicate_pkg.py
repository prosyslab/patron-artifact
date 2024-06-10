#!/usr/bin/env python3
import sys
import os
import subprocess
import csv

FILE_PATH = os.path.dirname(os.path.abspath(__file__))

def run(package_list):
    OUT_DIR = os.path.join(FILE_PATH, '..', 'out')
    with open(package_list, 'r') as f:
        packages = f.readlines()
    package_map = []
    try:
        packages = [x.strip() for x in packages]
        tmp_dir = os.path.join(FILE_PATH, 'tmp_dir')
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
        
    with open(os.path.join(OUT_DIR, 'package_map.tsv'), 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        for package, target_dir in package_map:
            writer.writerow([package, target_dir])
            print(f"{package}\t{target_dir}")
        writer.writerow([''])
        for package, target_dir in package_map:
            for package2, target_dir2 in package_map:
                if target_dir == target_dir2:
                    print(f"{package} and {package2} have the same target directory {target_dir}")
                    writer.writerow([package])
            
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python find_duplicate_pkg.py <package_list.txt>")
        sys.exit(1)
        
    package_list = sys.argv[1]
    run(package_list)
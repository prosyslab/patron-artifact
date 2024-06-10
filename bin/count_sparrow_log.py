#!/usr/bin/env python3
import csv
import os
import sys


def run(log_dir):
    if not os.path.exists(log_dir):
        print(f"{log_dir} does not exist.")
        sys.exit(1)

    files = os.listdir(log_dir)

    success_lst = []
    for file in files:
        is_success = False
        with open(os.path.join(log_dir, file), 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                if row[1] == 'O':
                    is_success = True
                    break
        if is_success:
            fname = file.split('_sparrow_stat')[0]
            success_lst.append(fname)
    
    with open(os.path.join(log_dir, 'success_list.txt'), 'w') as f:
        for name in set(success_lst):
            f.write(name + '\n')
            
    
            
            
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python count_sparrow_log.py <sparrow_log_dir>")
        sys.exit(1)

    log_dir = sys.argv[1]
    run(log_dir)
    
    
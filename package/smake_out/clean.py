# !/usr/bin/env python3
import os

script_dir = os.path.dirname(os.path.realpath(__file__))
done_list = os.path.join(script_dir, 'done_list.txt')

with open(done_list, 'r') as f:
    done_files = f.readlines()
    done_files = ['/'.join(file.split('\t')).strip() for file in done_files]
    for file in done_files:
        if os.path.exists(file):
            os.system(f'rm -rf {file}')
            print(f"Removed {file}")
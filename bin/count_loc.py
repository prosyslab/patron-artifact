#!/usr/bin/env python3
import sys
import os

def run(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    loc = 0
    for line in lines:
        if not '#line' in line:
            loc += 1
    

def find_file_path(target_dir, file_name):
    for root, dirs, files in os.walk(target_dir):
        if file_name in files:
            return os.path.join(root, file_name)
    return None

def parse_file_list(file_list_path):
    with open(file_list_path, 'r') as f:
        lines = f.readlines()
    for i in range(len(lines)):
        lines[i] = lines[i].strip()
        if not lines[i].endswith('.c'):
            lines[i] += '.c'
    return lines

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 count_loc.py <target_dir_path> <file_list.txt>")
        sys.exit(1)
    if os.path.exists(sys.argv[1]):
        print("Directory path exists")
        exit(0)
    elif os.path.exists(sys.argv[2]):
        print("File path exists")
        exit(0)
        
    files = parse_file_list(sys.argv[2])
    for file in files:
        path = find_file_path(sys.argv[1], file)
        if path is None:
            print("File not found: ", file)
            continue
        run(path)
    
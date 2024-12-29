#!/usr/bin/env python3
import sys
import os

if len(sys.argv) != 3:
    print("Usage: continue.py <out_dir> <target_dir>")
    sys.exit(1)

if sys.argv[1] == "-h" or sys.argv[1] == "--help":
    print("Usage: continue.py <out_dir> <target_dir>")
    sys.exit(1)

out_dir = sys.argv[1]
if not os.path.exists(out_dir):
    print("Directory not found: " + out_dir)
    sys.exit(1)
target_dir = sys.argv[2]
if not os.path.exists(target_dir):
    print("Directory not found: " + target_dir)
    sys.exit(1)

done_list = []
for f in os.listdir(out_dir):
    if f == "stat" or f.endswith(".txt"):
        continue
    with open(os.path.join(out_dir, f, "donee_path.txt"), "r") as p:
        path = p.read().strip()
        done_list.append(path)

for f in os.listdir(target_dir):
    for d in done_list:
        if f in d:
            print("Removing: " + d)
            os.system("rm -rf " + d)

with open(os.path.join(target_dir, "done_list.txt"), "a") as s:
    for d in done_list:
        s.write(d + "\n")

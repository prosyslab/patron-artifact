#!/usr/bin/env python3
import sys, os, datetime, subprocess, time

ALL=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
BENCHMARK_PATH=os.path.abspath(os.path.dirname(__file__))
OUT_DIR=os.path.join(BENCHMARK_PATH, "log")

def check_input():
    if len(sys.argv) < 2:
        print("Usage: python3 reproduce.py <id>\n")
        input("reproducing every benchmarks ... \nPress Enter to continue...")
        id = ALL
    else: 
        id = sys.argv[1:]
    for i in id:
        if not i.isdigit():
            print("Error: id should be integer, but got %s" % i)
            sys.exit(1)
    return id

def parse_config(config):
    fields = dict()
    with open(config, "r") as f:
        lines = f.readlines()
    for line in lines:
        val = line.split("=")
        fields[val[0]] = val[1]
    bin = fields["binary"].strip()
    exploit = fields["exploit"].strip()
    cmd = fields["cmd"].replace("<exploit>", exploit).strip()
    cmd = bin + " " + cmd
    return cmd.split(" ")

def reproduce(id, f=None):
    for i in id:
        if f is None:
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@BENCHMARK-{}@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@".format(i))
        else:
            f.write("================================{}================================\n".format(i))
        if os.path.exists(os.path.join(BENCHMARK_PATH, str(i), "config")):
            cmd = parse_config(os.path.join(BENCHMARK_PATH, str(i), "config"))
            if f is None:
                proc = subprocess.run(cmd)
            else:
                proc = subprocess.run(cmd, stdout=f, stderr=f)
def main():
    id = check_input()
    if len(sys.argv) == 2:
        reproduce(id)
    else:
        if not os.path.isdir(OUT_DIR):
            os.mkdir(OUT_DIR)
        with open(os.path.join(BENCHMARK_PATH, "reproduce-" + str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
                            + ".txt"), "w") as f:
            reproduce(id, f)
        
                


main()
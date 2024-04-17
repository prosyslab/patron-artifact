#!/usr/bin/env python3
import os
import sys
import subprocess
import oss_exp

FILE_PATH = os.path.dirname(os.path.realpath(__file__))
BIN_PATH = os.path.dirname(FILE_PATH)
ROOT_PATH = os.path.dirname(BIN_PATH)
BENCHMARK_EXP_PATH = os.path.join(ROOT_PATH, 'patron-experiment')
BENCHMARK_EXP_BIN_PATH = os.path.join(BENCHMARK_EXP_PATH, 'bin')
BENCHMARK_EXP_SCRIPT_PATH = os.path.join(BENCHMARK_EXP_BIN_PATH, 'experiment.sh')
OSS_EXPERIMENT = 1
BENCHMARK_EXPERIMENT = 2

def openings():
    print('______  ___ ___________ _____ _   _ ')
    print('| ___ \/ _ \_   _| ___ \  _  | \ | |')
    print('| |_/ / /_\ \| | | |_/ / | | |  \| |')
    print('|  __/|  _  || | |    /| | | | . ` |')
    print('| |   | | | || | | |\  \\ \_/ / |\  |')
    print('\_|   \_| |_/\_/ \_| \_|\___/\_| \_/\n')
    print('                             v.0.0.1')
    print('                by prosys lab, KAIST\n')

def oss_experiment():
    print("You have chosen OSS experiment")
    oss_exp.run_full()
    
def benchmark_experiment():
    print("You have chosen benchmark experiment")
    if not os.path.exists(BENCHMARK_EXP_SCRIPT_PATH):
        print("Experiment file not found")
        sys.exit(1)
    os.chdir(BENCHMARK_EXP_PATH)
    status = subprocess.run([BENCHMARK_EXP_SCRIPT_PATH])

def check_input():
    if len(sys.argv) != 2:
        usage()
        sys.exit(1)
    if len(sys.argv) == 1:
        return 0
    if sys.argv[1] == '-oss':
        return OSS_EXPERIMENT
    elif sys.argv[1] == '-benchmark':
        return BENCHMARK_EXPERIMENT
    
def choose_experiment():
    target_experiment = check_input()
    if target_experiment == 0:
        target_experiment = input("Choose the experiment to run: \n\t1. OSS Experiment\n\t2. Benchmark Experiment\nEnter exit to quit")
        if target_experiment == '1' or target_experiment == 'OSS Experiment':
            return OSS_EXPERIMENT
        elif target_experiment == '2' or target_experiment == 'Benchmark Experiment':
            return BENCHMARK_EXPERIMENT
        elif target_experiment == 'exit':
            sys.exit(0)
        else:
            print("Invalid input. Please try again.")
            choose_experiment()
    else:
        return target_experiment
        
            
def usage():
    print("Usage: ./run.py [-oss | -benchmark | -help]")

def main():
    openings()
    experiment = choose_experiment()
    if experiment == OSS_EXPERIMENT:
        oss_experiment()
    elif experiment == BENCHMARK_EXPERIMENT:
        benchmark_experiment()

if __name__ == '__main__':
    main()

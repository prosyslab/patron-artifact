#!/usr/bin/env python3
import os
import sys
import subprocess
import oss_exp
import patron
import config

FILE_PATH = os.path.dirname(os.path.realpath(__file__))
BIN_PATH = os.path.dirname(FILE_PATH)
ROOT_PATH = os.path.dirname(BIN_PATH)
BENCHMARK_EXP_PATH = os.path.join(ROOT_PATH, 'patron-experiment')
BENCHMARK_EXP_BIN_PATH = os.path.join(BENCHMARK_EXP_PATH, 'bin')
BENCHMARK_EXP_SCRIPT_PATH = os.path.join(BENCHMARK_EXP_BIN_PATH, 'experiment.sh')
OSS_EXPERIMENT = 1
BENCHMARK_EXPERIMENT = 2

def print_help() -> None:
    print("Usage: ./run.py [-oss | -benchmark | -help]")
    print("\nOptions:")
    print("\t-oss: Run OSS experiment(Corresponding to the Experiment 4 in the paper)")
    print("\t-benchmark: Run benchmark experimentBenchmark Experiment(Experiment 1, 2, 3)")
    print("\t-help: Display this help message")
    print("\n\t Checkout README.md for more information on low level executions.")

def usage() -> None:
    print("Usage: ./run.py [-oss | -benchmark | -help]")
    
'''
Function that runs /bin/oss_exp.py
Target debian list is default settings if run from here
Otherwise, consider running from oss.exp.py
This corresponds to RQ3 in the paper

Input: None
Output: None
'''
def oss_experiment() -> None:
    print("You have chosen OSS experiment")
    oss_exp.run_full_pipe()
    
'''
Function that runs /patron-experiment/bin/experiment.sh
This corresponds to RQ1 and RQ2 in the paper

Input: None
Output: None
'''
def benchmark_experiment() -> None:
    print("You have chosen benchmark experiment")
    if not os.path.exists(BENCHMARK_EXP_SCRIPT_PATH):
        print("Experiment file not found")
        sys.exit(1)
    os.chdir(BENCHMARK_EXP_PATH)
    status = subprocess.run([BENCHMARK_EXP_SCRIPT_PATH])
    
'''
Function that checks command line arguments
If nothing is given, it enters user-interaction mode

Input: None
Output: int (1: OSS Experiment, 2: Benchmark Experiment, 0: Nothing given)
'''
def check_cli_input() -> int:
    if len(sys.argv) > 2:
        usage()
        sys.exit(1)
    if len(sys.argv) == 1:
        return 0
    if sys.argv[1] == '-oss':
        return OSS_EXPERIMENT
    elif sys.argv[1] == '-benchmark':
        return BENCHMARK_EXPERIMENT
    elif sys.argv[1] == '-help':
        print_help()
        sys.exit(0)
    else:
        usage()
        sys.exit(1)
        
'''
Function that checks command line arguments
If nothing is given, it enters user-interaction mode

Input: None
Output: int (1: OSS Experiment, 2: Benchmark Experiment)
'''
def choose_experiment() -> int:
    target_experiment = check_cli_input()
    if target_experiment == 0:
        target_experiment = input("Choose the experiment to run: \n\t1. OSS Experiment(Corresponding to the Experiment 4 in the paper)\n\t2. Benchmark Experiment(Experiment 1, 2, 3)\nEnter exit to quit")
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
        

def main():
    config.openings()
    experiment = choose_experiment()
    if experiment == OSS_EXPERIMENT:
        oss_experiment()
    elif experiment == BENCHMARK_EXPERIMENT:
        benchmark_experiment()

if __name__ == '__main__':
    main()

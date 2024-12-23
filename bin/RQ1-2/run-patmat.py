#!/usr/bin/env python3
import argparse
import os
import datetime
import subprocess
import logging

PROJECT_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
PATRON_BIN = os.path.join(PROJECT_HOME, 'patron', 'patron')
timestamp = ''

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S",
    filemode='w',
    filename=os.path.join(PROJECT_HOME, "run-patmat.log"))


def init(args):
    global timestamp
    if args.timestamp:
        timestamp = args.timestamp
    else:
        timestamp = datetime.date.today().strftime('%Y%m%d-%H:%M:%S')


def run(WORK_DIR):
    WORK_DIR = os.path.abspath(WORK_DIR)
    run_patron = subprocess.run([PATRON_BIN, WORK_DIR])
    run_patron.check_returncode()


def main():
    parser = argparse.ArgumentParser(description='Bug Pattern Matching Test')
    parser.add_argument('WORK_DIR', required=True, type=str)
    parser.add_argument('-t', '--timestamp', type=str)
    args = parser.parse_args()
    init(args)
    run(args.WORK_DIR)

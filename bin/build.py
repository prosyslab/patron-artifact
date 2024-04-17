#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import config
from logger import log, INFO, ERROR, WARNING

BIN_DIR = os.path.dirname(os.path.realpath(__file__))
PKG_DIR = os.path.dirname(BIN_DIR) + '/pkg'
PKG_LIST = ""

def get_debian_packages():
    global PKG_LIST
    log(INFO, "Retrieving the list of Debian packages from web ...")
    PKG_LIST = os.path.join(PKG_DIR, 'debian_packages.txt')
    if not os.path.exists(PKG_LIST):
        status = subprocess.run(
            [sys.executable,
            os.path.join(PKG_DIR, 'debian_crawler.py')],
            check=True)
        if status.returncode != 0:
            log(ERROR, "Failed to retrieve the list of packages.")
            exit(1)
        retry_cnt = 0
        while os.path.exists(os.path.join(PKG_DIR, 'debian_packages.txt')):
            retry_cnt += 1
            log(WARNING, "Waiting for the file to be created. (Retry: {})".format(retry_cnt))
            time.sleep(5)
        log(INFO, "Package List ({}) is created.".format(PKG_LIST))
    else:
        log(INFO,"Package List ({}) already exists.".format(os.path.join(PKG_DIR, 'debian_packages.txt')))

def smake():
    if len(config.configuration["ARGS"].build) == 0 or config.configuration["ARGS"].build[0] == "None":
        get_debian_packages()
    if PKG_LIST == "":
        packages = config.configuration["ARGS"].build
    if not os.path.exists(os.path.join(PKG_DIR, 'i_files')):
        os.mkdir(os.path.join(PKG_DIR, 'i_files'))
    with open(os.path.join(PKG_DIR, 'debian_packages.txt'), 'r') as f:
        packages = f.readlines()
        os.chdir(PKG_DIR)
        for package in packages:
            package = package.strip()
            log(INFO, f"Building {package} ...")
            try:
                status = subprocess.run([os.path.join(PKG_DIR, 'build-deb.sh'), package],
                                    check=True)
            except subprocess.CalledProcessError as e:
                log(ERROR, f"building {package} has failed")
                log(ERROR, e.stderr)
            else:
                log(INFO, f"building {package} has succeeded")
def run():
    smake()

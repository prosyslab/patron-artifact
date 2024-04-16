#!/usr/bin/env python3
import os
import sys
import subprocess
import time

BIN_DIR = os.path.dirname(os.path.realpath(__file__))
PKG_DIR = os.path.dirname(BIN_DIR) + '/pkg'


def main():

    with open(os.path.join(PKG_DIR, 'debian_packages.txt'), 'r') as f:
        packages = f.readlines()
    with open(os.path.join(PKG_DIR, 'build_log.txt'), 'a') as f:
        os.chdir(PKG_DIR)
        for package in packages:
            package = package.strip()
            status = subprocess.run([sys.executable, 'build_deb.sh', package],
                                    check=True)
            if status.returncode != 0:
                f.write(f"{package}\tX")


if __name__ == '__main__':
    main()

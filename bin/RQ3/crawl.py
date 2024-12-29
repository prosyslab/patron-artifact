#!/usr/bin/env python3
from logger import log, ALL, ERROR, WARNING, ALL
from typing import TextIO
import os, config, find_duplicate_pkg, subprocess, sys

LIST_DIR = ""
PKG_DIR = ""

'''
Function that runs package/debian_crawler.py
Check crawl() function for more details

Input: None
Output: Boolean (True: Package list is retrieved, False: Package list is not retrieved)
'''
def get_package_list_from_web() -> bool:
    if os.path.exists(LIST_DIR):
        log(ALL, f"The package list directory already exists at {LIST_DIR}.")
        if 'y' == input("Do you want to delete the directory and crawl again? (y/n) ").lower():
            os.system(f"rm -r {LIST_DIR}")
        else:
            return False
    os.mkdir(LIST_DIR)
    try:
        status = subprocess.run(
            [sys.executable,
            os.path.join(PKG_DIR, 'debian_crawler.py')],
            check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        log(ERROR, "Failed to retrieve the list of packages.")
        log(ERROR, e.stderr.decode('utf-8'))
        config.patron_exit("CRAWL", LIST_DIR)
    if status.returncode != 0:
        log(ERROR, "Failed to retrieve the list of packages.")
        config.patron_exit("CRAWL", LIST_DIR)
    return True

'''
Function that crawls the Debian package list from the bookworm and save them based on the project category.
This function is called when -crawl option is given.
It has two parts:
1) Retrieve the list of Debian packages from web and save them in the package/debian_lists directory
2) Check duplicated packages within each category and remove them
This is because packages with different web names can actually be the same package.
This function prematurely exits if the package list directory already exists.
Delete the directory if you want to crawl again.

Input: None
Output: None
'''
def crawl() -> None:
    log(ALL, "Crawling Debian package list ...")
    log(ALL, "Retrieving the list of Debian packages from web ...")
    if not get_package_list_from_web():
        return
    log(ALL, "Packages are retrieved.")
    # log(ALL, "Checking duplicated packages ...")
    # find_duplicate_pkg.run([os.path.join(LIST_DIR, file) for file in os.listdir(LIST_DIR) if file.endswith(".txt")])
    log(ALL, "Crawling Summary:")
    for file in os.listdir(os.path.join(PKG_DIR, 'crawling_result')):
        if file.endswith(".txt"):
            with open(os.path.join(LIST_DIR, file), 'r') as f:
                log(ALL, f"{file} has {len(f.readlines())} packages.")
    log(ALL, "Package Lists are created at {}.".format(os.path.join(PKG_DIR, 'crawling_result')))
    
if __name__ == "__main__":
    config.setup_crawl()
    LIST_DIR = config.configuration["LIST_DIR"]
    PKG_DIR = config.configuration["PKG_DIR"]
    crawl()
    config.happy_ending(config.configuration["OUT_DIR"])
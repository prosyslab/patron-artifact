#!/usr/bin/env python3
import os
import datetime
import csv
import build
import sparrow
import patron
import config
import combine
import count_sparrow_log
from logger import log, INFO, ERROR, WARNING, ALL
import progressbar
import time

'''
Function that runs build.py->combine.py->sparrow.py in a pipeline
Crawling is not included in the pipeline for convenience.(You can do this with -crawl option)
If -pipe option is not given when run directly on this file, it exits False
Otherwise, this is the default mode, either run from run.py or run from main with -pipe option
In some cases, pipe mode is slower than running each script separately because
single OS can only run apt source command sequentially.
*Target debian list should be given with -pipe option, otherwise, it runs on default settings.

Input: Boolean, String (Both arguments indicate from where this function was called)
Output: Boolean (True: Pipe mode confirmed, False: Pipe mode not confirmed)
'''
def run_preprocess() -> bool:
    packages = build.get_target_list()
    tsvfile = open(os.path.join(config.configuration['OUT_DIR'], 'preprocess_stat_{}.tsv'.format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))), 'a')
    writer = csv.writer(tsvfile, delimiter='\t')
    writer.writerow(['Package', 'Build', 'Sparrow'])
    tsvfile.flush()
    work_size = len(packages)
    work_cnt = 0
    for package in packages:
        work_cnt += 1
        log(ALL, "Working on {}/{} ...".format(work_cnt, work_size))
        package = package.strip()
        is_success, next_args = build.run_smake([package])
        if not is_success[0]:
            writer.writerow([package, 'X', '-'])
            tsvfile.flush()
            continue
        is_success, pkg = combine.combine(next_args)
        if not is_success:
            writer.writerow([package, 'X', '-'])
            tsvfile.flush()
            continue
        sparrow_worklist = sparrow.mk_worklist([pkg])
        sparrow.execute_worklist(sparrow_worklist)
        writer.writerow([package, 'O', 'O'])
        tsvfile.flush()
    tsvfile.close()
    return True

def run_transplantation() -> bool:
    patron.run_patch_transplantation(config.transplant_configuration["DONEE_LIST"])

def run_database_construction() -> bool:
    patron.run_database()
'''
main function chooses which procedure will be run based on the CLI arguments

Input: None
Output: None
'''
def main():
    config.openings()
    purpose = config.setup_main()
    match purpose:
        case "PREP":
            run_preprocess()
        case "TRANS":
            run_transplantation()
        case "DB":
            run_database_construction()
        case _:
            log(ERROR, "Invalid purpose: {}".format(purpose))
            config.bad_ending(config.configuration['OUT_DIR'])
    config.happy_ending(config.configuration["OUT_DIR"])
    
if __name__ == '__main__':
    main()
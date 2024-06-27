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
import measure_time
from logger import log, INFO, ERROR, WARNING
CRWAL_ONLY = 1
BUILD_ONLY = 2
COMBINE_ONLY = 3
SPARROW_ONLY = 4
PATRON_ONLY = 5
TOP = 6
'''
Function that runs build.py->combine.py->sparrow.py->patron.py in a pipeline.
If you want to reproduce the experimental results, you can use this function.
However, to experiment on various debian software packages, 
This mode is not recommended because there exists a bottleneck in the apt source command.
Since this mode does everything in a single process, it does not need an input arg.

Input: None
Output: Boolean (True: success, False: fail)
'''
def run_full_pipe() -> bool:
    pass

'''
Function that runs build.py->combine.py->sparrow.py in a pipeline.
The purpose of the pipeline is to keep the analysis results, because analysis is an expensive process.
Crawling is not included in the pipeline for convenience.(You can do this with -crawl option)
If -pipe option is not given when run directly on this file, it exits False
Otherwise, this is the default mode, either run from run.py or run from main with -pipe option
In some cases, pipe mode is slower than running each script separately because
single OS can only run apt source command sequentially.
Input: None
Output: Boolean (True: Pipe mode confirmed, False: Pipe mode not confirmed)
'''
def run_pipe(level, from_top=False) -> bool:
    lv_string = "TOP"
    if level == CRWAL_ONLY:
        lv_string = "CRAWL"
    elif level == BUILD_ONLY:
        lv_string = "BUILD"
    elif level == COMBINE_ONLY:
        lv_string = "COMBINE"
    elif level == SPARROW_ONLY:
        lv_string = "SPARROW"
    elif level == PATRON_ONLY:
        lv_string = "PATRON"
    config.setup(lv_string)
    if not config.configuration["PIPE_MODE"] and not from_top:
        return False
    build.crawl()
    tsvfile = open(os.path.join(config.configuration['OUT_DIR'], 'pipe_stat_{}.tsv'.format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))), 'a')
    writer = csv.writer(tsvfile, delimiter='\t')
    writer.writerow(['Package', 'Build', 'Combine', 'Sparrow','Error Msg'])
    tsvfile.flush()
    packages = build.mk_category_dict()
    smake_out_dir = os.path.join(build.PKG_DIR, 'smake_out')
    if not os.path.exists(smake_out_dir):
        os.mkdir(smake_out_dir)
    work_size = len(packages.keys()) * sum([len(packages[str(category)]) for category in packages.keys()])
    work_cnt = 0
    for category in packages.keys():
        if not os.path.exists(os.path.join(smake_out_dir, str(category))):
            os.mkdir(os.path.join(smake_out_dir, str(category)))
        packages = packages[ str(category) ]
        os.chdir(build.PKG_DIR)
        for package in packages:
            work_cnt += 1
            log(INFO, "Working on {}/{} ...".format(work_cnt, work_size))
            package = package.strip()
            is_success, next_args = build.smake_pipe(str(category), package, tsvfile, writer, smake_out_dir, 0)
            if not is_success:
                continue
            is_success = combine.combine_pipe(next_args, tsvfile, writer)
            if not is_success:
                continue
            is_success = sparrow.sparrow_pipe(pkgs[0], tsvfile, writer)
            if not is_success:
                continue
            writer.writerow([package, 'O', 'O', 'O', 'O', '-'])
            tsvfile.flush()
    tsvfile.close()
    count_sparrow_log.run(sparrow.SPARROW_LOG_DIR)
    measure_time.run_from_top(config.configuration['OUT_DIR'], measure_time.PIPE_MODE)
    return True
'''
main function chooses which procedure will be run based on the CLI arguments
Input: None
Output: None
'''
def main():
    if config.configuration["CRWAL_ONLY"]:
        run_pipe(CRWAL_ONLY)
    if config.configuration["BUILD_ONLY"]:
        run_pipe(BUILD_ONLY)
    if config.configuration["SPARROW_ONLY"]:
        run_pipe(SPARROW_ONLY)
    if config.configuration["COMBINE_ONLY"]:
        run_pipe(COMBINE_ONLY)
    if config.configuration["PATRON_ONLY"]:
        run_pipe(PATRON_ONLY)            
    if run_pipe(TOP):
        return
    if config.configuration["CRWAL_ONLY"]:
        build.crawl()
    if config.configuration["BUILD_ONLY"]:
        build.smake(0)
    if config.configuration["SPARROW_ONLY"]:
        sparrow.sparrow(config.configuration["SPARROW_TARGET_FILES"])
    if config.configuration["COMBINE_ONLY"]:
        combine.oss_main()
    if config.configuration["SPARROW_ONLY"]:
        sparrow.sparrow("oss", config.configuration["SPARROW_TARGET_FILES"])
    if config.configuration["PATRON_ONLY"]:
        patron.main(True)
    return
    
    
if __name__ == '__main__':
    main()

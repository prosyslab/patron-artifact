#!/usr/bin/env python3
import os
import datetime
import csv
import build
import sparrow
import config
import combine
import count_sparrow_log
import measure_time
from logger import log, INFO, ERROR, WARNING

'''
Function that runs build.py->combine.py->sparrow.py->patron.py in a pipeline
Crawling is not included in the pipeline for convenience.(You can do this with -crawl option)
If -pipe option is not given when run directly on this file, it exits False
Otherwise, this is the default mode, either run from run.py or run from main with -pipe option
In some cases, pipe mode is slower than running each script separately because
single OS can only run apt source command sequentially.
*Target debian list should be given with -pipe option, otherwise, it runs on default settings.

Input: Boolean, String (Both arguments indicate from where this function was called)
Output: Boolean (True: Pipe mode confirmed, False: Pipe mode not confirmed)
'''
def run_pipe(level : str, from_top: bool=False ) -> bool:
    config.setup(level)
    if not config.configuration["PIPE_MODE"] and not from_top:
        return False
    build.crawl()
    tsvfile = open(os.path.join(config.configuration['OUT_DIR'], 'pipe_stat_{}.tsv'.format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))), 'a')
    writer = csv.writer(tsvfile, delimiter='\t')
    writer.writerow(['Package', 'Build', 'Combine', 'Sparrow','Error Msg'])
    tsvfile.flush()
    packages = build.mk_smake_worklist()
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
            assert(False)
            if not is_success:
                continue
            is_success = sparrow.sparrow_pipe(package, tsvfile, writer)
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
    config.openings()
    if config.configuration["CRWAL_ONLY"]:
        run_pipe("CRWAL")
    if config.configuration["BUILD_ONLY"]:
        run_pipe("BUILD")
    if config.configuration["SPARROW_ONLY"]:
        run_pipe("SPARROW")
    if config.configuration["COMBINE_ONLY"]:
        run_pipe("COMBINE")
    if config.configuration["PATRON_ONLY"]:
        run_pipe("PATRON")            
    if run_pipe("TOP"):
        return
    if config.configuration["CRWAL_ONLY"]:
        build.crawl()
    if config.configuration["BUILD_ONLY"]:
        build.run()
    if config.configuration["SPARROW_ONLY"]:
        sparrow.sparrow(config.configuration["SPARROW_TARGET_FILES"])
    if config.configuration["COMBINE_ONLY"]:
        combine.oss_main()
    if config.configuration["PATRON_ONLY"]:
        patron.run(True)
    return
    
    
if __name__ == '__main__':
    main()

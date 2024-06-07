#!/usr/bin/env python3
import os
import datetime
import csv
import build
import sparrow
import config
import combine
from logger import log, INFO, ERROR, WARNING

def run_pipe():
    config.setup("TOP")
    if not config.configuration["PIPE_MODE"]:
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
            is_success = sparrow.sparrow_pipe(package, tsvfile, writer)
            if not is_success:
                continue
            writer.writerow([package, 'O', 'O', 'O', 'O', '-'])
            tsvfile.flush()
    return True
            
def main():
    if run_pipe():
        return
    if config.configuration["CRWAL_ONLY"]:
        build.crawl()
    if config.configuration["BUILD_ONLY"]:
        build.smake(0)
    if config.configuration["SPARROW_ONLY"]:
        sparrow.sparrow(config.configuration["SPARROW_TARGET_FILES"])
    if config.configuration["COMBINE_ONLY"]:
        combine.oss_main()
    # if config.configuration["PATRON_ONLY"]:
    #     patron.run()
    return
    
    
if __name__ == '__main__':
    main()

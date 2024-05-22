#!/usr/bin/env python3
import os
import datetime
import csv
import build
import sparrow
import config
import combine

def run_full():
    config.setup("TOP")
    build.run()
    sparrow.sparrow(config.configuration["SPARROW_TARGET_FILES"])
    patron.run()
    
def run_pipe():
    tsvfile = open(os.path.join(config.configuration['OUT_DIR'], 'pipe_stat_{}.tsv'.format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))), 'a')
    writer = csv.writer(tsvfile, delimiter='\t')
    writer.writerow(['Package', 'Build', 'Combine', 'Sparrow','Error Msg'])
    tsvfile.flush()
    packages = build.mk_category_dict()
    i_files_dir = os.path.join(build.PKG_DIR, 'i_files')
    if not os.path.exists(i_files_dir):
        os.mkdir(i_files_dir)
    for category in packages.keys():
        if not os.path.exists(os.path.join(i_files_dir, str(category))):
            os.mkdir(os.path.join(i_files_dir, str(category)))
        packages = packages[ str(category) ]
        os.chdir(build.PKG_DIR)
        for package in packages:
            package = package.strip()
            is_success, next_args = build.smake_pipe(str(category), package, tsvfile, writer, i_files_dir)
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
            
def main():
    config.setup("TOP")
    if config.configuration["PIPE_MODE"]:
        run_pipe()
        return
    if config.configuration["CRWAL_ONLY"]:
        build.crawl()
    if config.configuration["BUILD_ONLY"]:
        build.smake()
    if config.configuration["SPARROW_ONLY"]:
        sparrow.sparrow(config.configuration["SPARROW_TARGET_FILES"])
    if config.configuration["COMBINE_ONLY"]:
        combine.oss_main()
    # if config.configuration["PATRON_ONLY"]:
    #     patron.run()
    return
    
    
if __name__ == '__main__':
    main()
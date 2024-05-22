#!/usr/bin/env python3
import sys, os, subprocess, datetime
import argparse, logging
# make BENCHMARK_PATH absolute path
BENCHMARK_PATH=os.path.abspath(os.path.dirname(__file__))
BIN_PATH=os.path.join(BENCHMARK_PATH, "..", "..", "bin", "vulnfix")
OUT_DIR=os.path.join(BENCHMARK_PATH, "log")
READY=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]

# parse arguments
parser = argparse.ArgumentParser(description='Run PatchWeave on a benchmark')
parser.add_argument ("purpose", help="build or patch")
parser.add_argument(
        "-id",
        nargs="+",
        default=[],
        help=
        "run specific id(s) of the given benchmark (e.g. -id 1,2,3       (skipping this option will run all ids))",
    )

def __get_logger():
    __logger = logging.getLogger("logger")
    formatter = logging.Formatter("[%(levelname)s][%(asctime)s] %(message)s")
    curr_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    __logger.addHandler(stream_handler)
    if not os.path.isdir(OUT_DIR):
        os.mkdir(OUT_DIR)
    log_name = "log_" + str(curr_time) + ".txt"
    file_handler = logging.FileHandler(
        os.path.join(OUT_DIR, log_name))
    file_handler.setFormatter(formatter)
    __logger.addHandler(file_handler)
    __logger.setLevel(logging.DEBUG)

    return __logger

def mk_worklist(args, logger):
    is_build = args.purpose == "build"
    if is_build:
        logger.info("Configuring for Building benchmark...")
        for id in args.id:
            if int(id) not in READY:
                logger.error("Benchmark id %s is not ready for building" % id)
                sys.exit(1)
        worklist = [(str(id), [os.path.join(BENCHMARK_PATH, str(id), "setup.sh")]) for id in args.id]
    else:
        logger.info("Configuring for Running vulnfix benchmark...")
        for id in args.id:
            if int(id) not in READY:
                logger.error("Benchmark id %s is not ready for patching" % id)
                sys.exit(1)
        worklist = [(str(id), [BIN_PATH, os.path.join(BENCHMARK_PATH, str(id), "config")]) for id in args.id]
    logger.info("Configuration All Set")
    return worklist

def run_parallel(worklist, logger):
    logger.info("Running in parallel...")
    proc_lst = []
    for id, cmd in worklist:
        if os.path.exists(os.path.join(BENCHMARK_PATH, id, "source")):
            logger.info("cleaning up previous build...")
            os.system("rm -rf %s" % os.path.join(BENCHMARK_PATH, id, "source"))
            os.system("rm -rf %s" % os.path.join(BENCHMARK_PATH, id, "runtime"))
            # check if file exists
            if os.path.exists(os.path.join(BENCHMARK_PATH, id, "imginfo")):
                bin = "imginfo"
            if os.path.exists(os.path.join(BENCHMARK_PATH, id, "j2k_to_image")):
                bin = "j2k_to_image"
            if os.path.exists(os.path.join(BENCHMARK_PATH, id, "opj_dump")):
                bin = "opj_dump"
            if os.path.exists(os.path.join(BENCHMARK_PATH, id, "sndfile-convert")):
                bin = "sndfile-convert"
            if os.path.exists(os.path.join(BENCHMARK_PATH, id, "ziptool")):
                bin = "ziptool"
            if os.path.exists(os.path.join(BENCHMARK_PATH, id, "tiff2ps")):
                bin = "tiff2ps"
            if os.path.exists(os.path.join(BENCHMARK_PATH, id, "tiff2pdf")):
                bin = "tiff2pdf"
            if bin is not None:
                os.system("rm %s" % os.path.join(BENCHMARK_PATH, id, bin))
        os.chdir(os.path.join(BENCHMARK_PATH, id))
        logger.info("Running benchmark %s" % id)
        logger.info("Command: %s" % cmd)
        proc = subprocess.Popen(cmd)
        proc_lst.append((id, proc))
    for id, proc in proc_lst:
        proc.wait()
        if proc.returncode != 0:
            logger.error("Benchmark {} failed with return code {}".format(id, proc.returncode))
    
        
def run_sequential(worklist, logger):
    logger.info("Running sequentially...")
    for id, cmd in worklist:
        logger.info("Running benchmark %s" % id)
        logger.info("Command: %s" % cmd)
        proc = subprocess.Popen(cmd)
        proc.wait()
        if proc.returncode != 0:
            logger.error("Benchmark {} failed with return code {}".format(id, proc.returncode))
        

def main():
    logger = __get_logger()
    logger.info("Start running VulnFix on Patchweave benchmark...")
    args = parser.parse_args()
    if args.id == []:
        args.id = READY
    logger.info("TARGET IDs: {}".format(args.id))
    worklist = mk_worklist(args, logger)
    if args.purpose == "build":
        run_parallel(worklist, logger)
    else:
        run_sequential(worklist, logger)
    
if __name__ == "__main__":
    main()
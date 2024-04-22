import os
import argparse
import logger
import logging
import datetime

configuration = {
    "ARGS": None,
    "FILE_PATH": os.path.dirname(os.path.realpath(__file__)),
    "ROOT_PATH": os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    "OUT_DIR": os.path.join(os.path.dirname(os.path.realpath(__file__)), ".." ,"out"),
    "ANALYSIS_DIR": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "pkg", "analysis-target"),
    "SPARROW_BIN_PATH": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "patron-experiment", "sparrow", "bin", "sparrow"),
    "BUILD_ONLY": False,
    "CRWAL_ONLY": False,
    "SPARROW_ONLY": False,
    "CSV_FOR_STAT": False,
    "DEFAULT_SPARROW_OPT": ["-taint", "-unwrap_alloc", "-remove_cast", "-patron", "-extract_datalog_fact_full"],
    "USER_SPARROW_OPT": [],
    "SPARROW_TARGET_FILES": []
}

def __get_logger():
    __logger = logging.getLogger("logger")
    formatter = logging.Formatter("[%(levelname)s][%(asctime)s] %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    __logger.addHandler(stream_handler)
    if not os.path.isdir(configuration["OUT_DIR"]):
        os.mkdir(configuration["OUT_DIR"])
    file_handler = logging.FileHandler(
        os.path.join(configuration["OUT_DIR"], "log_{}.txt".format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))))
    file_handler.setFormatter(formatter)
    __logger.addHandler(file_handler)
    __logger.setLevel(logging.DEBUG)
    return __logger

def oss_usage():
    print("Usage: python3 oss_exp.py [-h] [-build [BUILD [BUILD ...]]] [-crawl] [-sparrow [SPARROW [SPARROW ...]]]")
    print("Options:")
    print("  -h, --help            show this help message and exit")
    print("  -build [BUILD [BUILD ...]], -b [BUILD [BUILD ...]]")
    print("                        build the given path for category list(s) of package only (default:all)")
    print("  -crawl, -c            crawl the package list from the web only")
    print("  -sparrow [SPARROW [SPARROW ...]], -s [SPARROW [SPARROW ...]]")
    print("                        run the sparrow for the given directory(ies) (default:all)")
    print("  -io                  run the sparrow for Integer Overflow (cannot be used without -sparrow or -s)")
    print("  -tio                 run the sparrow for Times Integer Overflow (cannot be used without -sparrow or -s)")
    print("  -pio                 run the sparrow for Plus Integer Overflow (cannot be used without -sparrow or -s)")
    print("  -mio                 run the sparrow for Minus Integer Overflow (cannot be used without -sparrow or -s)")
    print("  -sio                 run the sparrow for Shift Integer Overflow (cannot be used without -sparrow or -s)")
    print("  -dz                  run the sparrow for Division by Zero (cannot be used without -sparrow or -s)")
    print("  -bo                  run the sparrow for Buffer Overflow (cannot be used without -sparrow or -s)")
    return

def sparrow_usage():
    print("Usage: python3 sparrow.py [-h] [-files [FILES [FILES ...]]]"
          "[-io] [-tio] [-pio] [-mio] [-sio] [-dz] [-bo]")
    print("Options:")
    print("  -h, --help            show this help message and exit")
    print("  -files [FILES [FILES ...]], -f [FILES [FILES ...]]")
    print("                        run the sparrow for the given file(s) (default:all)")
    print("  -io                  run the sparrow for Integer Overflow (cannot be used without -sparrow or -s)")
    print("  -tio                 run the sparrow for Times Integer Overflow (cannot be used without -sparrow or -s)")
    print("  -pio                 run the sparrow for Plus Integer Overflow (cannot be used without -sparrow or -s)")
    print("  -mio                 run the sparrow for Minus Integer Overflow (cannot be used without -sparrow or -s)")
    print("  -sio                 run the sparrow for Shift Integer Overflow (cannot be used without -sparrow or -s)")
    print("  -dz                  run the sparrow for Division by Zero (cannot be used without -sparrow or -s)")
    print("  -bo                  run the sparrow for Buffer Overflow (cannot be used without -sparrow or -s)")
    return

def parse_sparrow_opt(parser):
    parser.add_argument("-io", action="store_true", default=False, help="run the sparrow for Integer Overflow (cannot be used without -sparrow or -s)")
    parser.add_argument("-tio", action="store_true", default=False, help="run the sparrow for Times Integer Overflow (cannot be used without -sparrow or -s)")
    parser.add_argument("-pio", action="store_true", default=False, help="run the sparrow for Plus Integer Overflow (cannot be used without -sparrow or -s)")
    parser.add_argument("-mio", action="store_true", default=False, help="run the sparrow for Minus Integer Overflow (cannot be used without -sparrow or -s)")
    parser.add_argument("-sio", action="store_true", default=False, help="run the sparrow for Shift Integer Overflow (cannot be used without -sparrow or -s)")
    parser.add_argument("-dz", action="store_true", default=False, help="run the sparrow for Division by Zero (cannot be used without -sparrow or -s)")
    parser.add_argument("-bo", action="store_true", default=False, help="run the sparrow for Buffer Overflow (cannot be used without -sparrow or -s)")
    return parser

def check_sparrow_opt(level):
    if configuration["ARGS"].io:
        configuration["USER_SPARROW_OPT"].append("-io")
    if configuration["ARGS"].tio:
        configuration["USER_SPARROW_OPT"].append("-tio")
    if configuration["ARGS"].pio:
        configuration["USER_SPARROW_OPT"].append("-pio")
    if configuration["ARGS"].mio:
        configuration["USER_SPARROW_OPT"].append("-mio")
    if configuration["ARGS"].sio:
        configuration["USER_SPARROW_OPT"].append("-sio")
    if configuration["ARGS"].dz:
        configuration["USER_SPARROW_OPT"].append("-dz")
    if configuration["ARGS"].bo:
        configuration["USER_SPARROW_OPT"].append("-bo")
    if configuration["SPARROW_ONLY"] and len(configuration["USER_SPARROW_OPT"]) == 0:
        logger.log(logger.ERROR, "No sparrow option is given. Please provide at least one option.")
        if level == "TOP":
            oss_usage()
        elif level == "SPARROW":
            sparrow_usage()
        exit(1)
    if not configuration["SPARROW_ONLY"] and len(configuration["USER_SPARROW_OPT"]) != 0:
        logger.log(logger.ERROR, "Sparrow options are given but sparrow is not run.")
        if level == "TOP":
            oss_usage()
        elif level == "SPARROW":
            sparrow_usage()
        exit(1)
    return

def get_sparrow_target_files(dirs):
    if dirs == ["all"]:
        dirs = [configuration["ANALYSIS_DIR"]]
    for dir in dirs:
        if not os.path.exists(dir):
            logger.log(logger.ERROR, f"{dir} does not exist.")
            exit(1)
        for root, _, files in os.walk(dir):
            for file in files:
                if file.endswith(".c"):
                    configuration["SPARROW_TARGET_FILES"].append(os.path.abspath(os.path.join(root, file)))
def setup(level):
    logger.logger = __get_logger()
    parser = argparse.ArgumentParser()
    if level == "TOP":
        # parser.add_argument("-help", "-h", action="store_true", default=False, help="show this help message and exit")
        parser.add_argument("-build", "-b", nargs="*", default=["None"], help="build the given path for category list(s) of package only (default:all)")
        parser.add_argument("-crawl", "-c", action="store_true", default=False, help="crawl the package list from the web only")
        parser.add_argument("-sparrow", "-s", nargs="*", default=["None"], help="run the sparrow for the given directory(ies) (default:all)")
        parser = parse_sparrow_opt(parser)
        configuration["ARGS"] = parser.parse_args()
        if configuration["ARGS"].build == []:
            configuration["ARGS"].build = ["all"]
        if configuration["ARGS"].build[0] != "None":
            configuration["BUILD_ONLY"] = True
        if configuration["ARGS"].sparrow == []:
            configuration["ARGS"].sparrow = ["all"]
        if configuration["ARGS"].sparrow[0] != "None":
            configuration["SPARROW_ONLY"] = True
        if configuration["ARGS"].crawl:
            configuration["CRWAL_ONLY"] = True
        if not configuration["BUILD_ONLY"] and not configuration["CRWAL_ONLY"] and not configuration["SPARROW_ONLY"]:
            configuration["BUILD_ONLY"] = True
            configuration["CRWAL_ONLY"] = True
            configuration["SPARROW_ONLY"] = True
        if configuration["CSV_FOR_STAT"]:
            configuration["CSV_FOR_STAT"] = True
        if configuration["SPARROW_ONLY"]:
            check_sparrow_opt(level)
            get_sparrow_target_files(configuration["ARGS"].sparrow)
    if level == "SPARROW":
        configuration["SPARROW_ONLY"] = True
        # parser.add_argument("-help", "-h", action="store_true", default=False, help="show this help message and exit")
        parser.add_argument("-files", "-f", nargs="*", default=["None"], help="run the sparrow for the given file(s) (default:all)")
        parser = parse_sparrow_opt(parser)
        configuration["ARGS"] = parser.parse_args()
        if configuration["ARGS"].files == ["None"]:
            logger.log(logger.ERROR, "No file is given. Please provide at least one file.")
            sparrow_usage()
            exit(1)
        configuration["SPARROW_TARGET_FILES"] = configuration["ARGS"].files
        check_sparrow_opt(level)
        
    
    logger.log(logger.INFO, "Configuration: {}".format(configuration))
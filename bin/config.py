import os
import argparse
import logger
import logging
import datetime

configuration = {
    "ARGS": None,
    "VERBOSE": False,
    "START_TIME": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
    "FILE_PATH": os.path.dirname(os.path.realpath(__file__)),
    "ROOT_PATH": os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    "OUT_DIR": os.path.join(os.path.dirname(os.path.realpath(__file__)), ".." ,"out"),
    "PKG_DIR": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "package"),
    "SMAKE_OUT_DIR": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "package", "smake_out"),
    "LIST_DIR": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "package", "debian_lists"),
    "ANALYSIS_DIR": "",
    "EXP_ROOT_PATH": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "patron-experiment"),
    "SPARROW_BIN_PATH": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "patron-experiment", "sparrow", "bin", "sparrow"),
    "PATRON_ROOT_PATH": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "patron-experiment", "patron"),
    "PATRON_BIN_PATH": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "patron-experiment", "patron", "patron"),
    "EXP_BIN_PATH": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "patron-experiment", "bin"),
    "BENCHMARK_PATH": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "patron-experiment", "benchmark"),
    # "DB_PATH": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "patron-DB"),
    "BUILD_ONLY": False,
    "CRWAL_ONLY": False,
    "SPARROW_ONLY": False,
    "COMBINE_ONLY": False,
    "PATRON_ONLY": False,
    "PIPE_MODE": False,
    "DATABASE_ONLY": False,
    "CSV_FOR_STAT": False,
    "DEFAULT_SPARROW_OPT": ["-no_bo", "-tio", "-pio", "-mio", "-dz"],
    "USER_SPARROW_OPT": [],
    "ADDITIONAL_SPARROW_OPT": ["-taint", "-unwrap_alloc", "-remove_cast", "-patron", "-extract_datalog_fact_full"],
    "SPARROW_TARGET_FILES": [],
    "DONEE_LIST": [],
    "PROCESS_LIMIT": 20,
    "DB_PATH": os.path.abspath("benchmark-DB"),
    "DONOR_PATH": "benchmark",
    "OVERWRITE_SPARROW": False
}

def openings() -> None:
    print('______  ___ ___________ _____ _   _ ')
    print('| ___ \/ _ \_   _| ___ \  _  | \ | |')
    print('| |_/ / /_\ \| | | |_/ / | | |  \| |')
    print('|  __/|  _  || | |    /| | | | . ` |')
    print('| |   | | | || | | |\  \\ \_/ / |\  |')
    print('\_|   \_| |_/\_/ \_| \_|\___/\_| \_/\n')
    print('                             v.0.0.1')
    print('                by prosys lab, KAIST\n')

def patron_exit(stage:str):
    outpath = ""
    if stage == "BUILD":
        outpath = configuration["SMAKE_OUT_DIR"]
    elif stage == "CRAWL":
        outpath = configuration["LIST_DIR"]
    elif stage == "COMBINE":
        outpath = configuration["ANALYSIS_DIR"]
    elif stage == "SPARROW":
        outpath = configuration["ANALYSIS_DIR"]
    elif stage == "PATRON":
        outpath = configuration["OUT_DIR"]
    bad_ending(outpath)
    
        
    

def happy_ending(out_path:str) -> None:
    print('                                    .''.       ')
    print('        .''.        .        *''*     :_\/_:     . ')
    print('      :_\/_:   _\(/_  .:.*_\/_*   : /\ :  .\'.:.\'.')
    print('    .''.: /\ :   ./)\   \':\'* /\ * :  \'..\'.  -=:o:=-')
    print(' :_\/_:\'.:::.    \' *\'\'*    * \'.\'/.\' _\(/_\'.\':\'.\'')
    print(' : /\ : :::::     *_\/_*     -= o =-  /)\    \'  *')
    print('  \'..\'  \':::\'     * /\ *     .\'/.\\\'.   \'')
    print('      *            *..*         :')
    print('      *')
    print('      *')
    print('ALL DONE! THANK YOU FOR YOUR PATIENCE!')
    print('PLEASE CHECK THE {} FOR THE RESULTS!'.format(out_path))

def bad_ending(out_path:str) -> None:
    print('⠀⠀⠀⠀⠀⢻⠀⠀⠀⠀⠀⠀⠀    ⠀⠀⠀⠀⠀   ⠀⢠⠇')
    print('⠀⠀⠀⠀⠀⠀⣣⠀⠀⠀⠀⠀⠀⠀⠙⠛⠁⠀⠀⠀⠀⠀⠈⠛⠁⡰⠃⠀')
    print('⠀⠀⠀⠀⢠⠞⠋⢳⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠜⠁⠀⠀')
    print('⠀⠀⠀⣰⠋⠀⠀⠀⢷⠙⠲⢤⣀⡀⠀⠀⠀⠀⠴⠴⣆⠴⠚⠁⠀⠀⠀⠀')
    print('⠀⠀⣰⠃⠀⠀⠀⠀⠘⡇⠀⣀⣀⡉⠙⠒⠒⠒⡎⠉⠀⠀⠀⠀⠀⠀⠀⠀')
    print('⠀⢠⠃⠀⠀⢶⠀⠀⠀⢳⠋⠁⠀⠙⢳⡠⠖⠚⠑⠲⡀⠀⠀⠀⠀⠀⠀⠀')
    print('⠀⡎⠀⠀⠀⠘⣆⠀⠀⠈⢧⣀⣠⠔⡺⣧⠀⡴⡖⠦⠟⢣⠀⠀⠀⠀⠀⠀')
    print('⢸⠀⠀⠀⠀⠀⢈⡷⣄⡀⠀⠀⠀⠀⠉⢹⣾⠁⠁⠀⣠⠎⠀⠀⠀⠀⠀⠀')
    print('⠈⠀⠀⠀⠀⠀⡼⠆⠀⠉⢉⡝⠓⠦⠤⢾⠈⠓⠖⠚⢹⠀⠀⠀⠀⠀⠀⠀')
    print('⢰⡀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠁⠀⠀⠀⢸⠀⠀⠀⠀⡏⠀⠀⠀⠀⠀⠀⠀')
    print('⠀⠳⡀⠀⠀⠀⠀⠀⠀⣀⢾⠀⠀⠀⠀⣾⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀')
    print('⠀⠀⠈⠐⠢⠤⠤⠔⠚⠁⠘⣆⠀⠀⢠⠋⢧⣀⣀⡼⠀⠀⠀⠀⠀⠀⠀⠀')
    print('⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠈⠁⠀⠀⠀⠁⠀')
    print('SOMETHING WENT WRONG... PLEASE CHECK THE {} FOR THE RESULTS!'.format(out_path))
    
def __get_logger(level):
    __logger = logging.getLogger("logger")
    formatter = logging.Formatter("[%(levelname)s][%(asctime)s] %(message)s")
    if configuration["VERBOSE"]:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        __logger.addHandler(stream_handler)
    if not os.path.isdir(configuration["OUT_DIR"]):
        os.mkdir(configuration["OUT_DIR"])
    if level == "TOP":
        configuration["OUT_DIR"] = os.path.join(configuration["OUT_DIR"], configuration["START_TIME"] + '_pipe')
    elif level == "FULL":
        configuration["OUT_DIR"] = os.path.join(configuration["OUT_DIR"], configuration["START_TIME"] + '_full')
    elif level == "PATRON" or level == "PATRON_PIPE":
        configuration["OUT_DIR"] = os.path.join(configuration["OUT_DIR"], configuration["START_TIME"] + '_patch')
    elif level == "SPARROW":
        configuration["OUT_DIR"] = os.path.join(configuration["OUT_DIR"], configuration["START_TIME"] + '_sparrow')
    elif level == "COMBINE":
        configuration["OUT_DIR"] = os.path.join(configuration["OUT_DIR"], configuration["START_TIME"] + '_combine')
    elif level == "BUILD":
        configuration["OUT_DIR"] = os.path.join(configuration["OUT_DIR"], configuration["START_TIME"] + '_build')
    elif level == "CRAWL":
        configuration["OUT_DIR"] = os.path.join(configuration["OUT_DIR"], configuration["START_TIME"] + '_crawl')
    elif level == "MERGE":
        configuration["OUT_DIR"] = os.path.join(configuration["OUT_DIR"], configuration["START_TIME"] + '_mergeDB')
    os.mkdir(configuration["OUT_DIR"])
    file_handler = logging.FileHandler(
        os.path.join(configuration["OUT_DIR"], "log_{}.txt".format(configuration["START_TIME"])))
    file_handler.setFormatter(formatter)
    __logger.addHandler(file_handler)
    __logger.setLevel(logging.DEBUG)
    return __logger

def patron_usage():
    print("usage: patron.py [-h] [-donee [DONEE ...]] [-database] [-donorpath DONORPATH] [-dbpath DBPATH] [-process PROCESS] [-sparrow]")
    print("Options:")
    print("  -h, --help                 show this help message and exit")
    print("  -database, -db             construct patron-DB only")
    print("  -donorpath, -dp DONORPATH  path to the donor parograms when making db (default:benchmark")
    print("  -sparrow, -s               overwrite the sparrow results (if run with -db)")
    print("  -donee, -d [DONEE ...]     run the patron for the given donee directory(ies) (default:all)")
    print("  -process, -p PROCESS       number of threads to run (default:20)")
    print("  -dbpath, -dbp DBPATH       path to the DB directory(default:benchmark-DB")
    
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
    return

def get_sparrow_target_files(dirs):
    ret = []
    if dirs == ["all"]:
        dirs = [configuration["ANALYSIS_DIR"]]
    for d in dirs:
        if not os.path.exists(d):
            logger.log(logger.ERROR, f"{d} does not exist.")
            config.patron_exit("SPARROW")
        for root, _, files in os.walk(d):
            for file in files:
                if file.endswith(".c"):
                    configuration["SPARROW_TARGET_FILES"].append(os.path.abspath(os.path.join(root, file)))
                    ret.append(os.path.abspath(os.path.join(root, file)))
    return ret

def get_patron_target_files(target_dirs):
    donee_list = []
    for target in target_dirs:
        if not os.path.exists(target):
            logger.log(logger.ERROR, f"{target} does not exist.")
            config.patron_exit("PATRON")
        for root, dirs, files in os.walk(target):
            if any([d.isdigit() for d in dirs]):
                continue
            for file in files:
                if file.endswith(".c"):
                    donee_list.append((os.path.dirname(os.path.abspath(os.path.join(root, file))), os.path.abspath(os.path.join(root, file))))
    configuration["DONEE_LIST"] = donee_list
    logger.log("INFO", "Configured donee files: {}".format([os.path.basename(donee) for donee, path in configuration["DONEE_LIST"]]))
    return donee_list

def config_log(config):
    if config["VERBOSE"]:
        log = logger.INFO
    else:
        log = logger.ALL
        
    logger.log(log, "Configuration:")
    for key, value in config.items():
        if key == "ARGS":
            continue
        if value == ["None"] or value == []:
            continue
        if key == "DEFAULT_SPARROW_OPT" and "USER_SPARROW_OPT" != []:
            continue
        if value == False:
            continue
        logger.log(log, f"\t{key}: {value}")
            

def setup(level):
    global configuration
    if level != "PATRON_PIPE" and level != "PATRON":
        configuration["ANALYSIS_DIR"] = os.path.join(configuration["PKG_DIR"], "analysis_target_" + configuration["START_TIME"])
        if not os.path.exists(configuration["ANALYSIS_DIR"]):
            os.mkdir(configuration["ANALYSIS_DIR"])
    if level != "PATRON_PIPE":
        parser = argparse.ArgumentParser()
    if level != "PATRON_PIPE" and level != "PATRON" and level != "SPARROW" and level != "FULL":
        level = "TOP"
    if level == "TOP" or level == "FULL":
        parser.add_argument("-v", "--verbose", action="store_true", default=False, help="increase output verbosity")
        parser.add_argument("-oss", action="store_true", default=False, help="run the OSS experiment")
        parser.add_argument("-build", "-b", nargs="*", default=["None"], help="build the given path for category list(s) of package only (default:all)")
        parser.add_argument("-crawl", "-c", action="store_true", default=False, help="crawl the package list from the web only")
        parser.add_argument("-combine", "-m", nargs="*", default=["None"], help="combine *.i files into .c in the the given directory for packages only (default:all)")
        parser.add_argument("-sparrow", "-s", nargs="*", default=["None"], help="run the sparrow for the given directory(ies) (default:all)")
        parser.add_argument("-patron", "-p", nargs="*", default=["None"], help="run the patron for the given donee directory(ies) (default:all)")
        parser.add_argument("-donorpath", "-dp", type=str, default="benchmark", help="path to the donor parograms(default:benchmark")
        parser.add_argument("-dbpath", "-dbp", type=str, default="benchmark-DB", help="path to the DB directory(default:benchmark-DB")
        parser.add_argument("-pipe", nargs="*", default=["None"], help="run the sparrow in pipe mode (build->combine->sparrow)")
        parser.add_argument("-bo_only", action="store_true", default=False, help="run the sparrow for Buffer Overflow")
        parser = parse_sparrow_opt(parser)
        configuration["ARGS"] = parser.parse_args()
        configuration["DB_PATH"] = os.path.abspath(configuration["ARGS"].dbpath)
        configuration["VERBOSE"] = configuration["ARGS"].verbose
        logger.logger = __get_logger(level)
        if configuration["ARGS"].bo_only:
            configuration["DEFAULT_SPARROW_OPT"] = ["-bo"]
        if configuration["ARGS"].oss:
            configuration["ARGS"].pipe = ["all"]
        if configuration["ARGS"].pipe == []:
            configuration["ARGS"].pipe = ["all"]
        if configuration["ARGS"].pipe[0] != "None":
            configuration["PIPE_MODE"] = True
        if configuration["ARGS"].build == []:
            configuration["ARGS"].build = ["all"]
        if configuration["ARGS"].build[0] != "None":
            configuration["BUILD_ONLY"] = True
        if configuration["ARGS"].sparrow == []:
            configuration["ARGS"].sparrow = ["all"]
        if configuration["ARGS"].sparrow[0] != "None":
            configuration["SPARROW_ONLY"] = True
        if configuration["ARGS"].combine == []:
            configuration["ARGS"].combine = ["all"]
        if configuration["ARGS"].combine[0] != "None":
            configuration["COMBINE_ONLY"] = True
        if configuration["ARGS"].patron == []:
            configuration["ARGS"].patron = ["all"]
        if configuration["ARGS"].patron[0] != "None":
            configuration["PATRON_ONLY"] = True
        if configuration["ARGS"].crawl:
            configuration["CRWAL_ONLY"] = True
        if not configuration["BUILD_ONLY"] and not configuration["CRWAL_ONLY"] and not configuration["COMBINE_ONLY"] and not configuration["SPARROW_ONLY"] and not configuration["PIPE_MODE"] and not configuration["PATRON_ONLY"]:
            configuration["BUILD_ONLY"] = True
            configuration["CRWAL_ONLY"] = True
            configuration["SPARROW_ONLY"] = True
            configuration["COMBINE_ONLY"] = True
        if not configuration["BUILD_ONLY"] and not configuration["CRWAL_ONLY"] and not configuration["COMBINE_ONLY"] and not configuration["SPARROW_ONLY"] and not configuration["PATRON_ONLY"] and configuration["ARGS"].pipe == ["all"]:
            configuration["PIPE_MODE"] = True
            # NOTE: change this after experiment is set
            configuration["ARGS"].pipe = [os.path.join(configuration["LIST_DIR"], 'test.txt')]
        if configuration["CSV_FOR_STAT"]:
            configuration["CSV_FOR_STAT"] = True
        if configuration["SPARROW_ONLY"]:
            check_sparrow_opt(level)
            configuration["SPARROW_TARGET_FILES"] = get_sparrow_target_files(configuration["ARGS"].sparrow)
    if level == "SPARROW":
        configuration["SPARROW_ONLY"] = True
        parser.add_argument("-v", "--verbose", action="store_true", default=False, help="increase output verbosity")
        parser.add_argument("-files", "-f", nargs="*", default=["None"], help="run the sparrow for the given file(s) (default:all)")
        parser.add_argument("-out", "-o", type=str, default=configuration["ANALYSIS_DIR"], help="output directory for the analysis results")
        parser = parse_sparrow_opt(parser)
        configuration["ARGS"] = parser.parse_args()
        configuration["VERBOSE"] = configuration["ARGS"].verbose
        logger.logger = __get_logger(level)
        configuration["ANALYSIS_DIR"] = configuration["ARGS"].out
        if configuration["ARGS"].files == ["None"]:
            logger.log(logger.ERROR, "No file is given. Please provide at least one file.")
            sparrow_usage()
            config.patron_exit("SPARROW")
        configuration["SPARROW_TARGET_FILES"] = configuration["ARGS"].files
        check_sparrow_opt(level)
    if level == "COMBINE":
        configuration["COMBINE_ONLY"] = True
        parser.add_argument("-v", "--verbose", action="store_true", default=False, help="increase output verbosity")
        configuration["VERBOSE"] = configuration["ARGS"].verbose
        logger.logger = __get_logger(level)
        parser.add_argument("file", type=str, default="", help=".txt file containing list of target packages")
        parser.add_argument("-out", "-o", type=str, default=configuration["ANALYSIS_DIR"], help="output directory for the analysis results")
        configuration["ARGS"] = parser.parse_args()
        configuration["ANALYSIS_DIR"] = configuration["ARGS"].out
        if configuration["ARGS"].file == "":
            logger.log(logger.ERROR, "No file is given. Please provide a file.")
            config.patron_exit("COMBINE")
    if level == "PATRON":
        configuration["PATRON_ONLY"] = True
        parser.add_argument("-v", "--verbose", action="store_true", default=False, help="increase output verbosity")
        parser.add_argument("-donee", "-d", nargs="*", default=["None"], help="run the patron for the given donee directory(ies) (default:all)")
        parser.add_argument("-database", "-db", action="store_true", default=False, help="construct patron-DB only")
        parser.add_argument("-donorpath", "-dp", type=str, default="benchmark", help="path to the donor parograms(default:benchmark")
        parser.add_argument("-dbpath", "-dbp", type=str, default="benchmark-DB", help="path to the database directory(default:benchmark-DB")
        parser.add_argument("-process", '-p', type=int, default=20, help="number of threads to run")
        parser.add_argument("-sparrow", '-s', action="store_true", default=False, help="overwrite the sparrow results")
        configuration["ARGS"] = parser.parse_args()
        configuration["VERBOSE"] = configuration["ARGS"].verbose
        logger.logger = __get_logger(level)
        configuration["DB_PATH"] = os.path.abspath(configuration["ARGS"].dbpath)
        if configuration["ARGS"].database:
            configuration["DATABASE_ONLY"] = True
            configuration["DONOR_PATH"] = os.path.abspath(configuration["ARGS"].donorpath)
            configuration["OVERWRITE_SPARROW"] = configuration["ARGS"].sparrow
        else:
            logger.log(logger.INFO, "Configuring target donee files under given directories {}".format(configuration["ARGS"].donee))
            if configuration["ARGS"].donee == ["None"]:
                target_dirs = [ os.path.abspath(don) for don in configuration["ARGS"].patron ]
            else:
                target_dirs = [ os.path.abspath(don) for don in configuration["ARGS"].donee ]
            configuration['PROCESS_LIMIT'] = configuration["ARGS"].process
            get_patron_target_files(target_dirs)
    if level == "TOP" and configuration["PATRON_ONLY"]:
        configuration["PATRON_ONLY"] = True
        logger.log(logger.INFO, "Configuring target donee files under given directories {}".format(configuration["ARGS"].patron))
        target_dirs = [ os.path.abspath(don) for don in configuration["ARGS"].patron ]
        get_patron_target_files(target_dirs)
    config_log(configuration)

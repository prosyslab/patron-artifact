import os
import argparse
import logger
import logging
import datetime

configuration = {
    "ARGS": None,
    "VERBOSE": False,
    "PURPOSE": "",
    "START_TIME": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
    "FILE_PATH": "",
    "ROOT_PATH": "",
    "SPARROW_BIN_PATH": "",
    "PATRON_ROOT_PATH": "",
    "PATRON_BIN_PATH": "",
    "OUT_DIR": "",
    "PKG_DIR": "",
    "SMAKE_OUT_DIR": "",
    "LIST_DIR": "",
    "ANALYSIS_DIR": "",
    "CSV_FOR_STAT": False,
    "ITER_MODE": False,
    "DEFAULT_TARGET_LIST_PATH": "",
    "DONEE_LIST": [],
    "PROCESS_LIMIT": 20,
    "SPARROW_LOG_DIR": "",
    "DATABASE_ONLY": False
}

preprocess_configuration = {
    "VERBOSE":
    False,
    "TARGET_PACKAGES": [],
    "SPARROW_BIN_PATH":
    "",
    "DEFAULT_SPARROW_OPT":
    ["-taint", "-unwrap_alloc", "-remove_cast", "-patron", "-extract_datalog_fact_full"],
    "ADDITIONAL_SPARROW_OPT": ["-no_bo", "-tio", "-pio", "-mio", "-dz"],
    "USER_SPARROW_OPT": [],
    "SPARROW_TARGET_FILES": [],
    "OVERWRITE_SPARROW":
    True
}

transplant_configuration = {
    "VERBOSE": False,
    "PATRON_ROOT_PATH": "",
    "PATRON_BIN_PATH": "",
    "DB_PATH": "",
    "SUBOUT_DIR": "",
    "BENCHMARK_PATH": "",
    "DONEE_LIST": []
}

build_configuration = {"VERBOSE": False, "TARGET_PACKAGES": []}

sparrow_configuration = {
    "SPARROW_BIN_PATH":
    "",
    "DEFAULT_SPARROW_OPT":
    ["-taint", "-unwrap_alloc", "-remove_cast", "-patron", "-extract_datalog_fact_full"],
    "ADDITIONAL_SPARROW_OPT": ["-no_bo", "-tio", "-pio", "-mio", "-dz"],
    "SPARROW_COMMAND":
    "",
    "USER_SPARROW_OPT": [],
    "SPARROW_TARGET_FILES": [],
    "OVERWRITE_SPARROW":
    False
}

db_configuration = {
    "PATRON_ROOT_PATH": "",
    "PATRON_BIN_PATH": "",
    "DONOR_PATH": "",
    "BENCHMARK_PATH": "",
    "RQ1-2_EXP_PATH": "",
    "DB_OUT_DIR": "",
    "OVERWRITE_SPARROW": False
}


def openings() -> None:
    print('______  ___ ___________ _____ _   _ ')
    print('| ___ \/ _ \_   _| ___ \  _  | \ | |')
    print('| |_/ / /_\ \| | | |_/ / | | |  \| |')
    print('|  __/|  _  || | |    /| | | | . ` |')
    print('| |   | | | || | | |\  \\ \_/ / |\  |')
    print('\_|   \_| |_/\_/ \_| \_|\___/\_| \_/\n')
    print('                             v.0.1.0')
    print('                by prosys lab, KAIST\n')


def patron_exit(stage: str, out_path=None):
    outpath = ""
    if stage == "BUILD":
        outpath = out_path if out_path else configuration["SMAKE_OUT_DIR"]
    elif stage == "CRAWL":
        outpath = out_path if out_path else configuration["LIST_DIR"]
    elif stage == "COMBINE":
        outpath = out_path if out_path else configuration["ANALYSIS_DIR"]
    elif stage == "SPARROW":
        outpath = out_path if out_path else configuration["ANALYSIS_DIR"]
    elif stage == "PATRON":
        outpath = out_path if out_path else configuration["OUT_DIR"]
    bad_ending(outpath)


def happy_ending(out_path: str) -> None:
    print('                                    .'
          '.       ')
    print('        .'
          '.        .        *'
          '*     :_\/_:     . ')
    print('      :_\/_:   _\(/_  .:.*_\/_*   : /\ :  .\'.:.\'.')
    print('    .'
          '.: /\ :   ./)\   \':\'* /\ * :  \'..\'.  -=:o:=-')
    print(' :_\/_:\'.:::.    \' *\'\'*    * \'.\'/.\' _\(/_\'.\':\'.\'')
    print(' : /\ : :::::     *_\/_*     -= o =-  /)\    \'  *')
    print('  \'..\'  \':::\'     * /\ *     .\'/.\\\'.   \'')
    print('      *            *..*         :')
    print('      *')
    print('      *')
    print('ALL DONE! THANK YOU FOR YOUR PATIENCE!')
    print('PLEASE CHECK THE {} FOR MORE DETAILS!'.format(out_path))


def bad_ending(out_path: str) -> None:
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
    exit(1)


def __get_logger(purpose):
    __logger = logging.getLogger("logger")
    formatter = logging.Formatter("[%(levelname)s][%(asctime)s] %(message)s")
    if configuration["VERBOSE"]:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        __logger.addHandler(stream_handler)
    if not os.path.isdir(configuration["OUT_DIR"]):
        os.mkdir(configuration["OUT_DIR"])
    match purpose:
        case "PREP":
            configuration["OUT_DIR"] = os.path.join(configuration["OUT_DIR"],
                                                    configuration["START_TIME"] + '_RQ3_PREPROCESS')
        case "TRANS":
            configuration["OUT_DIR"] = os.path.join(configuration["OUT_DIR"],
                                                    configuration["START_TIME"] + '_RQ3_TRANSPLANT')
        case "CRAWL":
            configuration["OUT_DIR"] = os.path.join(configuration["OUT_DIR"],
                                                    configuration["START_TIME"] + '_debian_crawl')
        case "BUILD":
            configuration["OUT_DIR"] = os.path.join(configuration["OUT_DIR"],
                                                    configuration["START_TIME"] + '_build_packages')
        case "SPARROW":
            configuration["OUT_DIR"] = os.path.join(configuration["OUT_DIR"],
                                                    configuration["START_TIME"] + '_sparrow')
        case "DB":
            configuration["OUT_DIR"] = os.path.join(configuration["OUT_DIR"],
                                                    configuration["START_TIME"] + '_patron_db')
        case _:
            print("[ERROR] Invalid purpose")
            exit(1)
    os.mkdir(configuration["OUT_DIR"])
    file_handler = logging.FileHandler(
        os.path.join(configuration["OUT_DIR"], "log_{}.txt".format(configuration["START_TIME"])))
    file_handler.setFormatter(formatter)
    __logger.addHandler(file_handler)
    __logger.setLevel(logging.DEBUG)
    return __logger

def get_patron_target_files(target_dirs):
    donee_list = []
    print(target_dirs)
    for target in target_dirs:
        if not os.path.exists(target):
            logger.log(logger.ERROR, f"{target} does not exist.")
            patron_exit("PATRON")
        for root, dirs, files in os.walk(target):
            if any([d.isdigit() for d in dirs]):
                continue
            for file in files:
                if file.endswith(".c"):
                    donee_list.append((os.path.dirname(os.path.abspath(os.path.join(root, file))),
                                       os.path.abspath(os.path.join(root, file))))
    transplant_configuration["DONEE_LIST"] = donee_list
    logger.log(
        logger.ALL, "Configured donee files: {}".format(
            [os.path.basename(donee) for donee, path in configuration["DONEE_LIST"]]))
    return donee_list


def filter_unnecessary_config(config):
    for key, value in config.items():
        if key == "ARGS":
            continue
        if value == ["None"] or value == [] or value == "":
            continue
        if key == "DEFAULT_SPARROW_OPT" and "USER_SPARROW_OPT" != []:
            continue
        if value == False:
            continue
        logger.log(logger.ALL, f"\t{key}: {value}")


def config_log(purpose):
    if configuration["VERBOSE"]:
        logger.LOG_MODE = logger.ALL
    else:
        logger.LOG_MODE = logger.INFO
    logger.log(logger.ALL, "Configuration:")
    filter_unnecessary_config(configuration)
    match purpose:
        case "PREP":
            filter_unnecessary_config(preprocess_configuration)
        case "TRANS":
            filter_unnecessary_config(transplant_configuration)
        case "BUILD":
            filter_unnecessary_config(build_configuration)
        case "SPARROW":
            filter_unnecessary_config(sparrow_configuration)
        case "DB":
            filter_unnecessary_config(db_configuration)


def setup_default_config():
    global configuration
    configuration["FILE_PATH"] = os.path.dirname(os.path.realpath(__file__))
    configuration["ROOT_PATH"] = os.path.abspath(
        os.path.join(configuration["FILE_PATH"], '..', '..'))
    configuration["OUT_DIR"] = os.path.abspath(os.path.join(configuration["ROOT_PATH"], "out"))
    configuration["PKG_DIR"] = os.path.abspath(
        os.path.join(configuration["ROOT_PATH"], "data", "RQ3", "DebianBench"))
    configuration["SMAKE_OUT_DIR"] = os.path.join(configuration["PKG_DIR"], "smake_out")
    configuration["LIST_DIR"] = os.path.abspath(
        os.path.join(configuration["PKG_DIR"], "crawling_result"))
    configuration["SPARROW_BIN_PATH"] = os.path.abspath(
        os.path.join(configuration["ROOT_PATH"], "sparrow", "bin", "sparrow"))
    configuration["PATRON_ROOT_PATH"] = os.path.abspath(
        os.path.join(configuration["ROOT_PATH"], "patron"))
    configuration["PATRON_BIN_PATH"] = os.path.abspath(
        os.path.join(configuration["ROOT_PATH"], "patron", "patron"))
    configuration["ANALYSIS_DIR"] = os.path.join(configuration["PKG_DIR"],
                                                 "analysis_target_" + configuration["START_TIME"])
    configuration["DEFAULT_TARGET_LIST_PATH"] = os.path.join(configuration["PKG_DIR"],
                                                             "target_list.txt")


def setup_sparrow():
    global configuration, sparrow_configuration
    openings()
    setup_default_config()
    configuration["PURPOSE"] = "SPARROW"
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose',
                        '-v',
                        action='store_true',
                        default=False,
                        help='increase output verbosity')
    parser.add_argument('--target-directory',
                        '-t',
                        nargs='+',
                        default=[],
                        help='run the sparrow for the given directory(ies)')
    parser.add_argument('--integer-overflow',
                        '-io',
                        action='store_true',
                        default=False,
                        help='run the sparrow for Integer Overflow')
    parser.add_argument('--times-integer-overflow',
                        '-tio',
                        action='store_true',
                        default=False,
                        help='run the sparrow for Times Integer Overflow')
    parser.add_argument('--plus-integer-overflow',
                        '-pio',
                        action='store_true',
                        default=False,
                        help='run the sparrow for Plus Integer Overflow')
    parser.add_argument('--minus-integer-overflow',
                        '-mio',
                        action='store_true',
                        default=False,
                        help='run the sparrow for Minus Integer Overflow')
    parser.add_argument('--shift-integer-overflow',
                        '-sio',
                        action='store_true',
                        default=False,
                        help='run the sparrow for Shift Integer Overflow')
    parser.add_argument('--division-by-zero',
                        '-dz',
                        action='store_true',
                        default=False,
                        help='run the sparrow for Division by Zero')
    parser.add_argument('--buffer-overflow',
                        '-bo',
                        action='store_true',
                        default=False,
                        help='run the sparrow for Buffer Overflow')
    parser.add_argument('--overwrite-sparrow',
                        action='store_true',
                        default=False,
                        help='overwrite the sparrow results if already exists')
    parser.add_argument('--process-limit',
                        '-p',
                        type=int,
                        default=20,
                        help='number of threads to run (default:20)')
    configuration["ARGS"] = parser.parse_args()
    configuration["PROCESS_LIMIT"] = configuration["ARGS"].process_limit
    configuration["VERBOSE"] = configuration["ARGS"].verbose
    logger.logger = __get_logger("SPARROW")
    configuration["SPARROW_LOG_DIR"] = os.path.join(configuration['OUT_DIR'], 'sparrow_logs')
    if not os.path.exists(configuration["SPARROW_LOG_DIR"]):
        os.mkdir(configuration["SPARROW_LOG_DIR"])
    if configuration["ARGS"].target_directory == []:
        logger.log(logger.ERROR, "No target directory is given.")
        bad_ending(configuration["OUT_DIR"])
    if configuration["ARGS"].overwrite_sparrow:
        sparrow_configuration["OVERWRITE_SPARROW"] = True
    if not (configuration["ARGS"].integer_overflow or configuration["ARGS"].times_integer_overflow
            or configuration["ARGS"].plus_integer_overflow
            or configuration["ARGS"].minus_integer_overflow
            or configuration["ARGS"].shift_integer_overflow
            or configuration["ARGS"].division_by_zero or configuration["ARGS"].buffer_overflow):
        sparrow_configuration["USER_SPARROW_OPT"] = sparrow_configuration["ADDITIONAL_SPARROW_OPT"]
    if configuration["ARGS"].integer_overflow:
        sparrow_configuration["USER_SPARROW_OPT"].append("-io")
        if not '-no_bo' in sparrow_configuration["USER_SPARROW_OPT"]:
            sparrow_configuration["USER_SPARROW_OPT"].append("-no_bo")
    if configuration["ARGS"].times_integer_overflow:
        sparrow_configuration["USER_SPARROW_OPT"].append("-tio")
        if not '-no_bo' in sparrow_configuration["USER_SPARROW_OPT"]:
            sparrow_configuration["USER_SPARROW_OPT"].append("-no_bo")
    if configuration["ARGS"].plus_integer_overflow:
        sparrow_configuration["USER_SPARROW_OPT"].append("-pio")
        if not '-no_bo' in sparrow_configuration["USER_SPARROW_OPT"]:
            sparrow_configuration["USER_SPARROW_OPT"].append("-no_bo")
    if configuration["ARGS"].minus_integer_overflow:
        sparrow_configuration["USER_SPARROW_OPT"].append("-mio")
        if not '-no_bo' in sparrow_configuration["USER_SPARROW_OPT"]:
            sparrow_configuration["USER_SPARROW_OPT"].append("-no_bo")
    if configuration["ARGS"].shift_integer_overflow:
        sparrow_configuration["USER_SPARROW_OPT"].append("-sio")
        if not '-no_bo' in sparrow_configuration["USER_SPARROW_OPT"]:
            sparrow_configuration["USER_SPARROW_OPT"].append("-no_bo")
    if configuration["ARGS"].division_by_zero:
        sparrow_configuration["USER_SPARROW_OPT"].append("-dz")
        if not '-no_bo' in sparrow_configuration["USER_SPARROW_OPT"]:
            sparrow_configuration["USER_SPARROW_OPT"].append("-no_bo")
    if configuration["ARGS"].buffer_overflow:
        sparrow_configuration["USER_SPARROW_OPT"].append("-bo")
        if '-no_bo' in sparrow_configuration["USER_SPARROW_OPT"]:
            sparrow_configuration["USER_SPARROW_OPT"].remove("-no_bo")
    return


def setup_build():
    global configuration
    openings()
    setup_default_config()
    configuration["PURPOSE"] = "BUILD"
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose',
                        '-v',
                        action='store_true',
                        default=False,
                        help='increase output verbosity')
    parser.add_argument(
        '--projects',
        '-p',
        nargs='+',
        default=["all"],
        help='build the given debian projects (default:113 projects from DebianBench)')
    configuration["ARGS"] = parser.parse_args()
    logger.logger = __get_logger("BUILD")
    return


def setup_crawl():
    global configuration
    openings()
    setup_default_config()
    configuration["PURPOSE"] = "CRAWL"
    logger.logger = __get_logger("CRAWL")
    return


def setup_preprocess():
    configuration["PURPOSE"] = "PREPROCESS"
    logger.logger = __get_logger("PREP")
    configuration["SPARROW_LOG_DIR"] = os.path.join(configuration["OUT_DIR"], "sparrow_logs")
    if not os.path.exists(configuration["SPARROW_LOG_DIR"]):
        os.mkdir(configuration["SPARROW_LOG_DIR"])


def setup_db():
    configuration["PURPOSE"] = "DB"
    db_configuration["DATABASE_ONLY"] = True
    db_configuration["BENCHMARK_PATH"] = os.path.join(configuration["ROOT_PATH"], "data", "RQ1-2")
    if configuration["ARGS"].database == "":
        print("[ERROR] Invalid usage for database option:")
        print("\t--database, -db [DONOR_PATH]")
        exit(1)
    db_configuration["DONOR_PATH"] = os.path.abspath(configuration["ARGS"].database)
    db_configuration["OVERWRITE_SPARROW"] = configuration["ARGS"].overwrite_sparrow
    db_configuration["RQ1-2_EXP_PATH"] = os.path.join(configuration["ROOT_PATH"], "bin", "RQ1-2")
    db_configuration["DB_OUT_DIR"] = os.path.abspath(configuration["ARGS"].database_path)
    logger.logger = __get_logger("DB")


def setup_transplant():
    configuration["PURPOSE"] = "TRANSPLANT"
    if not os.path.exists(configuration["ARGS"].database_path):
        print(f"[ERROR] {configuration['ARGS'].database_path} does not exist.")
        print(
            f"[ERROR] Please run \"./bin/run_patron --construct-database\" or \"./bin/RQ3/run.py --construct-database path/to/donor\" first."
        )
        exit(1)
    logger.logger = __get_logger("TRANS")
    transplant_configuration["DB_PATH"] = os.path.abspath(configuration["ARGS"].database_path)
    target_dirs = [os.path.abspath(don) for don in configuration["ARGS"].projects]
    get_patron_target_files(target_dirs)
    transplant_configuration["SUBOUT_DIR"] = os.path.abspath(
        os.path.join(configuration["OUT_DIR"], "patches"))
    os.mkdir(transplant_configuration["SUBOUT_DIR"])


def safty_check_main(args):
    is_database = False if args.database == "" else True
    msg = "[ERROR] You can only use one of the following options: --preprocess, --transplant, --database"
    if args.preprocess and args.transplant:
        print(msg)
        exit(1)
    elif args.preprocess and is_database:
        print(msg)
        exit(1)
    elif args.transplant and is_database:
        print(msg)
        exit(1)
    elif not (args.preprocess or args.transplant or is_database):
        print("[ERROR] No arguments given, ex) --database [DONOR_PATH]")
        exit(1)


def setup_main():
    global configuration
    setup_default_config()
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose',
                        '-v',
                        action='store_true',
                        default=False,
                        help='increase output verbosity')
    parser.add_argument('--preprocess',
                        '-prep',
                        action='store_true',
                        default=False,
                        help='run the preprocess (crawl-build-parse-analysis)')
    parser.add_argument('--transplant',
                        '-trans',
                        action='store_true',
                        default=False,
                        help='run the transplant')
    parser.add_argument(
        '--projects',
        '-p',
        nargs='+',
        default=["all"],
        help='run on the given debian projects (default:113 projects from DebianBench)')
    parser.add_argument('--package-list',
                        type=str,
                        default=configuration["DEFAULT_TARGET_LIST_PATH"],
                        help='path to the debian package list as a file (.txt)')
    parser.add_argument('--database',
                        '-db',
                        type=str,
                        default="",
                        help='run the database construction on the given donor directory(ies)')
    parser.add_argument('--database-path',
                        '-dbp',
                        type=str,
                        default="benchmark-DB",
                        help='path to the DB directory (default:benchmark-DB)')
    parser.add_argument('--overwrite-sparrow',
                        action='store_true',
                        default=False,
                        help='overwrite the sparrow results if already exists')
    parser.add_argument('--process-limit',
                        '-pl',
                        type=int,
                        default=20,
                        help='number of threads to run (default:20)')
    configuration["ARGS"] = parser.parse_args()
    safty_check_main(configuration["ARGS"])
    configuration["PROCESS_LIMIT"] = configuration["ARGS"].process_limit
    if configuration["ARGS"].preprocess:
        purpose = "PREP"
        setup_preprocess()
    elif configuration["ARGS"].transplant:
        purpose = "TRANS"
        setup_transplant()
    elif configuration["ARGS"].database != "":
        purpose = "DB"
        setup_db()
    else:
        print("Invalid option. Please choose one of the following options:")
        print("\t--preprocess, -prep: run the preprocess (crawl-build-parse-analysis)")
        print("\t--transplant, -trans: run the patch transplantation")
        print("\t--database, -db: run the database construction")
    configuration["VERBOSE"] = configuration["ARGS"].verbose
    build_configuration['PIPE_MODE'] = True
    config_log(purpose)
    return purpose


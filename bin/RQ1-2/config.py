import os
import argparse
import logger
import logging
import benchmark
import datetime

TARGET_PROCEDURE = ["PIPE_DB", "SPARROW", "PATRON"]
configuration = {
    "TARGET_PROCEDURE":
    "PIPE_DB",
    "SPARROW_BIN_PATH":
    "",
    "PATRON_BIN_PATH":
    "",
    "BENCHMARK_HOME":
    None,
    "BIN_HOME":
    None,
    "OUT_DIR":
    None,
    "PROJECT_HOME":
    None,
    "default_sparrow_options": [
        "-taint", "-unwrap_alloc", "-extract_datalog_fact_full", "-patron",
        "-remove_cast"
    ],
    "default_patron_options": ["dtd"],
    "args":
    None,
    "TIMEOUT":
    1800,
    "CPU_CORE":
    0,
    "benchmark_set":
    "",
    "time_record": [],
    "log_title": ""
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
        os.path.join(configuration["OUT_DIR"], configuration["log_title"] + "log.txt"))
    file_handler.setFormatter(formatter)
    __logger.addHandler(file_handler)
    __logger.setLevel(logging.DEBUG)

    return __logger


def setup():
    configuration["PROJECT_HOME"] = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..'))
    configuration["BENCHMARK_DIR"] = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), "data", "RQ1-2")
    configuration["BIN_HOME"] = os.path.join(configuration["PROJECT_HOME"], "bin", "RQ1-2")
    parser = argparse.ArgumentParser()
    parser.add_argument("-sparrow",
                        action="store_true",
                        default=False,
                        help="run sparrow only")
    parser.add_argument("-patron",
                        action="store_true",
                        default=False,
                        help="run patron only")
    parser.add_argument("-mute",
                        action="store_true",
                        default=False,
                        help="mute the log")
    parser.add_argument("-parallel",
                        "-p",
                        action="store_true",
                        default=False,
                        help="run in parallel")
    parser.add_argument(
        "-no_target",
        action="store_true",
        default=False,
        help="run without the labelled target alarm for the sparrow analysis")
    parser.add_argument(
        "-out",
        default=os.path.join(configuration["PROJECT_HOME"], "out",
                             datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "_RQ1-2"),
        help="output directory(default={}/out)".format(
            configuration["PROJECT_HOME"]),
    )
    parser.add_argument(
        "-log_title", "-lt", type=str, default="", help="log title(default=log)")
    parser.add_argument("benchmark_set", type=str)
    parser.add_argument(
        "-id",
        nargs="+",
        default=[],
        help=
        "run specific id(s) of the given benchmark (e.g. -id 1,2,3       (skipping this option will run all ids))",
    )
    parser.add_argument(
        "-range",
        nargs="+",
        default=None,
        help=
        "run a range of ids. overrides -id option (e.g. -range 1 10     (run id 1 to 10))",
    )
    parser.add_argument("-dug",
                        action="store_true",
                        default=False,
                        help="run saprrow with -dug option")
    parser.add_argument(
        "-timeout",
        type=int,
        default=600,
        help="set timeout for each benchmark(default = 600 sec)",
    )
    parser.add_argument("-t",
                        action="store_true",
                        default=False,
                        help="measure the time of the execution")
    parser.add_argument(
        "-cpu",
        type=int,
        default=int(os.cpu_count()) / 2,
        help=
        "set desirable cpu core on the experiment(default = half the cores)",
    )
    parser.add_argument(
        "--skip-intro",
        action="store_true",
        default=False,
        help="skip the introduction message"
    )
    configuration["args"] = parser.parse_args()
    if configuration["args"].t and configuration["args"].parallel:
        logger.log(
            -1,
            "Can't measure execution time on parallel mode! Please choose one of the options: -t or -parallel"
        )
        exit(1)
    
    configuration["OUT_DIR"] = configuration["args"].out
    configuration["benchmark_set"] = configuration["args"].benchmark_set
    if not os.path.isdir("out"):
        os.mkdir("out")
    try:
        if not os.path.isdir(configuration["OUT_DIR"]):
            os.mkdir(configuration["OUT_DIR"])
    except OSError:
        print("can't log: output directory is not approriate")
        print("Given path: " + configuration["OUT_DIR"])
        exit(-1)
    if configuration["args"].log_title != "":
        configuration["log_title"] = configuration["args"].log_title + "_"
    logger.logger = __get_logger()
    path = os.path.join(configuration["PROJECT_HOME"], "sparrow", "bin",
                        "sparrow")
    logger.log(0, "task objectives: run patron pipeline")
    if not os.path.isfile(path):
        logger.log(-1, "SPARROW is not built")
        exit(1)
    configuration["SPARROW_BIN_PATH"] = os.path.join(
        configuration["PROJECT_HOME"], "sparrow", "bin", "sparrow")
    path = os.path.join(configuration["PROJECT_HOME"], "patron", "patron")
    if not os.path.isfile(path):
        logger.log(-1, "PATRON is not built")
        exit(1)
    configuration["PATRON_BIN_PATH"] = os.path.join(
        configuration["PROJECT_HOME"], "patron", "patron")
    procedure_checker = int(configuration["args"].sparrow) + int(
        configuration["args"].patron)
    if procedure_checker > 1:
        logger.log(-1, "Please specify only one procedure")
        exit(1)
    elif configuration["args"].sparrow:
        configuration["TARGET_PROCEDURE"] = TARGET_PROCEDURE[1]
    elif configuration["args"].patron:
        configuration["TARGET_PROCEDURE"] = TARGET_PROCEDURE[2]

    configuration["CPU_CORE"] = configuration["args"].cpu
    configuration["TIMEOUT"] = configuration["args"].timeout
    if configuration["TARGET_PROCEDURE"] == "SPARROW":
        if configuration["args"].dug:
            configuration["default_sparrow_options"].append("-dug")
    if configuration["args"].range is not None:
        configuration["args"].id = []
        if len(configuration["args"].range) != 2 or int(
                configuration["args"].range[0]) > int(
                    configuration["args"].range[1]):
            logger.log(-1, "range: Please specify the range of benchmark id")
            exit(1)
        for i in range(int(configuration["args"].range[0]),
                       int(configuration["args"].range[1]) + 1):
            configuration["args"].id.append(str(i))
    logger.log(0, "Your configuration is as follows:")
    logger.log(0,
               "\tEXPERIMENT TARGET: " + configuration["args"].benchmark_set)
    logger.log(0, "\tPROCESS_TARGET: " + configuration["TARGET_PROCEDURE"])
    logger.log(0, "\tSPARROW_BIN_PATH: " + configuration["SPARROW_BIN_PATH"])
    logger.log(0, "\tPATRON_BIN_PATH: " + configuration["PATRON_BIN_PATH"])
    if configuration["args"].id == []:
        print(configuration["args"].benchmark_set)
        configuration["args"].id = benchmark.expriment_ready_to_go[
            configuration["args"].benchmark_set]
        logger.log(
            0,
            "\tTARGET ID: Not Given\n\t\t\t\t procedding with all available IDs:\n\t\t\t\t\t"
            + str(configuration["args"].id),
        )
    else:
        logger.log(0, "\tTARGET ID: " + str(configuration["args"].id))

    logger.log(0, "Environment setup completed")

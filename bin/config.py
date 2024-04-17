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
    "BUILD_ONLY": False
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

def setup(is_top_level):
    logger.logger = __get_logger()
    if not is_top_level:
        parser = argparse.ArgumentParser()
        parser.add_argument("-build", "-b", nargs="*", default=["None"], help="build the given package(s)")
        configuration["ARGS"] = parser.parse_args()
        if len(configuration["ARGS"].build) == 0 or configuration["ARGS"].build[0] != "None":
            configuration["BUILD_ONLY"] = True
        logger.log(logger.INFO, "Configuration: {}".format(configuration))
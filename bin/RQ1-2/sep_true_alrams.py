#!/usr/bin/env python3

import os
import json
import logger
import config
import argparse
import datetime
import benchmark

FILE_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.abspath(os.path.join(FILE_PATH, "..", ".."))

failed = []
successed = []

PATRON_BENCH_PATH = os.path.join(ROOT_PATH, "data", "RQ1-2", "patron")
PATCHWEAVE_BENCH_PATH = os.path.join(ROOT_PATH, "data", "RQ1-2", "PWBench")

configuration = {"BENCHMARK_SET": "", "ID": None, "NO_LOG": False}


def logger_wrapper(level, msg):
    if not configuration["NO_LOG"]:
        logger.log(level, msg)


def parse_args():
    parser = argparse.ArgumentParser(description="Separate true alarms")
    config.configuration["PROJECT_HOME"] = os.path.dirname(
        os.path.dirname(os.path.realpath(__file__)))
    parser.add_argument("benchmark_set", type=str)
    parser.add_argument(
        "-out",
        default=os.path.join(config.configuration["PROJECT_HOME"], "out",
                             datetime.datetime.now().strftime("%Y%m%d%H%M%S")),
        help="output directory(default={}/out)".format(
            config.configuration["PROJECT_HOME"]),
    )
    parser.add_argument("-no_log", action="store_true", help="do not log")
    parser.add_argument(
        "-id",
        nargs="+",
        default=[],
        help=
        "run specific id(s) of the given benchmark (e.g. -id 1,2,3       (skipping this option will run all ids))",
    )
    configuration["BENCHMARK_SET"] = parser.parse_args().benchmark_set
    config.configuration["OUT_DIR"] = parser.parse_args().out
    configuration["NO_LOG"] = parser.parse_args().no_log
    configuration["ID"] = parser.parse_args().id
    if configuration["ID"] == []:
        configuration["ID"] = benchmark.expriment_ready_to_go[
            configuration["BENCHMARK_SET"]]
    if not configuration["NO_LOG"]:
        config.configuration['log_title'] = "ALARM_SEP"
        logger.logger = config.__get_logger()
    logger_wrapper(
        0, "logs are saved in " + config.configuration["OUT_DIR"] + "/ALARM_SEP_log.txt")
    logger_wrapper(0, "task objectives: separate true alarms")
    logger_wrapper(0,
                   "target benchmark_set: " + configuration["BENCHMARK_SET"])
    logger_wrapper(0, "target id: " + str(configuration["ID"]))
    return


def safty_check_patron(dir, alarm_paths):
    alram_num = os.path.basename(dir)
    if not os.path.exists(dir):
        logger_wrapper(1, alram_num + " does not exist. Skip this project.")
        failed.append(alram_num)
        return False
    if not os.path.exists(dir + "/bug/sparrow-out"):
        logger_wrapper(
            1, alram_num + "/sparrow-out does not exist. Skip this project.")
        failed.append(alram_num)
        return False
    if os.path.exists(dir + "/bug/sparrow-out/taint/datalog_full"):
        logger_wrapper(
            1, alram_num +
            "/datalog_full file already exists. Skip this project.")
        failed.append(alram_num)
        return False
    if not os.path.exists(dir + "/bug/sparrow-out/taint/datalog"):
        logger_wrapper(
            1, alram_num + "/datalog file does not exist. Skip this project.")
        failed.append(alram_num)
        return False
    for path in alarm_paths:
        if not os.path.exists(path):
            logger_wrapper(
                1, alram_num + " " + path +
                "th alarm do not exist in the datalog. Skip this project.")
            failed.append(alram_num)
            return False
    if alarm_paths == []:
        logger_wrapper(
            1, alram_num + ",no alarm in the project. Skip this project.")
        failed.append(alram_num)
        return False
    return True


def run_on_patron():
    logger_wrapper(0, "Start to separate true alarms.")
    alarm_paths = []
    for dir in os.listdir(PATRON_BENCH_PATH):
        if dir in configuration["ID"]:
            full_dir = os.path.join(PATRON_BENCH_PATH, dir)
            with open(os.path.join(full_dir, "label.json"), "r") as f:
                label = json.load(f)
                # safety check
                try:
                    alarms = label["TRUE-ALARM"]["ALARM-DIR"] + label[
                        "OTHER-ALARMS"]["ALARM-DIR"]
                except KeyError:
                    logger_wrapper(
                        1, dir +
                        "/label.json does not contain True-Alarm or Other-Alarms. Skip this project."
                    )
                    continue
                alarm_paths = [
                    (full_dir + "/bug/sparrow-out/taint/datalog/" + alarm)
                    for alarm in alarms
                ]
                if not safty_check_patron(full_dir, alarm_paths):
                    continue
                # critical area
                os.system("mv " + full_dir +
                          "/bug/sparrow-out/taint/datalog " + full_dir +
                          "/bug/sparrow-out/taint/datalog_full")
                os.system("mkdir " + full_dir +
                          "/bug/sparrow-out/taint/datalog")
                for alarm in alarms:
                    os.system("cp -r " + full_dir +
                              "/bug/sparrow-out/taint/datalog_full/" + alarm +
                              " " + full_dir +
                              "/bug/sparrow-out/taint/datalog/")
                logger_wrapper(0, "Done separating " + full_dir)
                successed.append(dir)
    logger_wrapper(0, "Separate true alarms done.")
    logger_wrapper(0, "Failed projects: " + str(failed))
    logger_wrapper(0, "Successed projects: " + str(successed))


def safty_check_patchweave(dir, donor_alarm_paths, donee_alarm_paths):
    alarm_num = os.path.basename(dir)
    if not os.path.exists(dir):
        logger_wrapper(1, alarm_num + " does not exist. Skip this project.")
        failed.append(alarm_num)
    if not os.path.exists(dir + "/donor/bug/sparrow-out"):
        logger_wrapper(
            1, alarm_num +
            "/donor/bug/sparrow-out does not exist. Skip this project.")
        failed.append(alarm_num)
        return False
    if not os.path.exists(dir + "/donee/sparrow-out"):
        logger_wrapper(
            1, alarm_num +
            "/donee/sparrow-out does not exist. Skip this project.")
        failed.append(alarm_num)
        return False
    if not os.path.exists(dir + "/donor/bug/sparrow-out/taint/datalog"):
        logger_wrapper(
            1, alarm_num +
            "/donor/bug/sparrow-out/taint/datalog does not exist. Skip this project."
        )
        failed.append(alarm_num)
        return False
    if os.path.exists(dir + "/donor/bug/sparrow-out/taint/datalog_full"):
        logger_wrapper(
            1, alarm_num +
            "/donor/bug/sparrow-out/taint/datalog_full file already exists. Skip this project."
        )
        failed.append(alarm_num)
        return False
    if not os.path.exists(dir + "/donee/sparrow-out/taint/datalog"):
        logger_wrapper(
            1, alarm_num +
            "/donee/sparrow-out/taint/datalog does not exist. Skip this project."
        )
        failed.append(dir)
        return False
    if os.path.exists(dir + "/donee/sparrow-out/taint/datalog_full"):
        logger_wrapper(
            1, alarm_num +
            "/donee/sparrow-out/taint/datalog_full file already exists. Skip this project."
        )
        failed.append(alarm_num)
        return False
    for path in donor_alarm_paths:
        if not os.path.exists(path):
            logger_wrapper(
                1, path +
                "th alarm do not exist in the donor datalog. Skip this project."
            )
            failed.append(alarm_num)
            return False
    for path in donee_alarm_paths:
        if not os.path.exists(path):
            logger_wrapper(
                1, alarm_num + " " + path +
                "th alarm do not exist in the donee datalog. Skip this project."
            )
            failed.append(alarm_num)
            return False
    if donor_alarm_paths == []:
        logger_wrapper(
            1,
            alarm_num + ", no alarm in the donor project. Skip this project.")
        failed.append(alarm_num)
        return False
    if donee_alarm_paths == []:
        logger_wrapper(
            1,
            alarm_num + ", no alarm in the donee project. Skip this project.")
        failed.append(alarm_num)
        return False
    return True


def run_on_patchweave():
    logger_wrapper(0, "Start to separate true alarms.")
    donor_alarm_paths = []
    donee_alarm_paths = []
    for dir in os.listdir(PATCHWEAVE_BENCH_PATH):
        if dir in configuration["ID"]:
            full_dir = os.path.join(PATCHWEAVE_BENCH_PATH, dir)
            with open(os.path.join(full_dir, "label.json"), "r") as f:
                label = json.load(f)
                try:
                    donor_alarms = label["DONOR"]["TRUE-ALARM"]["ALARM-DIR"]
                    donee_alarms = label["DONEE"]["OTHER-ALARMS"]["ALARM-DIR"]
                except KeyError:
                    logger_wrapper(
                        1, dir +
                        ", no donor or donee alarms in the label file. Skip this project."
                    )
                    continue
                donor_alarm_paths = [
                    (full_dir + "/donor/bug/sparrow-out/taint/datalog/" +
                     alarm) for alarm in donor_alarms
                ]
                donee_alarm_paths = [
                    (full_dir + "/donee/sparrow-out/taint/datalog/" + alarm)
                    for alarm in donee_alarms
                ]
                if not safty_check_patchweave(full_dir, donor_alarm_paths,
                                              donee_alarm_paths):
                    continue
                os.system("mv " + full_dir +
                          "/donor/bug/sparrow-out/taint/datalog " + full_dir +
                          "/donor/bug/sparrow-out/taint/datalog_full")
                os.system("mkdir " + full_dir +
                          "/donor/bug/sparrow-out/taint/datalog")
                for alarm in donor_alarms:
                    os.system("cp -r " + full_dir +
                              "/donor/bug/sparrow-out/taint/datalog_full/" +
                              alarm + " " + full_dir +
                              "/donor/bug/sparrow-out/taint/datalog/")
                os.system("mv " + full_dir +
                          "/donee/sparrow-out/taint/datalog " + full_dir +
                          "/donee/sparrow-out/taint/datalog_full")
                os.system("mkdir " + full_dir +
                          "/donee/sparrow-out/taint/datalog")
                for alarm in donee_alarms:
                    os.system("cp -r " + full_dir +
                              "/donee/sparrow-out/taint/datalog_full/" +
                              alarm + " " + full_dir +
                              "/donee/sparrow-out/taint/datalog/")
                logger_wrapper(0, "Done separating " + full_dir)
                successed.append(dir)
    logger_wrapper(0, "Separate true alarms done.")
    logger_wrapper(0, "Failed: " + str(failed))
    logger_wrapper(0, "Successed: " + str(successed))


def main():
    logger.openings()
    parse_args()
    if configuration["BENCHMARK_SET"] == "patron":
        run_on_patron()
    elif configuration["BENCHMARK_SET"] == "PWBench":
        run_on_patchweave()
    else:
        logger_wrapper(-1, "Please specify the benchmark set")
        exit(1)


if __name__ == "__main__":
    main()

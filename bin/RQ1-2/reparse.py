#!/usr/bin/env python3

import os
import logger
import config
import argparse
import datetime
import benchmark

FILE_PATH=os.path.dirname(os.path.abspath(__file__))
ROOT_PATH=os.path.abspath(os.path.join(FILE_PATH, "..", ".."))

failed = []
successed = []

PATRON_BENCH_PATH = os.path.join(ROOT_PATH, "data", "RQ1-2", "patron")
PATCHWEAVE_BENCH_PATH = os.path.join(ROOT_PATH, "data", "RQ1-2", "PWBench")
SPARROW_BIN = os.path.join(ROOT_PATH, "sparrow", "bin", "sparrow")


def run_cil_frontend(old_path, new_path):
    return os.system(SPARROW_BIN + " -il " + old_path + " > " + new_path)


configuration = {"BENCHMARK_SET": "", "ID": None}


def parse_args():
    parser = argparse.ArgumentParser(description="Separate true alarms")
    config.configuration["PROJECT_HOME"] = os.path.dirname(
        os.path.dirname(os.path.realpath(__file__)))
    parser.add_argument("benchmark_set", type=str)
    parser.add_argument(
        "-out",
        default=os.path.join(config.configuration["PROJECT_HOME"], "out",
                             datetime.datetime.now().strftime("%Y%m%d%H%M%S")),
        help="output directory(default={}/out)".format(config.configuration["PROJECT_HOME"]),
    )
    parser.add_argument(
        "-id",
        nargs="+",
        default=[],
        help=
        "run specific id(s) of the given benchmark (e.g. -id 1,2,3       (skipping this option will run all ids))",
    )
    configuration["BENCHMARK_SET"] = parser.parse_args().benchmark_set
    config.configuration["OUT_DIR"] = parser.parse_args().out
    configuration["ID"] = parser.parse_args().id
    if configuration["ID"] == []:
        configuration["ID"] = benchmark.expriment_ready_to_go[configuration["BENCHMARK_SET"]]
    logger.logger = config.__get_logger()
    logger.log(0, "logs are saved in " + config.configuration["OUT_DIR"] + "/log.txt")
    logger.log(0, "task objectives: CIL parse the existing benchmark source code")
    logger.log(0, "target benchmark_set: " + configuration["BENCHMARK_SET"])
    logger.log(0, "target id: " + str(configuration["ID"]))
    return


def reparse_patron():
    for dir in os.listdir(PATRON_BENCH_PATH):
        if dir in configuration["ID"]:
            full_dir = os.path.join(PATRON_BENCH_PATH, dir)
            patch_dir = os.path.join(full_dir, "patch")
            old_patch_file = ""
            if not os.path.exists(os.path.join(patch_dir, "patch.c")):
                os.system("rm " + os.path.join(patch_dir, "patch.c"))
            for patch in os.listdir(patch_dir):
                if patch.endswith(".c"):
                    if patch.endswith("patch.c"):
                        os.system("rm " + os.path.join(patch_dir, patch))
                        continue
                    old_patch_file = os.path.join(patch_dir, patch)
                    break
            if old_patch_file == "":
                logger.log(1, "No patch file in " + dir)
                failed.append(dir)
                continue
            new_patch_file = os.path.join(patch_dir, "patch.c")
            if run_cil_frontend(old_patch_file, new_patch_file) != 0:
                logger.log(1, "Failed to run cil frontend for " + dir)
                failed.append(dir)
                continue
            logger.log(0, "Succeed to run cil frontend for " + dir)
            os.system("mv " + new_patch_file + " " + old_patch_file)
            successed.append(dir)


def reparse_patchweave():
    for dir in os.listdir(PATCHWEAVE_BENCH_PATH):
        if dir in configuration["ID"]:
            full_dir = os.path.join(PATCHWEAVE_BENCH_PATH, dir)
            donee_dir = os.path.join(full_dir, "donee")
            patch_dir = os.path.join(full_dir, "donor", "patch")
            old_patch_file = ""
            if not os.path.exists(os.path.join(patch_dir, "patch.c")):
                os.system("rm " + os.path.join(patch_dir, "patch.c"))
            for patch in os.listdir(patch_dir):
                if patch.endswith(".c"):
                    if patch.endswith("patch.c"):
                        os.system("rm " + os.path.join(patch_dir, patch))
                        continue
                    old_patch_file = os.path.join(patch_dir, patch)
                    break
            if old_patch_file == "":
                logger.log(1, "No patch file in " + dir)
                failed.append(dir)
                continue
            new_patch_file = os.path.join(patch_dir, "patch.c")
            if run_cil_frontend(old_patch_file, new_patch_file) != 0:
                logger.log(1, "Failed to run cil frontend for " + dir)
                failed.append(dir)
                continue
            logger.log(0, "Succeed to run cil frontend for " + dir)
            successed.append(dir)
            os.system("mv " + new_patch_file + " " + old_patch_file)
            for donee in os.listdir(donee_dir):
                if donee.endswith(".c"):
                    donee_file = os.path.join(donee_dir, donee)
                    new_donee_file = os.path.join(donee_dir, "donee.c")
                    if run_cil_frontend(donee_file, new_donee_file) != 0:
                        logger.log(1, "Failed to run cil frontend for " + donee)
                        failed.append(donee)
                        continue
                    logger.log(0, "Succeed to run cil frontend for " + donee)
                    os.system("mv " + new_donee_file + " " + donee_file)
                    successed.append(donee)


def main():
    logger.openings()
    parse_args()
    if configuration["BENCHMARK_SET"] == "patron":
        reparse_patron()
    elif configuration["BENCHMARK_SET"] == "PWBench":
        reparse_patchweave()
    else:
        logger.log(-1, "Please specify the benchmark set")
        exit(1)
    logger.log(0, "completing the task")
    logger.log(1, "@@@@@@MAKE SURE YOU MAKE THE BUGGY VERSION FROM THE PATCHED SOURCE CODE@@@@@@@")
    logger.log(
        1,
        "\tFIRST, DELETE THE BUGGY VERSION AND THEN COPY THE PATCHED SOURCE CODE TO THE BUGGY VERSION"
    )
    logger.log(1, "\tTHEN REVERT THE PATCHED PART OF THE SOURCE CODE")
    logger.log(0, "Succeed to run cil frontend for " + str(successed))
    logger.log(1, "Failed to run cil frontend for " + str(failed))


if __name__ == "__main__":
    main()

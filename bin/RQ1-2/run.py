#!/usr/bin/env python3

import os
import logger
import subprocess
import sparrow
import patron
import config
import benchmark
import datetime
import summary
from options import sparrow_options

PIPE_CODE = 0
SPARROW_CODE = 1
PATRON_CODE = 2


def run_cmd(cmd_str, shell=False):
    if shell:
        cmd_args = cmd_str
    else:
        cmd_args = cmd_str.split()
    try:
        subprocess.call(cmd_args,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        shell=shell)
    except Exception as e:
        print(e)
        exit(1)


def generate_worklist():
    processes = benchmark.load(config.configuration["args"].id,
                               config.configuration["args"].benchmark_set)
    versions = []
    sparrow_opt = []
    patron_opt = []
    benchmark_set = config.configuration["args"].benchmark_set
    for v in processes:
        target_path = os.path.join(config.configuration["BENCHMARK_DIR"],
                                   benchmark_set, v)
        patron_path = [target_path, target_path
                       ] if benchmark_set != "patchweave" else [
                           target_path + "/donor", target_path + "/donee"
                       ]
        if os.path.exists(patron_path[1] +
                          "/bug") and os.path.exists(target_path + "/patch"):
            patron_path[1] = target_path + "/bug"
        donor_path = get_file_path(v, True)
        donee_path = get_file_path(v, False)
        if donor_path is None or donee_path is None:
            donor_path = ["not ready"]
            donee_path = ["not ready"]
        if config.configuration["TARGET_PROCEDURE"] == "SPARROW":
            sparrow_opt.append(
                (config.configuration["default_sparrow_options"] + donor_path +
                 sparrow_options[benchmark_set][str(v)]))
            patron_opt.append([])
            versions.append(benchmark_set + "/" + str(v) + (
                "/donor" if benchmark_set == "patchweave" else ""))
            if benchmark_set == "patchweave":
                sparrow_opt.append(
                    (config.configuration["default_sparrow_options"] +
                     donee_path + sparrow_options[benchmark_set][str(v)]))
                patron_opt.append([])
                versions.append(benchmark_set + "/" + str(v) + (
                    "/donee" if benchmark_set == "patchweave" else ""))
        elif config.configuration["TARGET_PROCEDURE"] == "PATRON":
            label_path = os.path.join(benchmark_set, v)
            path = sparrow.get_label_dir(label_path)
            patron_option = sparrow.get_true_alarm(path)
            patron_opt.append(config.configuration["default_patron_options"] +
                              patron_path + [patron_option])
            sparrow_opt.append([])
            versions.append(benchmark_set + "/" + str(v) + (
                "/donor" if benchmark_set == "patchweave" else ""))
        else:
            label_path = os.path.join(benchmark_set, v)
            path = sparrow.get_label_dir(label_path)
            patron_option = sparrow.get_true_alarm(path)
            sparrow_opt.append(
                (config.configuration["default_sparrow_options"] +
                 sparrow_options[benchmark_set][str(v)]))
            patron_opt.append(config.configuration["default_patron_options"] +
                              patron_path + [patron_option])
            versions.append(benchmark_set + "/" + str(v) + (
                "/donor" if benchmark_set == "patchweave" else ""))

    worklist = []
    for process, s_option, patron_option in zip(versions, sparrow_opt,
                                                patron_opt):
        worklist.append((process, s_option, patron_option))
    return worklist


def fetch_works(worklist):
    works = []
    for i in range(int(config.configuration["CPU_CORE"])):
        if len(worklist) <= 0:
            break
        works.append(worklist.pop(0))
    return works


def run_seqential(works):
    tsv, file, writer = summary.open_csv()
    procs = None
    for tup in works:
        cmd, sparrow_option, patron_option = tup
        v = cmd
        if config.configuration["TARGET_PROCEDURE"] == "SPARROW":
            start_time = datetime.datetime.now()
            log, child_process = sparrow.run_sparrow(v, sparrow_option, False)
            procs = (v, log, child_process, SPARROW_CODE)
        elif config.configuration["TARGET_PROCEDURE"] == "PATRON":
            out_name = "out-{}".format(v.replace('/', '-'))
            patron_out = os.path.join(config.configuration["OUT_DIR"],
                                      out_name)
            patron_option = patron_option + ["-o", patron_out]
            start_time = datetime.datetime.now()
            child_process = patron.run_patron(v, patron_option)
            log = None
            procs = (v, log, child_process, PATRON_CODE)
        else:
            logger.log(-1, "Not implemented yet")
            log, child_process = sparrow.run_sparrow(v, sparrow_option, False)
            logger.log(0, "Wating for sparrow process to finish")
            child_process.wait()
            if patron_option == []:
                logger.log(
                    1,
                    "No patron process to run, skip this and run the next sparrow process"
                )
                continue
            child_process = patron.run_patron(v, patron_option)
            log = None
            procs = (v, log, child_process, PIPE_CODE)
        child_process.wait()
        v, log, child_process, proc_code = procs
        success = True
        if child_process.returncode != 0:
            logger.log(
                -1,
                "An error occurred while running the {} process example-{}".
                format(config.TARGET_PROCEDURE[proc_code], v),
            )
            success = False
            res = child_process.communicate()
            if res[1] is not None:
                for r in res[1].split(b"\n"):
                    logger.log(-1, r)
            else:
                is_sparrow = True if proc_code == SPARROW_CODE else False
                is_bug = None
                if is_sparrow:
                    is_bug = True
                logger.log(
                    -1,
                    "Error Message Saved in {}".format(
                        get_log_paths(v, is_sparrow, is_bug)),
                )

        if log is not None:
            log.close()
        end_time = datetime.datetime.now()
        if config.configuration["args"].t:
            exec_time = end_time - start_time
            logger.log(
                0, "Execution Time for {} process example-{} : {}".format(
                    config.TARGET_PROCEDURE[proc_code], v, exec_time))
            t = (config.TARGET_PROCEDURE[proc_code], v, exec_time, success)
            config.configuration["time_record"].append(t)
            summary.record_csv(tsv, file, writer, t)
        logger.log(
            0,
            "FINISH " + config.configuration["TARGET_PROCEDURE"] +
            " PROCESS - benchmark example-{}".format(v),
        )
    if proc_code == SPARROW_CODE and not config.configuration["args"].no_target:
        target_dir = sparrow.get_label_dir(v)
        datalog_dir = os.path.join(sparrow.get_sparrow_out_dir(v, "bug"),
                                   "taint", "datalog")
        sparrow.adjust_labels(target_dir, datalog_dir)


def run_parallel(works):
    PROCS = []
    STARTS = dict()
    for tup in works:
        cmd, sparrow_option, patron_option = tup
        v = cmd
        STARTS[v] = datetime.datetime.now()
        if config.configuration["TARGET_PROCEDURE"] == "SPARROW":
            log, child_process = sparrow.run_sparrow(v, sparrow_option, False)
            PROCS.append((v, log, child_process, SPARROW_CODE))
        elif config.configuration["TARGET_PROCEDURE"] == "PATRON":
            out_name = "out-{}".format(v.replace('/', '-'))
            patron_out = os.path.join(config.configuration["OUT_DIR"],
                                      out_name)
            patron_option = patron_option + ["-o", patron_out]
            child_process = patron.run_patron(v, patron_option)
            log = None
            PROCS.append((v, log, child_process, PATRON_CODE))
        else:
            out_name = "out-{}".format(v.replace('/', '-'))
            patron_out = os.path.join(config.configuration["OUT_DIR"],
                                      out_name)
            patron_option = patron_option + ["-o", patron_out]
            log, child_process = sparrow.run_sparrow(v, sparrow_option, True,
                                                     patron_option)
            PROCS.append((v, log, child_process, PIPE_CODE))
            log = None
    for v, log, proc, proc_code in PROCS:
        proc.wait()
        if proc.returncode != 0:
            logger.log(
                -1,
                "An error occurred while running the {} process example-{}".
                format(config.TARGET_PROCEDURE[proc_code], v),
            )
            res = proc.communicate()
            if res[1] is not None:
                for r in res[1].split(b"\n"):
                    logger.log(-1, r)
            else:
                is_sparrow = True if proc_code == SPARROW_CODE else False
                is_bug = None
                if is_sparrow:
                    is_bug = True
                logger.log(
                    -1,
                    "Error Message Saved in {}".format(
                        get_log_paths(v, is_sparrow, is_bug)),
                )
            if (config.configuration["args"].t):
                end_time = datetime.datetime.now()
                exec_time = end_time - STARTS[v]
                logger.log(
                    0, "Execution Time for {} process example-{} : {}".format(
                        config.TARGET_PROCEDURE[proc_code], v, exec_time))
                t = (config.TARGET_PROCEDURE[proc_code], v, exec_time)
                config.configuration["time_record"].append(t)

        if log is not None:
            log.close()
        logger.log(
            0,
            "FINISH " + config.configuration["TARGET_PROCEDURE"] +
            " PROCESS - benchmark example-{}".format(v),
        )
        if proc_code == SPARROW_CODE and not config.configuration[
                "args"].no_target:
            target_dir = sparrow.get_label_dir(v)
            datalog_dir = os.path.join(sparrow.get_sparrow_out_dir(v, "bug"),
                                       "taint", "datalog")
            sparrow.adjust_labels(target_dir, datalog_dir)


def get_log_paths(version, is_sparrow, is_bug=None):
    if is_sparrow:
        if is_bug is None:
            return os.path.join(
                config.configuration["PROJECT_HOME"],
                "benchmark",
                version,
                "<bug or patch>",
                "sparrow_log",
            )
        return (os.path.join(
            config.configuration["PROJECT_HOME"],
            "benchmark",
            version,
            "bug",
            "sparrow_log",
        ) if is_bug else os.path.join(
            config.configuration["PROJECT_HOME"],
            "benchmark",
            version,
            "patch",
            "sparrow_log",
        ))
    else:
        return os.path.join(
            config.configuration["OUT_DIR"],
            "out-" + version,
            "log.txt",
        )


def get_file_path(i, is_donor):
    target_dir = ""
    path = os.path.join(
        config.configuration["BENCHMARK_DIR"],
        config.configuration["args"].benchmark_set,
        i,
    )
    if config.configuration["args"].benchmark_set == "patchweave":
        if is_donor:
            path = os.path.join(path, "donor")
        else:
            path = os.path.join(path, "donee")
    for dirs in os.listdir(path):
        if dirs == "bug":
            target_dir = os.path.join(path, dirs)
    if target_dir == "":
        for f in os.listdir(path):
            if f.endswith(".c"):
                return [os.path.join(path, f)]
        logger.log(-1, "No .c file found in the directory")
    for f in os.listdir(target_dir):
        if f.endswith(".c"):
            return [os.path.join(target_dir, f)]


if __name__ == "__main__":
    logger.openings()
    config.setup()
    worklist = generate_worklist()
    if len(worklist) == 0:
        logger.log(-1, "Worklist is empty")
        exit(-1)
    if config.configuration["args"].parallel:
        logger.log(0, "Running in parallel mode")
        while len(worklist) > 0:
            works = fetch_works(worklist)
            run_parallel(works)
    else:
        logger.log(0, "Running in sequential mode(default)")
        while len(worklist) > 0:
            works = fetch_works(worklist)
            run_seqential(works)
    if config.configuration["args"].t and config.configuration["args"].parallel:
        with summary.open_csv() as (tsv, file, writer):
            for t in config.configuration["time_record"]:
                summary.record_csv(tsv, file, writer, t)
                file.flush()
                os.fsync(file.fileno())
    logger.log(0, "Closing Patrons... Good Luck!")

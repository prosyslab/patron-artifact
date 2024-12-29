import subprocess
import os
import logger
from config import configuration
import datetime, re

PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..',
                                            '..'))

try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'wb')


def parse_patron2csv(tsv, file, writer, t, cols):
    parsed_logs = []
    dir_name = os.path.join(configuration["OUT_DIR"], "out-{}".format(t[1].replace('/', '-')))
    start_time = None
    end_time = None
    preprocess_end_time = None
    match_end_time = None
    patch_start_time = None
    org_rel_num = None
    org_due_num = None
    alt_rel_num = None
    alt_due_num = None
    msg = ""
    # parsing log.txt
    with open(os.path.join(dir_name, "log.txt"), "r") as f:
        for line in f:
            match = re.match(r'\[(\d{8}-\d{2}:\d{2}:\d{2})\]\[(\w+)\]\s(.*)', line)
            if match:
                time = datetime.datetime.strptime(match.group(1), "%Y%m%d-%H:%M:%S")
                log_type = match.group(2)
                msg = match.group(3)
                parsed_logs.append((time, log_type, msg))
    for i in range(len(parsed_logs)):
        if "Starting Patron" in parsed_logs[i][2]:
            start_time = parsed_logs[i][0]
        if "Patron procedure on Donor to Donee direct transplantation" in parsed_logs[i][2]:
            end_time = parsed_logs[i][0]
        if "Preprocessing with pattern is done" in parsed_logs[i][2]:
            preprocess_end_time = parsed_logs[i][0]
        if "Try matching with ..." in parsed_logs[i][2] and "is done" in parsed_logs[i][2]:
            match_end_time = parsed_logs[i][0]
        if "Translating patch" in parsed_logs[i][2]:
            patch_start_time = parsed_logs[i][0]
        if "Original Pattern" in parsed_logs[i][2]:
            matches = re.findall(r"#Rels: (\d+), #DUEdges: (\d+)", parsed_logs[i][2])
            if matches:
                org_rel_num, org_due_num = matches[0]
        if "Alternative Pattern" in parsed_logs[i][2]:
            matches = re.findall(r"#Rels: (\d+), #DUEdges: (\d+)", parsed_logs[i][2])
            if matches:
                alt_rel_num, alt_due_num = matches[0]
    # writing both to tsv and txt files with safty checks
    if org_rel_num is None:
        org_rel_num = "X"
    if org_due_num is None:
        org_due_num = "X"
    if alt_rel_num is None:
        alt_rel_num = "X"
    if alt_due_num is None:
        alt_due_num = "X"
    if start_time is None or end_time is None or preprocess_end_time is None or match_end_time is None or patch_start_time is None:
        msg = "Error parsing Patron log, Check if {} process ended successfully".format(t[1])
        logger.log(-1, msg)
    if start_time is None or preprocess_end_time is None:
        if start_time is None:
            msg = "\tNo Patron Start Time Found in log for {}\n".format(t[1])
            logger.log(-1, msg)
            file.write(msg)
        if preprocess_end_time is None:
            msg = "\tNo Patron Preprocessing End Time Found in log for {}\n".format(t[1])
            logger.log(-1, msg)
            file.write(msg)
        preprocess_time = "X"
        file.write("\tCan't compute preprocess time\n")
    else:
        preprocess_time = (preprocess_end_time - start_time).total_seconds()
        file.write("\tPreprocessing Time: {}\n".format(preprocess_time))
    file.flush()
    os.fsync(file.fileno())
    if match_end_time is None or preprocess_end_time is None:
        if match_end_time is None:
            msg = "\tNo Patron Match Time Found in log for {}\n".format(t[1])
            logger.log(-1, msg)
            file.write(msg)
        if preprocess_end_time is None:
            msg = "\tNo Patron Preprocessing End Time Time Found in log for {}\n".format(t[1])
            logger.log(-1, msg)
            file.write(msg)
        match_time = "X"
        file.write("\tCan't compute match time\n")
    else:
        match_time = (match_end_time - preprocess_end_time).total_seconds()
        file.write("\tMatching Time: {}\n".format(match_time))
    file.flush()
    os.fsync(file.fileno())
    if end_time is None or patch_start_time is None:
        if end_time is None:
            msg = "\tNo Patron End Time Found in log for {}\n".format(t[1])
            logger.log(-1, msg)
            file.write("\tNo Patron End Time Found in log\n")
        if patch_start_time is None:
            msg = "\tNo Patron Patch Translation Start Time Found in log for {}\n".format(t[1])
            logger.log(-1, msg)
            file.write(msg)
        patch_time = "X"
        file.write("\tCan't compute patch translation time\n")
    else:
        patch_time = (end_time - patch_start_time).total_seconds()
        file.write("\tPatch Translation Time: {}\n".format(patch_time))
    file.flush()
    os.fsync(file.fileno())
    all_cols = cols + [
        preprocess_time,
        match_time,
        patch_time,
        org_rel_num,
        org_due_num,
        alt_rel_num,
        alt_due_num,
    ]
    if not any(s.endswith(".patch") for s in os.listdir(dir_name)):
        all_cols[1] = "X"
    writer.writerow(all_cols)
    file.flush()
    os.fsync(file.fileno())
    tsv.flush()
    os.fsync(tsv.fileno())
    return


def run_patron(version, options):
    timeout = str(configuration["TIMEOUT"])
    if 'not ready' in options:
        logger.log(-1, "Patron is not ready on example-{}".format(version))
        return None
    logger.log(
        0, "Running patron on example-{}".format(version) + "\n\twith options:{}".format(options))
    os.chdir(os.path.join(PROJECT_HOME, 'patron'))
    return subprocess.Popen(["timeout", timeout] + [configuration["PATRON_BIN_PATH"]] + options,
                            stdout=DEVNULL,
                            stderr=subprocess.PIPE)

import subprocess
import os
import shutil
import logger
import json
from config import configuration
import time

try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'wb')


def get_true_alarm(label_path):
    label = {}
    try:
        with open(os.path.join(label_path, 'label.json'), 'r') as f:
            label = json.load(f)
    except FileNotFoundError:
        return ['not ready']
    try:
        ret = label["DONOR"]["TRUE-ALARM"]["ALARM-DIR"][0]
    except KeyError or IndexError:
        try:
            ret = label["TRUE-ALARM"]["ALARM-DIR"][0]
        except KeyError or IndexError:
            ret = ['not ready']
    return ret


def adjust_labels(label_path, datalog_path):
    label = {}
    new_true_dir = []
    new_other_dir = []
    new_true_sym = []
    new_other_sym = []
    is_patchweave = False
    with open(os.path.join(label_path, 'label.json'), 'r') as f:
        label = json.load(f)
    try:
        true_loc = label["DONOR"]["TRUE-ALARM"]["ALARM-LOC"]
        other_loc = label["DONEE"]["OTHER-ALARMS"]["ALARM-LOC"]
        true_exp = label["DONOR"]["TRUE-ALARM"]["ALARM-EXP"]
        other_exp = label["DONEE"]["OTHER-ALARMS"]["ALARM-EXP"]
        is_patchweave = True
    except KeyError:
        true_loc = label["TRUE-ALARM"]["ALARM-LOC"]
        other_loc = label["OTHER-ALARMS"]["ALARM-LOC"]
        true_exp = label["TRUE-ALARM"]["ALARM-EXP"]
        other_exp = label["OTHER-ALARMS"]["ALARM-EXP"]
    true_datalog_path = datalog_path
    other_datalog_path = datalog_path
    if is_patchweave:
        other_datalog_path = str(datalog_path).replace("donor", "donee").replace("bug/", "")
    delay_counter = 1
    while not os.path.isfile(os.path.join(true_datalog_path, "Alarm.map")):
        logger.log(
            -1,
            os.path.join(true_datalog_path, "Alarm.map") +
            " has not been created yet due to I/O delay. waiting for 10 more sec. ({}th try)".
            format(str(delay_counter)))
        delay_counter += 1
        time.sleep(10)
    with open(os.path.join(true_datalog_path, "Alarm.map"), 'r') as f:
        alarm_map = f.readlines()
        alarm_map = [line.strip().split('\t') for line in alarm_map]
        for tl, te in zip(true_loc, true_exp):
            for line in alarm_map:
                if line[0].strip() == str(tl).strip() and line[1].strip() == str(te).strip():
                    new_true_sym.append(line[2])
        for new_sym in new_true_sym:
            for root, dirs, files in os.walk(true_datalog_path):
                for file in files:
                    if file == "SparrowAlarm.facts":
                        with open(os.path.join(root, file), 'r') as f:
                            if new_sym in f.read():
                                new_true_dir.append(root)
    delay_counter = 1
    while not os.path.isfile(os.path.join(other_datalog_path, "Alarm.map")):
        logger.log(
            -1,
            os.path.join(other_datalog_path, "Alarm.map") +
            " has not been created yet due to I/O delay. waiting for 10 more sec. ({}th try)".
            format(str(delay_counter)))
        delay_counter += 1
        time.sleep(10)
    with open(os.path.join(other_datalog_path, "Alarm.map"), 'r') as f:
        alarm_map = f.readlines()
        alarm_map = [line.strip().split('\t') for line in alarm_map]
        for ol, oe in zip(other_loc, other_exp):
            for line in alarm_map:
                if line[0].strip() == str(ol).strip() and line[1].strip() == str(oe).strip():
                    new_other_sym.append(line[2])
        for new_sym in new_other_sym:
            for root, dirs, files in os.walk(other_datalog_path):
                for file in files:
                    if file == "SparrowAlarm.facts":
                        with open(os.path.join(root, file), 'r') as f:
                            if new_sym in f.read():
                                new_other_dir.append(root)
        if len(new_true_dir) != len(new_true_sym) or len(new_other_dir) != len(new_other_sym):
            logger.log(
                -1,
                "ERROR in adjusting labels, ALARM-DIR and ALARM-SYMBOL don't match. PLEASE manually adjust the label for the {}."
                .format(label_path))
            return
        if not is_patchweave and (len(new_true_dir) == 0 or len(new_other_dir) == 0
                                  or len(new_true_sym) == 0 or len(new_other_sym) == 0):
            logger.log(
                -1,
                "ERROR in adjusting labels, Some field is empty. PLEASE manually adjust the label for the {}."
                .format(label_path))
            return
        if is_patchweave and (len(new_true_dir) == 0 or len(new_true_sym)
                              == 0) and (len(new_other_dir) == 0 or len(new_other_sym) == 0):
            logger.log(
                -1,
                "ERROR in adjusting labels, Some field is empty. PLEASE manually adjust the label for the {}."
                .format(label_path))
            return
        if is_patchweave:
            if len(new_true_dir) != 0 and (len(label["DONOR"]["TRUE-ALARM"]["ALARM-DIR"]) == 0
                                           or label["DONOR"]["TRUE-ALARM"]["ALARM-DIR"]
                                           != [os.path.basename(ntd) for ntd in new_true_dir]):
                label["DONOR"]["TRUE-ALARM"]["ALARM-DIR"] = [
                    os.path.basename(ntd) for ntd in new_true_dir
                ]
                label["DONOR"]["TRUE-ALARM"]["ALARM-SYMBOL"] = new_true_sym
            if len(new_other_dir) != 0 and (len(label["DONEE"]["OTHER-ALARMS"]["ALARM-DIR"]) == 0
                                            or label["DONEE"]["OTHER-ALARMS"]["ALARM-DIR"]
                                            != [os.path.basename(nod) for nod in new_other_dir]):
                label["DONEE"]["OTHER-ALARMS"]["ALARM-DIR"] = [
                    os.path.basename(nod) for nod in new_other_dir
                ]
                label["DONEE"]["OTHER-ALARMS"]["ALARM-SYMBOL"] = new_other_sym
        else:
            label["TRUE-ALARM"]["ALARM-DIR"] = [os.path.basename(ntd) for ntd in new_true_dir]
            label["OTHER-ALARMS"]["ALARM-DIR"] = [os.path.basename(nod) for nod in new_other_dir]
            label["TRUE-ALARM"]["ALARM-SYMBOL"] = new_true_sym
            label["OTHER-ALARMS"]["ALARM-SYMBOL"] = new_other_sym
    with open(os.path.join(label_path, 'label.json'), 'w') as f:
        json.dump(label, f, indent=4)
    logger.log(0, "labels are overwritten for the {}.".format(label_path))
    return


def get_target_loc(path):
    out = []
    with open(os.path.join(path, "label.json"), 'r') as f:
        label = json.load(f)
        try:
            donor_locs = label["DONOR"]["TRUE-ALARM"]["ALARM-LOC"]
            donee_locs = label["DONEE"]["OTHER-ALARMS"]["ALARM-LOC"]
            locs = donor_locs + donee_locs
        except KeyError:
            true_loc = label["TRUE-ALARM"]["ALARM-LOC"]
            other_loc = label["OTHER-ALARMS"]["ALARM-LOC"]
            locs = true_loc + other_loc
        if len(locs) == 0:
            return locs
        for loc in locs:
            out.append("-target_loc")
            out.append(loc)
        return out


def get_label_dir(version):
    label_path = os.path.join(configuration['PROJECT_HOME'], 'data/RQ1-2/{}'.format(version))
    if os.path.basename(label_path) == "donor" or os.path.basename(label_path) == "donee":
        label_path = os.path.dirname(label_path)
    if os.path.basename(label_path) == "bug":
        label_path = os.path.dirname(os.path.dirname(label_path))
    return label_path


def get_sparrow_out_dir(version, target):
    if os.path.isdir(
            os.path.join(configuration['PROJECT_HOME'], 'data/RQ1-2/{}/{}/'.format(version,
                                                                                  target))):
        target_path = os.path.join(configuration['PROJECT_HOME'],
                                   'data/RQ1-2/{}/{}/'.format(version, target))
    else:
        target_path = os.path.join(configuration['PROJECT_HOME'], 'data/RQ1-2/{}'.format(version))
    return os.path.join(target_path, 'sparrow-out')


def run_sparrow(version, options, is_pipe):
    pat_options = []
    target = 'bug'
    if not configuration['args'].no_target:
        label_path = get_label_dir(version)
        target_locs = get_target_loc(label_path)
        if set(pat_options) >= set(target_locs):
            target_locs = []
        pat_options += target_locs
    if configuration['args'].no_target:
        pat_options = []
    if is_pipe:
        logger.log(
            1,
            "YOU ARE RUNNING PIPE-MODE and PARALLEL MODE at the same time!!! ALL ERRORS WILL BE RECORDED in sparrow_log"
        )
    logger.log(
        0, "SPARROW ANALYSIS on {} version of example-{}".format(target, version) +
        "\n\twith options:{}".format(options + pat_options))
    if os.path.isdir(
            os.path.join(configuration['PROJECT_HOME'], 'data/RQ1-2/{}/{}/'.format(version,
                                                                                  target))):
        os.chdir(
            os.path.join(configuration['PROJECT_HOME'], 'data/RQ1-2/{}/{}/'.format(version, target)))
    else:
        os.chdir(os.path.join(configuration['PROJECT_HOME'], 'data/RQ1-2/{}'.format(version)))
    if not configuration['args'].mute:
        log = open('sparrow_log', 'w')
    else:
        log = DEVNULL
    if 'not ready' in options:
        logger.log(-1, "SPARROW is not ready on {} version of example-{}".format(target, version))
        return log, None
    if os.path.isdir('sparrow-out'):
        shutil.rmtree('sparrow-out')
        logger.log(0, "sparrow-out already EXISTS! Removed old sparrow-out directory")

    return log, subprocess.Popen([configuration["SPARROW_BIN_PATH"]] + options + pat_options,
                                 stdout=log,
                                 stderr=subprocess.STDOUT)

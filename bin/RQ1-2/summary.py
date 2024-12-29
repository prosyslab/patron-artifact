import config
import os
import patron
import csv
import datetime

prev_record_sparrow = None
duplicate_check = False


def open_csv():
    global duplicate_check
    tsvfile = open(
        os.path.join(config.configuration["OUT_DIR"],
                     "summary_{}.tsv".format(config.configuration["TARGET_PROCEDURE"])), "a")
    txtfile = open(
        os.path.join(config.configuration["OUT_DIR"],
                     "summary_hum_{}.txt".format(config.configuration["TARGET_PROCEDURE"])), "a")
    writer = csv.writer(tsvfile, delimiter='\t', lineterminator='\n')
    columns = ["Project", "Success?"]
    if config.configuration["TARGET_PROCEDURE"] == "PATRON":
        columns += [
            "Total Time", "Preprocess Time", "Match Time", "Patch Time", "Original Rel #",
            "Original DUE #", "Alt. Rel #", "Alt. DUE #,"
        ]
    else:
        columns += ["Donor Time", "Donee Time"]
    if not duplicate_check:
        writer.writerow(columns)
        tsvfile.flush()
        os.fsync(tsvfile.fileno())
    duplicate_check = True
    return tsvfile, txtfile, writer


def parse_time_from_log(line):
    return datetime.datetime.strptime(line.split("[")[1].split("]")[0], "%Y%m%d-%H:%M:%S")


def get_log_time(log_file):
    with open(log_file, "r") as f:
        lines = f.readlines()
    start_time = None
    end_time = None
    for line in lines:
        if "Starting Patron..." in line:
            start_time = parse_time_from_log(line)
        if "Successfully applied" in line:
            end_time = parse_time_from_log(line)
    return str(end_time - start_time)


def double_check(out_dir, info):
    info_lst = info[1].split("/")
    if info_lst[-1] == "donor":
        target_dir = os.path.join(out_dir, "out-PWBench-" + info_lst[-2] + "-" + info_lst[-1])
    else:
        target_dir = os.path.join(out_dir, "out-patron-" + info_lst[-1])
    patron_out = os.listdir(target_dir)
    if any([f.startswith("result__") for f in patron_out]):
        new_time = get_log_time(os.path.join(target_dir, "log.txt"))
        return "O", "Experiment Success(Check Required)", new_time
    else:
        return "X", "Experiment Failed", "NO_TIME_RECORDED"


def record_csv(tsv, file, writer, t):
    global prev_record_sparrow
    target_info = t[1].split("/")
    if len(target_info) == 3:
        donor_or_donee = target_info[2]
    else:
        donor_or_donee = None
    case_num = '-'.join(target_info[:2])
    if t[3]:
        is_success = "O"
        return_code = "Experiment Success"
        time_taken = str(t[2].total_seconds())
    else:
        is_success, return_code, new_time = double_check(config.configuration["OUT_DIR"], t)
        time_taken = new_time
    file.write("{} - {} - {}\n".format(t[0], t[1], time_taken, return_code))
    file.flush()
    os.fsync(file.fileno())
    if config.configuration["TARGET_PROCEDURE"] == "PATRON":
        patron.parse_patron2csv(tsv, file, writer, t, [case_num, is_success, time_taken])
    if config.configuration["TARGET_PROCEDURE"] == "SPARROW":
        if donor_or_donee is not None:
            if prev_record_sparrow is None or prev_record_sparrow[1] != case_num:
                prev_record_sparrow = (donor_or_donee, case_num, is_success, time_taken)
                return
            elif prev_record_sparrow[1] == case_num:
                if donor_or_donee == "donor":
                    writer.writerow([case_num, is_success, time_taken, prev_record_sparrow[3]])
                else:
                    writer.writerow([case_num, is_success, prev_record_sparrow[3], time_taken])
                tsv.flush()
                os.fsync(tsv.fileno())
        else:
            writer.writerow([case_num, is_success, time_taken, time_taken])
            tsv.flush()
            os.fsync(tsv.fileno())

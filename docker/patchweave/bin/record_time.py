#!/usr/bin/env python3

import csv
import os
import sys

FILE_PATH = os.path.dirname(os.path.abspath(__file__))

def parse_time_duration(data_rows):
  time_duration = dict()
  for row in data_rows:
    if "Initialization" in row:
      time_duration["Initialization"] = row.split(":")[1].strip().split("seconds")[0].strip()
    if "Build" in row:
      time_duration["Build"] = row.split(":")[1].strip().split("seconds")[0].strip()
    if "Diff Analysis" in row:
      time_duration["Diff Analysis"] = row.split(":")[1].strip().split("seconds")[0].strip()
    if "Trace Analysis" in row:
      time_duration["Trace Analysis"] = row.split(":")[1].strip().split("seconds")[0].strip()
    if "Symbolic Trace Analysis" in row:
      time_duration["Symbolic Trace Analysis"] = row.split(":")[1].strip().split("seconds")[0].strip()
    if "Slicing" in row:
      time_duration["Slicing"] = row.split(":")[1].strip().split("seconds")[0].strip()
    if "Transplantation" in row:
      time_duration["Transplantation"] = row.split(":")[1].strip().split("seconds")[0].strip()
    if "Verification" in row:
      time_duration["Verification"] = row.split(":")[1].strip().split("seconds")[0].strip()
    if "PatchWeave" in row:
      time_duration["Total"] = row.split("after")[1].strip().split("seconds")[0].strip()  
  return time_duration

def run(log_dir_path):
  fp = open("time_duration.tsv", "w")
  writer = csv.writer(fp, delimiter='\t')
  writer.writerow(["Title", "Initilization", "Build", "Diff Analysis", "Trace Analysis", "Symbolic Trace Analysis", "Slicing", "Transplantation", "Verification", "Total"])
  fp.flush()
  files = os.listdir(log_dir_path)
  for file in files:
      if not file.startswith("log-"):
          continue
      if not file[4].isdigit():
          continue
      title = file[4:]
      log_file = os.path.join(log_dir_path, file)
      with open(log_file, "r") as f:
          lines = f.readlines()
          idx = -1
          for i in range(len(lines) - 1, -1, -1):
              line = lines[i]
              if "Time duration" in line:
                  idx = i + 2
          if idx == -1:
              print("Error: no time duration found in log file " + title)
              writer.writerow([title, "X", "X", "X", "X", "X", "X", "X", "X", "X"])
              fp.flush()
              continue
          data_rows = lines[idx:]
          data = parse_time_duration(data_rows)
          for key in data:
            if key not in ["Initialization", "Build", "Diff Analysis", "Trace Analysis", "Symbolic Trace Analysis", "Slicing", "Transplantation", "Verification", "Total"]:
              print("Error: unknown key in time duration")
              writer.writerow([title, "?", "?", "?", "?", "?", "?", "?", "?", "?"])
              fp.flush()
              continue
          writer.writerow([title, data["Initialization"], data["Build"], data["Diff Analysis"], data["Trace Analysis"], data["Symbolic Trace Analysis"], data["Slicing"], data["Transplantation"], data["Verification"], data["Total"]])
          fp.flush()
          
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python extract_times.py <log_dir>")
        sys.exit(1)
      
    log_dir = sys.argv[1]
    if not os.path.exists(log_dir):
        print("Error: log directory does not exist")
        sys.exit(1)
    log_path = os.path.abspath(log_dir)
    run(log_path)

#!/usr/bin/env python3
import sys
import datetime
import os
import re
import time
import csv
PIPE_MODE = 1
PATCH_MODE = 2

def parse_build(package, lines):
  for i in range(len(lines)):
    mode, time, msg = lines[i]
    if "Building" in msg and "has succeded" in msg and package in msg:
      return time
  return None

def parse_combine(package, lines):
  for i in range(len(lines)):
    mode, time, msg = lines[i]
    if "Combining" in msg and "was successful" in msg and package in msg:
      return time
    if "No package was combined." in msg:
      return time
  return None

def parse_binary(file, lines):
  for i in range(len(lines)):
    mode, time, msg = lines[i]
    if "Failed to analyze" in msg and file in msg:
      return None
    elif "is successfully analyzed." in msg and file in msg:
      return time
  return None

def parse_sparrow(package, lines, record):
  record[package] = dict()
  for i in range(len(lines)):
    mode, time, msg = lines[i]
    if "Running sparrow for" in msg and "..." in msg:
      file = msg.split(' ')[-2].split('/')[-1]
      sparrow_start = time
      sparrow_end = parse_binary(file, lines[i:])
      if sparrow_end is None:
        record[package][file] = "-"
      else:
        record[package][file] = str((sparrow_end - sparrow_start).total_seconds())
    if "files are successfully analyzed" in msg or "No file is successfully analyzed." in msg:
      return record
  return record

def parse_pipe_log(lines):
  build_record = dict()
  combine_record = dict()
  sparrow_record = dict()
  for i in range(len(lines)):
    mode, time, msg = lines[i]
    if "Building" in msg and "..." in msg:
      build_package = msg.split(' ')[1]
      build_start = time
      build_end = parse_build(build_package, lines[i:])
      if build_end is None:
        build_record[build_package] = "-"
      else:
        build_record[build_package] = str((build_end - build_start).total_seconds())
    if "Beginning to Combine" in msg:
      combine_package = msg.split(' ')[3][1:-1]
      combine_start = time
      combine_end = parse_combine(combine_package, lines[i:])
      if combine_end is None:
        combine_record[combine_package] = "-"
      else:
        combine_record[combine_package] = str((combine_end - combine_start).total_seconds())
    if "Found" in msg and ".c files":
      sparrow_package = msg.split(' ')[-1].split('/')[-1].replace('.', '')
      sparrow_record = parse_sparrow(sparrow_package, lines[i:], sparrow_record)
  return build_record, combine_record, sparrow_record

def write_pipe_log(record, out_path):
  build_record, combine_record, sparrow_record = record
  with open(os.path.join(out_path, 'build_time.tsv'), 'w') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(['Package', 'Time'])
    f.flush()
    for package, time in build_record.items():
      writer.writerow([package, time])
      f.flush()
  with open(os.path.join(out_path, 'combine_time.tsv'), 'w') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(['Package', 'Time'])
    f.flush()
    for package, time in combine_record.items():
      writer.writerow([package, time])
      f.flush()
  with open(os.path.join(out_path, 'sparrow_time.tsv'), 'w') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(['Package', 'File', 'Time'])
    f.flush()
    for package, files in sparrow_record.items():
      for file, time in files.items():
        writer.writerow([package, file, time])
        f.flush()

def parse_patch(lines, file):
  for i in range(len(lines)):
    mode, time, msg = lines[i]
    if "Failed to run patron with" in msg and file in msg:
      return None
    elif "Successfully ran patron with" in msg and file in msg:
      return time
  return None

def parse_patch_log(lines):
  patch_record = dict()
  for i in range(len(lines)):
    mode, time, msg = lines[i]
    if "Running patron with" in msg:
      m = re.search(r'\[.*\]', msg).group(0)
      if m:
        args = m[1:-1].split(', ')[2].replace("'", "").split('/')
        package_name = args[-2]
        file_name = args[-1]
        if 'analysis_target_' in package_name:
          package_name = file_name
        patch_start = time
        patch_end = parse_patch(lines[i:], file_name)
        patch_record[package] = dict()
        patch_record[package][file] = str((patch_end - patch_start).total_seconds())
  return patch_record

def write_patch_log(record, out_path):
  with open(os.path.join(out_path, 'patch_time.tsv'), 'w') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(['Package', 'File', 'Time'])
    f.flush()
    for package, files in record.items():
      for file, time in files.items():
        writer.writerow([package, file, time])
        f.flush()

def run(log_file, mode, out_path):
  with open(log_file, 'r') as f:
    lines = f.readlines()
  parsed_lines = []
  for line in lines:
    m = re.match(r'\[(\w+)\]\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\] (.*)', line)
    if m:
      t = datetime.datetime.strptime(m.group(2), '%Y-%m-%d %H:%M:%S,%f')
      parsed_lines.append((m.group(1), t, m.group(3)))
  if mode == PIPE_MODE:
    write_pipe_log(parse_pipe_log(parsed_lines), out_path)
  else:
    write_patch_log(parse_patch_log(parsed_lines), out_path)

def run_from_top(out_path, mode):
  for file in os.listdir(out_path):
    if file.endswith('.txt') and file.startswith('log_'):
      run(os.path.join(out_path, file), mode, out_path)
      break

def main():
  if len(sys.argv) != 2:
    print("Usage: ./measure_time.py [log.txt]")
    sys.exit(1)
  CWD=os.getcwd()
  log = sys.argv[1]
  log_parent = os.path.dirname(log)
  mode = PIPE_MODE if "_pipe" in log_parent else PATCH_MODE
  log_file = os.path.join(CWD, sys.argv[1])
  ROOT_PATH = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
  OUT_PATH = os.path.join(ROOT_PATH, 'out', datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '_time')
  if not os.path.exists(OUT_PATH):
    os.makedirs(OUT_PATH)
  run(log_file, mode, OUT_PATH)
  
if __name__ == '__main__':
    main()
#!/usr/bin/env python3
import os, sys, argparse, subprocess
import logger as L
import config
import progressbar

FILE_PATH=os.path.dirname(__file__)
ROOT_PATH=os.path.abspath(os.path.join(FILE_PATH, ".."))
local_config = {
  "IS_SCRATCH": False,
  "DB_PATHS":[],
  "DONOR_PATHS":dict()
}

def run_process(cmd):
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = p.communicate()
  return out, err

def mk_exp_dbs():
  L.log(L.ALL, "Running the python.py script for constructing benchmark DB")
  first_out, first_err = run_process(['python3', os.path.join(FILE_PATH, 'patron.py'), '-db'])
  if first_err:
    L.log(L.ERROR, "Error: {}".format(first_err))
    sys.exit(1)
  for line in first_out.decode().split("\\n"):
    L.log(L.INFO, line)
  L.log(L.ALL, 'First run done (benchmark DB)')
  L.log(L.ALL, "Running the python.py script for constructing juliet DB")
  second_out, second_err = run_process(['python3', os.path.join(FILE_PATH, 'patron.py'), '-db', '-donorpath', 'data/CWE-patches'])
  if second_err:
    L.log(L.ERROR, "Error: {}".format(second_err))
    sys.exit(1)
  for line in second_out.decode().split("\\n"):
    L.log(L.INFO, line)
  L.log(L.ALL, 'Second run done (juliet DB)')
  L.log(L.ALL, "Running the python.py script for constructing CVE DB")
  third_out, third_err = run_process(['python3', os.path.join(FILE_PATH, 'patron.py'), '-db', '-donorpath', 'data/CVE-patches'])
  if third_err:
    L.log(L.ERROR, "Error: {}".format(third_err))
    sys.exit(1)
  for line in third_out.decode().split("\\n"):
    L.log(L.INFO, line)
  L.log(L.ALL, 'Third run done (CVE DB)')
  

def run():
  for path in local_config['DB_PATHS']:
    path = os.path.abspath(path)
    if not os.path.exists(path):
      L.log(L.ALL, "Path does not exist: {}".format(path))
      sys.exit(1)
    if not os.path.isdir(path):
      L.log(L.ALL, "Path is not a directory: {}".format(path))
      sys.exit(1)
    for cont in os.listdir(path):
      cont_path = os.path.join(path, cont)
      if not cont in local_config['DONOR_PATHS']:
        local_config['DONOR_PATHS'][cont] = []
      local_config['DONOR_PATHS'][cont] = local_config['DONOR_PATHS'][cont] + [ os.path.join(cont_path, f) for f in os.listdir(cont_path) ]
  os.makedirs(os.path.join(ROOT_PATH, "combined-DB"), exist_ok=True)
  for key, value in local_config['DONOR_PATHS'].items():
    os.makedirs(os.path.join(ROOT_PATH, "combined-DB", key), exist_ok=True)
    for f in value:
      if os.path.exists(os.path.join(ROOT_PATH, "combined-DB", key, os.path.basename(f))):
        L.log(L.ALL, "File already exists: {}".format(f))
        continue
      else:
        os.system("cp -rf {} {}".format(f, os.path.join(ROOT_PATH, "combined-DB", key)))
      

if __name__ == "__main__":
  L.logger = config.__get_logger("MERGE")
  if sys.argv[1] == "-s" or sys.argv[1] == "--scratch":
    local_config['IS_SCRATCH'] = True
    mk_exp_dbs()
    local_config["DB_PATHS"] = ["CVE-patches-DB", "CWE-patches-DB", "benchmark-DB"]
  else:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("db_path", nargs="+", help="Path to the database")
    args = arg_parser.parse_args()
    local_config['DB_PATHS'] = args.db_path
    L.log(L.ALL, "DB_PATHS: {}".format(local_config['DB_PATHS']))
  run()
  L.log(L.ALL, "Merging is complete!")

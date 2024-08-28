#!/usr/bin/env python3
import os, sys, argparse, subprocess

FILE_PATH=os.path.dirname(__file__)
ROOT_PATH=os.path.abspath(os.path.join(FILE_PATH, ".."))
config = {
  "IS_SCRATCH": False,
  "DB_PATHS":[],
  "DONOR_PATHS":dict()
}

def run_process(cmd):
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = p.communicate()
  return out, err

def mk_exp_dbs():
  first_out, first_err = run_process([FILE_PATH + 'patron.py', '-db'])
  if first_err:
    print("Error: {}".format(first_err))
    sys.exit(1)
  print('First run done (benchmark DB)')
  second_out, second_err = run_process([FILE_PATH + 'patron.py', '-db', '-donorpath', 'data/CWE-patches'])
  if second_err:
    print("Error: {}".format(second_err))
    sys.exit(1)
  print('Second run done (juliet DB)')
  third_out, third_err = run_process([FILE_PATH + 'patron.py', '-db', '-donorpath', 'data/CVE-patches'])
  if third_err:
    print("Error: {}".format(third_err))
    sys.exit(1)
  print('Third run done (CVE DB)')
  

def run():
  for path in config['DB_PATHS']:
    path = os.path.abspath(path)
    if not os.path.exists(path):
      print("Path does not exist: {}".format(path))
      sys.exit(1)
    if not os.path.isdir(path):
      print("Path is not a directory: {}".format(path))
      sys.exit(1)
    for cont in os.listdir(path):
      cont_path = os.path.join(path, cont)
      # check if key exists
      if not cont in config['DONOR_PATHS']:
        config['DONOR_PATHS'][cont] = []
      config['DONOR_PATHS'][cont] = config['DONOR_PATHS'][cont] + [ os.path.join(cont_path, f) for f in os.listdir(cont_path) ]
  os.makedirs(os.path.join(ROOT_PATH, "combined-DB"), exist_ok=True)
  for key, value in config['DONOR_PATHS'].items():
    os.makedirs(os.path.join(ROOT_PATH, "combined-DB", key), exist_ok=True)
    for f in value:
      os.system("cp -rf {} {}".format(f, os.path.join(ROOT_PATH, "combined-DB", key)))
      

if __name__ == "__main__":
  if sys.argv[1] == "-s" or sys.argv[1] == "--scratch":
    config['IS_SCRATCH'] = True
    mk_exp_dbs()
    config.DB_PATHS = ["..-DB"] # TODO: Check the path to the DB after the test
  else:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("db_path", nargs="+", help="Path to the database")
    args = arg_parser.parse_args()
    config['DB_PATHS'] = args.db_path
    print("DB_PATHS: {}".format(config['DB_PATHS']))
  run()

#!/usr/bin/env python3
import json
import sys
import os

FILE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run(pattern_file, datalog_dir):
    if not os.path.exists(datalog_dir) or not os.path.isdir(datalog_dir):
        print("Invalid datalog directory")
        return
    if not os.path.exists(pattern_file) or not os.path.isfile(pattern_file):
        print("Invalid pattern file")
        return
    with open(pattern_file, "r") as f:
        pat_lines = f.readlines()
    node_json = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(datalog_dir))), "node.json")
    with open(node_json, "r") as f:
        node_data = json.load(f)["nodes"]
    with open(os.path.join(datalog_dir, "Exp.map"), "r") as f:
      exp_data = dict()
      raw_exp = [ line.strip().split("\t") for line in f.readlines() ]
      exp_data = { line[0]: line[1] for line in raw_exp }
    with open(os.path.join(datalog_dir, "Lval.map"), "r") as f:
      lval_data = dict()
      raw_lval = [ line.strip().split("\t") for line in f.readlines() ]
      lval_data = { line[0]: line[1] for line in raw_lval }
    with open(os.path.join(datalog_dir, "LibCallExp.facts"), "r") as f:
      libcall_data = dict()
      raw_libcall = [ line.strip().split("\t") for line in f.readlines() ]
      libcall_data = { line[0]: line[1] for line in raw_libcall }
    with open(os.path.join(datalog_dir, "ReadCallExp.facts"), "r") as f:
      readcall_data = dict()
      raw_readcall = [ line.strip().split("\t") for line in f.readlines() ]
      readcall_data = { line[0]: line[1] for line in raw_readcall }
    with open(os.path.join(FILE_PATH, "out", "pattern_translation.chc"), "w") as f:
        f.write("=================ORIGINAL==================\n")
        for line in pat_lines:
            f.write(line)
        f.write("\n")
        f.write("=================TRANSLATED==================\n")
        for line in pat_lines:
          is_continue = False
          line = line.strip().replace(")", "").replace("(", "").replace(",", "").split(" ")
          f.write("(")
          for comp in line:
            if comp == '<-':
              f.write(") <- \n")
              is_continue = True
              break
            if comp in node_data:
              f.write(str(node_data[comp]['cmd']) + " ")
            elif comp in exp_data:
              f.write(str(exp_data[comp]) + " ")
            elif comp in lval_data:
              f.write(str(lval_data[comp]) + " ")
            elif comp in libcall_data:
              f.write(str(libcall_data[comp]) + " ")
            elif comp in readcall_data:
              f.write(str(readcall_data[comp]) + " ")
            else:
              f.write(comp + " ")
          if is_continue:
            f.write("===================\n")
            continue
          f.write(")\n")
          f.write("===================\n")        
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pattern_translator.py <pattern.chc> <datalog_dir>")
        exit(1)
    pattern_file = os.path.abspath(sys.argv[1])
    datalog_dir = os.path.abspath(sys.argv[2])
    run(pattern_file, datalog_dir)
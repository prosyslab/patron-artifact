import os
import sys
import re

FILE_PATH = os.path.dirname(os.path.abspath(__file__))
BUILT_PATH = os.path.join(FILE_PATH, 'built')
TEST = os.path.join(BUILT_PATH, 'CWE121_Stack_Based_Buffer_Overflow__char_type_overrun_memcpy_01')
bug_file = os.path.join(TEST, 'bug.i')
patch_file = os.path.join(TEST, 'patch.i')
OUT_DIR = os.path.join(FILE_PATH, 'out')
def lexical_func_parse(flines):
  bracket_cnt = 0
  in_func = False
  functions = []
  func_contents = []
  start_line = -1
  for i in range(len(flines)):
    line = flines[i]
    if in_func:
      func_contents.append(line)
    if '{' in line and '}' in line:
      continue
    if '{' in line:
      if bracket_cnt == 0:
        if '(' in flines[i-1] and ')' in flines[i-1] and not ';' in line:
          in_func = True
          start_line = i
          func_name = flines[i-1].split('(')[0].split(' ')[-1]
      if in_func:
        bracket_cnt += 1
      continue
    if '}' in line:
      if start_line != -1:
        bracket_cnt -= 1
        if bracket_cnt == 0:
          in_func = False
          end_line = i
          functions.append((start_line, end_line, func_name, func_contents))
          func_contents = []
          start_line = -1
      continue
  return functions

def get_xor_funcs(funcs1, funcs2):
  xor_set = []
  for start1, end1, name1, contents1 in funcs1:
    if 'main' in name1:
      continue
    same = False
    for start2, end2, name2, contents2 in funcs2:
      if name1 == name2 or contents1 == contents2:
        same = True
        break
    if not same:
      xor_set.append((start1, end1, name1, contents1))
  return xor_set

def get_and_funcs(funcs1, funcs2):
  and_set = []
  for start1, end1, name1, contents1 in funcs1:
    for start2, end2, name2, contents2 in funcs2:
      if contents1 == contents2:
        and_set.append((name1, name2))
  return and_set

def filter_bug_funcs(funcs):
  for start, end, name, contents in funcs:
    if not 'CWE' in name:
      funcs.remove((start, end, name, contents))
  return funcs

def filter_patch_funcs(funcs):
  for start, end, name, contents in funcs:
    if '_good' in name:
      funcs.remove((start, end, name, contents))
  return funcs

def print_funcs(funcs):
  for start, end, name, contents in funcs:
    print('funcname:', name)
    print('start:', start)
    print('Contents:', contents)
    print('------------------')

def replace_func_and_write(path, target, patch_funcs, and_funcs, bug_lines, patch_lines):
  if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)
  cnt = 0
  dir_name = os.path.basename(path)
  start1, end1, name1, contents1 = target
  for start2, end2, name2, contents2 in patch_funcs:
    new_lines = bug_lines[:start1] + patch_lines[start2:end2+1] + bug_lines[end1+1:]
    out_path = os.path.join(OUT_DIR, dir_name)
    while os.path.exists(out_path):
      out_path = os.path.join(OUT_DIR, dir_name + '_{}'.format(cnt))
      cnt += 1
    if not os.path.exists(out_path):
      os.makedirs(out_path)
    with open(os.path.join(out_path, 'bug.i'), 'w') as f:
      f.writelines(bug_lines)
    with open(os.path.join(out_path, 'patch.i'), 'w') as f:
      f.writelines(new_lines)
    
    



def run():
  work_len = len(os.listdir(BUILT_PATH))
  cnt = 1
  for d in os.listdir(BUILT_PATH):
    print('Processing {}/{}'.format(cnt, work_len))
    cnt += 1
    path = os.path.join(BUILT_PATH, d)
    bug_file = os.path.join(path, 'bug.i')
    patch_file = os.path.join(path, 'patch.i')
    with open(bug_file, 'r') as f:
      bug_lines = f.readlines()
    with open(patch_file, 'r') as f:
      patch_lines = f.readlines()
    bug_funcs = lexical_func_parse(bug_lines)
    patch_funcs = lexical_func_parse(patch_lines)
    bug_funcs_xor = filter_bug_funcs(get_xor_funcs(bug_funcs, patch_funcs))
    and_funcs = get_and_funcs(bug_funcs, patch_funcs)
    patch_funcs_xor = filter_patch_funcs(get_xor_funcs(patch_funcs, bug_funcs))

    if len(bug_funcs_xor) != 1:
      continue
    if len(patch_funcs_xor) == 0:
      continue
    bug_target_func = bug_funcs_xor[0]
    replace_func_and_write(path, bug_target_func, patch_funcs_xor, and_funcs, bug_lines, patch_lines)
    
    
run()

# with open(bug_file, 'r') as f:
#   bug_lines = f.readlines()
# with open(patch_file, 'r') as f:
#   patch_lines = f.readlines()
# bug_funcs = lexical_func_parse(bug_lines)
# patch_funcs = lexical_func_parse(patch_lines)

# bug_funcs_xor = get_xor_funcs(bug_funcs, patch_funcs)
# patch_funcs_xor = get_xor_funcs(patch_funcs, bug_funcs)

# if len(bug_funcs_xor) != 1:
#   print('Error: More than one xor function')
#   sys.exit(1)
  
# bug_target_func = bug_funcs_xor[0]

# for start, end, name, contents in get_xor_funcs(bug_funcs, patch_funcs):
#   print('funcname:', name)
#   print('start:', start)
#   print('Contents:', contents)
#   print('------------------')

# for start, end, name, contents in patch_funcs:
#   print('funcname:', name)
#   print('start:', start)
#   print('Contents:', contents)
#   print('------------------')


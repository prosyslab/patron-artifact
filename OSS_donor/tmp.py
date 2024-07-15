import os
import json
import subprocess
FILE_PATH = os.path.abspath(__file__)
label = os.path.join(os.path.dirname(FILE_PATH), 'CVE-2018-1100', 'label.json')
for file in os.listdir(os.path.dirname(FILE_PATH)):
    if '_' in file:
      bug_path = os.path.join(os.path.dirname(FILE_PATH), file, 'bug')
      # patch_path = os.path.join(os.path.dirname(FILE_PATH), file, 'patch')
      # os.chdir(patch_path)
      os.chdir(bug_path)

      # os.system('rm patch_tmp.c')
      file_path = os.path.join(bug_path, 'bug.c')
      # os.chdir(os.path.join(bug_path, 'sparrow-out', 'taint', 'datalog'))
      # alram_map = os.path.join(bug_path, 'sparrow-out', 'taint', 'datalog', 'Alarm.map')
      # with open(alram_map, 'r') as f:
      #   lines = f.readlines()
      #   if len(lines) > 1:
      #     print(file + '\t has more than 2 alarms')
      #   comps = lines[0].split('\t')
      #   line_no = comps[0]
      #   alarm_exp = comps[1]
      #   alarm_no = comps[2]
      # with open(os.path.join(bug_path, 'sparrow-out', 'taint', 'report.txt'), 'r') as f:
      #   lines = f.readlines()
      #   for line in lines:
      #     if line_no in line:
      #       func = line.split('{')[-1].split('}')[0].strip()
      #       break
      # out = subprocess.check_output('ls | wc -l', shell=True)
      # print(out)
      # if out == b'3\n':
      #   print(file)
      # if os.path.exists(os.path.join(bug_path, 'sparrow-out')):
      #   os.system('rm -r sparrow-out')
      
      label = os.path.join(os.path.dirname(FILE_PATH), file, 'label.json')
      label = json.load(open(label, 'r'))
      # label['TRUE-ALARM']['ALARM-LOC'] = [line_no]
      # label['TRUE-ALARM']['ALARM-EXP'] = [alarm_exp]
      # label['TRUE-ALARM']['ALARM-SYMBOL'] = [alarm_no.strip()]
      # label['TRUE-ALARM']['ALARM-DIR'] = ['0']
      # label['TRUE-ALARM']['ALARM-FUNC'] = [func]
      typ = label['TYPE']
      if typ == 'BO':
        type_flag = '-bo'
      elif typ == 'DZ':
        type_flag = '-dz'
      elif typ == 'PIO':
        type_flag = '-pio'
      elif typ == 'TIO':
        type_flag = '-tio'
      elif typ == 'MIO':
        type_flag = '-mio'
      os.system('sparrow -taint -extract_datalog_fact_full -unwrap_alloc -remove_cast -patron ' + type_flag + ' ' + file_path)
      # with open('cmd', 'w') as f:
      #   f.write('sparrow -taint -extract_datalog_fact_full -unwrap_alloc -remove_cast -patron ' + type_flag + ' ' + file_path)
      # for i in range(len(file)):
      #   if file[i] == '_' and file[i+1] == '_':
      #     true_name = file[:i]
      # label['ID'] = file
      # label['URL'] = 'https://github.com/arichardson/juliet-test-suite-c/tree/master/testcases/' + true_name
      # label['PROJECT'] = 'juliet-test-suite-c'
      # if 'Integer_Overflow' in file or 'Underflow' in file:
      #   if '_add' in file or 'inc' in file:
      #     label['TYPE'] = "PIO"
      #   elif '_multiply' in file or '_square' in file:
      #     label['TYPE'] = "TIO"
      #   elif '_sub' in file or 'dec' in file:
      #     label['TYPE'] = "MIO"
      # elif 'Buffer_Overflow' in file:
      #   label['TYPE'] = "BO"
      # elif 'Divide_by_Zero' in file:
      #   label['TYPE'] = "DZ"
      # # pretty dump
      # with open(os.path.join(os.path.dirname(FILE_PATH), file, 'label.json'), 'w') as f:
      #   json.dump(label, f, indent=4)
        
         
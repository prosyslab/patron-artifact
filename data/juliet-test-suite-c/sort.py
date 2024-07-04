import sys
import os
import subprocess
import re

def parse_diff(diff_lines):
    changes = []
    current_change = None

    for line in diff_lines:
        if re.match(r'\d+(?:,\d+)?[acd]\d+(?:,\d+)?', line):
            if current_change:
                changes.append(current_change)
            current_change = {'line_info': line, 'lines': []}
        elif current_change is not None:
            current_change['lines'].append(line)

    if current_change:
        changes.append(current_change)

    return changes
def is_useful_diff(lines):
    for line in lines:
        if '_bad()' in line:
            return False
        if 'void' in line and '()' in line:
            return False
        if 'Calling good()...' in line:
            return False
        if "Calling bad()..." in line:
            return False
        if 'finished good()' in line:
            return False
        if 'finished bad()' in line:
            return False
    return True
def apply_diff(bug_lines, changes):
    for change in changes:
        line_info = change['line_info']
        lines = change['lines']
        if not is_useful_diff(lines):
            continue
        if 'a' in line_info:
            # Addition
            index = int(line_info.split('a')[0])
            for line in reversed(lines):
                clean_line = line.lstrip('> ')
                bug_lines.insert(index, clean_line + '\n')
        elif 'd' in line_info:
            # Deletion
            line_range = line_info.split('d')[0]
            if ',' in line_range:
                start, end = map(int, line_range.split(','))
            else:
                start = end = int(line_range)
            for _ in range(end - start + 1):
                bug_lines.pop(start - 1)
        elif 'c' in line_info:
            # Change
            bug_range, patch_range = line_info.split('c')
            if ',' in bug_range:
                bug_start, bug_end = map(int, bug_range.split(','))
            else:
                bug_start = bug_end = int(bug_range)
            new_lines = []
            for line in lines:
                if line.startswith('>'):
                    clean_line = line.lstrip('> ')
                    new_lines.append(clean_line + '\n')
            bug_lines[bug_start-1:bug_end] = new_lines

    return bug_lines

FILE_PATH = os.path.dirname(os.path.abspath(__file__))
TESTCASE_DIR = os.path.join(FILE_PATH, 'testcases')
OUT_DIR = os.path.join(FILE_PATH, 'built')
TEST = os.path.join(OUT_DIR, 'CWE121_Stack_Based_Buffer_Overflow__char_type_overrun_memcpy_01')
# for file in os.listdir(OUT_DIR):
#     full_path = os.path.join(OUT_DIR, file)
#     if os.path.isdir(full_path):
bug_file = os.path.join(TEST, 'bug.i')
patch_file = os.path.join(TEST, 'patch.i')
diff_file = os.path.join(TEST, 'diff.txt')

# parse the diff file
with open(diff_file, 'r') as f:
    diff_lines = f.readlines()
changes = parse_diff(diff_lines)
with open(bug_file, 'r') as f:
    bug_lines = f.readlines()
new_bug_lines = apply_diff(bug_lines, changes)
with open(os.path.join(TEST, 'patch_new.i'), 'w') as f:
    f.writelines(new_bug_lines)
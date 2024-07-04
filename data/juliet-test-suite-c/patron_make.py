import re
import sys 
import os 

FILE_PATH = os.path.dirname(os.path.abspath(__file__))

def convert_func_name(funcs):
  for i in range(len(funcs)):
    if "static void" in funcs[i]:
      func_name = re.search(r"static void (\w+)\(", funcs[i]).group(1)
      funcs[i] = "void {func_name}()".format(func_name='func')
      break
    elif "void CWE" in funcs[i]:
      func_name = re.search(r"void (\w+)\(", funcs[i]).group(1)
      funcs[i] = "void {func_name}()".format(func_name='func')
      break
  return funcs

def parse_file(c_file):
  includes = []
  good_functions = []
  bad_functions = []
  include_section = True
  in_good_function = False
  in_bad_function = False
  in_function = False
  for line in c_file:
    if line.startswith("#endif /* OMITBAD */"):
      in_function = False
      in_bad_function = False
      continue
    if line.startswith("#endif /* OMITGOOD */"):
      in_function = False
      in_good_function = False
      continue
    if in_good_function:
      if "void" in line:
        if in_function:
          in_function = False
          in_good_function = False
          continue
        else:
          in_function = True
      good_functions.append(line)
    if in_bad_function:
      if "void" in line:
        if in_function:
          in_function = False
          in_bad_function = False
          continue
        else:
          in_function = True
      bad_functions.append(line)
    if "#ifdef INCLUDEMAIN" in line:
      includes = ''.join(includes)
      good_functions = ''.join(convert_func_name(good_functions))
      bad_functions = ''.join(convert_func_name(bad_functions))
      return includes, good_functions, bad_functions
    if "#ifndef OMITBAD" in line:
      in_bad_function = True
      include_section = False
    if "#ifndef OMITGOOD" in line:
      in_good_function = True
      include_section = False
    if (not in_good_function) and (not in_bad_function) and (not in_function) and (include_section):
      includes.append(line)

def generate_c_file(includes, function_code, filename):
  c_program_template = """
{includes}

{function_code}

int main(int argc, char * argv[])
{{
    /* seed randomness */
    srand((unsigned)time(NULL));
    printLine("Calling function...");
    func();
    printLine("Finished function");
    return 0;
}}
"""
  program_code = c_program_template.format(includes=includes, function_code=function_code)
  with open(filename, "w") as file:
      file.write(program_code)

def run(input_file, out):
  with open(input_file, 'r') as file:
    c_source_code = file.readlines()
  ret = parse_file(c_source_code)
  if ret is None:
    print("Error: Unable to parse the provided source code. {}".format(input_file))
    assert(False)
    return
  includes, good_func, bad_func = ret
  path = os.path.join(out, os.path.basename(input_file).split('.c')[0])
  if not os.path.exists(path):
    os.makedirs(path)
  if good_func:
    good_path = os.path.join(path, "patch")
    if not os.path.exists(good_path):
        os.makedirs(good_path)
    file_name = os.path.basename(input_file).split('.c')[0] + '_good.c'
    generate_c_file(includes, good_func, os.path.join(good_path, file_name))
  else:
    print("Error: Unable to find the 'good' function implementation in the provided source code.")

  if bad_func:
    bad_path = os.path.join(path, "bug")
    if not os.path.exists(bad_path):
      os.makedirs(bad_path)
    file_name = os.path.basename(input_file).split('_')[0] + '_bad.c'
    generate_c_file(includes, bad_func, os.path.join(bad_path, file_name))
  else:
    print("Error: Unable to find the 'bad' function implementation in the provided source code.")
      
def main(input_file):
  out_dir = os.path.join(FILE_PATH, "patron")
  if not os.path.exists(out_dir):
    os.makedirs(out_dir)
  for root, dirs, files in os.walk(input_file):
    for file in files:
      if file.endswith(".c"):
        run(os.path.join(root, file), out_dir)
  
if __name__ == "__main__":
  if len(sys.argv) == 1:
    input_file = os.path.join(FILE_PATH, "testcases")
  else:
    input_file = sys.argv[1]
  main(input_file)
import record_time
import os
import subprocess
import sys

# EXPERIMENT_ITEMS = list()
# DIR_MAIN = os.getcwd()
# CONF_DATA_PATH = "/data"
# CONF_TOOL_PARAMS = ""
os.chdir(path)
sys.path.insert(0, path)
import driver 

def execute_command_override(command):
    if driver.CONF_DEBUG:
        print("\t[COMMAND]" + command)
    process = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    try:
      (output, error) = process.communicate(timeout=10)
    except subprocess.TimeoutExpired:
      process.kill()
      print("\t[ERROR] Timeout")
      return
    
def evaluate_override(conf_path, bug_name, bug_id):
    global driver.CONF_TOOL_PARAMS, driver.CONF_TOOL_PATH, driver.CONF_TOOL_NAME, driver.DIR_LOGS
    print("\t[INFO]running evaluation")
    log_path = str(conf_path).replace(".conf", ".log")
    tool_command = "{ cd " + driver.CONF_TOOL_PATH + ";" + driver.CONF_TOOL_NAME + " --conf=" + conf_path + " "+ driver.CONF_TOOL_PARAMS + ";} 2> " + driver.FILE_ERROR_LOG
    execute_command_override(tool_command)
    exp_dir = driver.DIR_RESULT + "/" + str(bug_id)

    copy_output = "{ cp -rf " + driver.CONF_TOOL_PATH + "/output/" + bug_name + " " + exp_dir + ";} 2> " + driver.FILE_ERROR_LOG
    execute_command_override(copy_output)
    copy_log = "{ cp " + driver.CONF_TOOL_PATH + "/logs/log-latest " + exp_dir + ";} 2> " + driver.FILE_ERROR_LOG
    execute_command_override(copy_log)

def time_out_driver(path):
  global driver.EXPERIMENT_ITEMS, driver.DIR_MAIN, driver.CONF_DATA_PATH, driver.CONF_TOOL_PARAMS
  print("[DRIVER] Running experiment driver")
  driver.read_arg()
  driver.load_experiment()
  driver.create_directories()
  index = 1
  for experiment_item in driver.EXPERIMENT_ITEMS:
      if driver.CONF_BUG_ID and index != driver.CONF_BUG_ID:
          index = index + 1
          continue
      if driver.CONF_START_ID and index < driver.CONF_START_ID:
          index = index + 1
          continue
      if driver.CONF_SKIP_LIST and str(index) in driver.CONF_SKIP_LIST:
          index = index + 1
          continue
      driver.CONF_TOOL_PARAMS = ""
      experiment_name = "Experiment-" + str(index) + "\n-----------------------------"
      print(experiment_name)
      bug_name = str(experiment_item[driver.KEY_BUG_NAME])
      directory_name = str(experiment_item[driver.KEY_DONOR])
      script_name = bug_name + ".sh"
      conf_file_name = bug_name + ".conf"
      category = str(experiment_item[driver.KEY_CATEGORY])
      if category == "cross-program":
          directory_name = str(experiment_item[driver.KEY_DONOR]) + "-" + str(experiment_item[driver.KEY_TARGET])
      script_path = driver.DIR_SCRIPT + "/" + category + "/" + directory_name
      conf_file_path = driver.DIR_CONF + "/" + category + "/" + directory_name + "/" + conf_file_name
      if category == "backporting":
          directory_name = "backport/" + str(experiment_item[driver.KEY_DONOR])
          driver.CONF_TOOL_PARAMS = " --backport "
      deploy_path = driver.CONF_DATA_PATH + "/" + directory_name + "/" + bug_name + "/"
      deployed_conf_path = deploy_path + "/" + conf_file_name
      print("\t[META-DATA] category: " + category)
      print("\t[META-DATA] project: " + directory_name)
      print("\t[META-DATA] bug ID: " + bug_name)
      if not os.path.isfile(deployed_conf_path):
          setup(script_path, script_name, conf_file_path, deployed_conf_path)
      if not CONF_SETUP_ONLY:
          evaluate_override(deployed_conf_path, bug_name, index)
      index = index + 1

if __name__ == "__main__":
  BIN_PATH = os.path.dirname(os.path.realpath(__file__))
  EXPERIMENT_PATH = os.path.dirname(BIN_PATH)
  LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(EXPERIMENT_PATH)), "logs")
  time_out_driver(EXPERIMENT_PATH)
  record_time.run(LOG_PATH)
  
import os, sys
import datetime
FILE_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.abspath(os.path.join(FILE_PATH, '..'))
OUT_DIR = os.path.join(ROOT_PATH, 'out')
start_time_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
out_name = start_time_str + '_alarm_counter.txt'
fp = open(os.path.join(OUT_DIR, out_name), 'w')


def run(target_dir):
  for root, dirs, files in os.walk(target_dir):
    for d in dirs:
        if d == 'sparrow-out':
            project_path = root
            alarm_path = os.path.join(project_path, 'sparrow-out', 'taint', 'datalog')
            cnt = 0
            for alarm in os.listdir(alarm_path):
                if alarm == 'Alarm.map':
                    continue
            cnt += 1
            fp.write(f"{project_path}\t{cnt}\n")
            fp.flush()
            print(f"{project_path}\t{cnt}")
        
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python alarm_counter.py <target_dir>")
        sys.exit(1)

    run(sys.argv[1])
    
    
fp.close()

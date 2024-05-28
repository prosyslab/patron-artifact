import os
import sys
FILE_PATH = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) != 2:
    print("Usage: python3 filter_reproducible_alarms.py <target directory>")
    sys.exit(1)
TARGET_PATH = os.path.abspath(sys.argv[1])
if not os.path.exists(sys.argv[1]):
    print("{} Directory does not exist".format(TARGET_PATH))
    sys.exit(1)

FP = open('reproducible_alarm_list.txt', 'r')
txt = FP.readlines()
FP.close()
alarm_list = []
for line in txt:
    alarm_list.append(line.strip().split('@@'))
target_len = len(alarm_list)
target_projects = set([ project[0] for project in alarm_list ])
cnt = 0
for root, dirs, _ in os.walk(TARGET_PATH):
    for directory in dirs:
        if directory == "sparrow-out":
            parent = os.path.join(root, directory)
            project = os.path.basename(os.path.dirname(parent))
            target_dir = os.path.join(parent, 'taint', 'datalog')
            if not os.path.exists(target_dir):
                print("sparrow-out directory does not exist in {}".format(target_dir))
                continue
            for target in os.listdir(target_dir):
                if target == 'Alarm.map':
                    continue
                is_found = False
                for alarm in alarm_list:
                    if (project == alarm[0] and target == alarm[1]):
                        print('Found Project: {}, Target: {}, keeping it'.format(project, target))
                        is_found = True
                        cnt +=1
                        alarm_list.remove(alarm)
                        break
                if not is_found:
                    print('Removing Project: {}, Target: {}'.format(project, target))
                    os.system('rm -rf {}'.format(os.path.join(target_dir, target)))
print("Total Alarms: {}".format(target_len))
print("Found Alarms: {}".format(cnt))
if len(alarm_list) != 0:
    print("There are some alarms that are not found in the target directory as follows:")
    for alarm in alarm_list:
        print(alarm)
    

                

                



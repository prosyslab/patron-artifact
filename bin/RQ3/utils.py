import sys, os, subprocess, argparse
import datetime

PROCESS_LIMIT = 20
working_processes = []
FILE_PATH=os.path.dirname(os.path.realpath(__file__))
OUT_PATH=os.path.join(FILE_PATH, '..', 'out')
OUT_DIR=os.path.join(OUT_PATH, datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '_utils')
LOG_FD = None

def log(msg):
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", file=LOG_FD)
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")
    

def run_sparrow(files):
    global working_processes
    cmd_prep = ['sparrow', '-unwrap_alloc', '-remove_cast', '-patron', '-extract_datalog_fact_full', '-dz', '-no_bo', '-io', '-taint']
    cmds = list(map(lambda x: cmd_prep + [x], files))
    for cmd in cmds:
        if len(working_processes) >= PROCESS_LIMIT:
            pid, status = os.waitpid(0, 0)
            working_processes.remove(pid)  
            log(f"Process {pid} finished with status {status}")
        pid = os.fork()
        if pid == 0:
            try:
                subprocess.run(cmd, stdout=subprocess.PIPE, check=True)
            except subprocess.CalledProcessError as e:
                log(f"Subprocess failed: {e}")
            sys.exit(0) 
        else:
            working_processes.append(pid)
    while len(working_processes) > 0:
        pid, status = os.waitpid(0, 0) 
        working_processes.remove(pid) 
        log(f"Process {pid} finished with status {status}")
    
def find_unanalyzed(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.c') and not os.path.exists(os.path.join(root, 'sparrow-out')):
                yield os.path.abspath(os.path.join(root, file))


if __name__ == '__main__':
    # global LOG_FD
    if not os.path.exists(OUT_PATH):
        os.makedirs(OUT_PATH)
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
    LOG_FD = open(os.path.join(OUT_DIR, 'utils.log'), 'w')
    parser = argparse.ArgumentParser(description='This is a simple utility script')
    parser.add_argument('--find-unanalyzed', '-f', type=str, default='', help='Find all the unanalyzed c files under the given directory')
    parser.add_argument('--analyzed-left-out', '-a', type=str, default='', help='Analyzed all the unanalyzed c files under the given directory')
    args = parser.parse_args()
    if args.find_unanalyzed and args.analyzed_left_out:
        log('--find-unanalyzed option and --analyzed-left-out option cannot be used together')
        sys.exit(1)
    if args.find_unanalyzed:
        log('\n'.join(find_unanalyzed(args.find_unanalyzed)))
    elif args.analyzed_left_out:
        run_sparrow(find_unanalyzed(args.analyzed_left_out))
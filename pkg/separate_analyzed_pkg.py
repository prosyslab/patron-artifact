import sys
import os

FILE_PATH = os.path.dirname(os.path.abspath(__file__))

def print_help():
    print("Separate the analyzed packages from the analysis target")
    print("Usage: python separate_analyzed_pkg.py <target dir>")
    sys.exit(1)

def check_if_analyzed(pkg_dir):
    sparrow_path = os.path.join(pkg_dir, 'sparrow-out')
    taint_path = os.path.join(sparrow_path, 'taint')
    datalog_path = os.path.join(taint_path, 'datalog')
    if not os.path.exists(datalog_path):
        return False
    if len(os.listdir(datalog_path)) < 5: # change this later
        return False
    return True
    
def separate_analyzed_pkg(target_dir):
    if os.path.exists(target_dir + '-analyzed'):
        print("The analyzed package directory already exists")
        return False
    os.mkdir(target_dir + '-analyzed')

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.c'):
                file_path = os.path.join(root, file)
                if check_if_analyzed(os.path.dirname(file_path)):
                    split_path = file_path.split('/')
                    for i in range(len(split_path)):
                        package_path = None
                        if split_path[i] == os.path.basename(target_dir):
                            package_path = '/'.join(split_path[:i+2])
                            break
                    if package_path is None:
                        print("Error in separating analyzed packages")
                        continue
                    os.rename(package_path, package_path.replace(target_dir, target_dir + '-analyzed'))
                    print("Moved the analyzed package: " + package_path)
    return True
        

def main():
    if sys.argv[1] == '-h' or sys.argv[1] == '--help':
        print_help()
    if len(sys.argv) != 2:
        print_help()
    target_dir = sys.argv[1]
    if not os.path.exists(os.path.join(FILE_PATH, target_dir)):
        print("No analysis target found")
        sys.exit(1)
    separate_analyzed_pkg(os.path.join(FILE_PATH, target_dir))



if __name__ == '__main__':
    main()
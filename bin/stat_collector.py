import sys
import os
import datetime
import csv

TIME = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'out', TIME)

def open_tsv(cnt):
    f = open(os.path.join(OUT_DIR, '{}_combined_stat.tsv'.format(str(cnt))), 'a')
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(["Donee Name", "Donor Benchmark", "Donor #", "Donee #", "Pattern Type","Correct?", "Diff"])
    f.flush()
    return f, writer

def process_tsvs(dir_path):
    cnt = 0
    line_cnt = 0
    out_f, writer = open_tsv(cnt)
    for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file == 'status.tsv':
                    full_file_path = os.path.join(root, file)
                    with open(full_file_path, 'r') as f:
                        while True:
                            line = f.readline()
                            if "Donee Name" in line:
                                continue
                            if not line:
                                break
                            if line_cnt > 1000:
                                out_f.close()
                                cnt += 1
                                out_f, writer = open_tsv(cnt)
                                line_cnt = 0
                            row = line.strip().split('\t')
                            writer.writerow(row)
                            out_f.flush()
                            line_cnt += 1
                    print("written {}".format(full_file_path))
    out_f.close()

def process_single_tsv(file_path):
    cnt = 0
    line_cnt = 0
    out_f, writer = open_tsv(cnt)
    with open(file_path, 'r') as f:
        while True:
            line = f.readline()
            if "Donee Name" in line:
                continue
            if not line:
                break
            if line_cnt > 100:
                out_f.close()
                cnt += 1
                out_f, writer = open_tsv(cnt)
                line_cnt = 0
            row = line.strip().split('\t')
            writer.writerow(row)
            out_f.flush()
            line_cnt += 1
        print("written {}".format(file_path))
        
def main():
    if len(sys.argv) != 2:
        print("Usage: python3 stat_collector.py <path>")
        exit(1)
    if not os.path.exists(OUT_DIR):
        os.mkdir(OUT_DIR)
        dir_path = os.path.abspath(sys.argv[1])
        
        if dir_path.endswith('.tsv'):
            process_single_tsv(dir_path)
        else:
            process_tsvs(dir_path)
        print("Done writing to {}".format(OUT_DIR))
                    

if __name__ == '__main__':
    main()
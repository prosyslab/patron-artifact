import sys
import os
import datetime
import csv

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'out')

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 stat_collector.py <dir>")
        exit(1)
    with open(os.path.join(OUT_DIR, '{}_combined_stat.tsv'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))), 'a') as out_f:
        writer = csv.writer(out_f, delimiter='\t')
        writer.writerow(["Donee Name", "Donor Benchmark", "Donor #", "Donee #", "Pattern Type","Correct?", "Diff"])
        out_f.flush()
        dir_path = os.path.abspath(sys.argv[1])
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file == 'status.tsv':
                    full_file_path = os.path.join(root, file)
                    with open(full_file_path, 'r') as f:
                        lines = f.readlines()[1:]
                    if len(lines) == 0:
                        continue
                    for line in lines:
                        row = line.strip().split('\t')
                        writer.writerow(row)
                        out_f.flush()
                    print("written {}".format(full_file_path))
        print("Done writing to {}".format(out_f.name))
                    

if __name__ == '__main__':
    main()
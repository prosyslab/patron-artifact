# !/usr/bin/env python3
import os

script_dir = os.path.dirname(os.path.realpath(__file__))

for filename in os.listdir(script_dir):
    if filename.endswith("_tmp"):
        os.remove(os.path.join(script_dir, filename))
        print(f"Removed {filename}")
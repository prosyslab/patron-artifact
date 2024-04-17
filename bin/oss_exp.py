#!/usr/bin/env python3
import build
import config

def run_full():
    config.setup(True)
    build.run()
    
def main():
    config.setup(False)
    if config.configuration["BUILD_ONLY"]:
        build.run()
    else:
        build.run()
    
if __name__ == '__main__':
    main()
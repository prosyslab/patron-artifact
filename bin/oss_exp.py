#!/usr/bin/env python3
import build
import config

def run_full():
    config.setup(True)
    build.run()
    
def main():
    config.setup(False)
    if config.configuration["CRWAL_ONLY"]:
        build.crawl()
    if config.configuration["BUILD_ONLY"]:
        build.smake()
        return
    
    
if __name__ == '__main__':
    main()
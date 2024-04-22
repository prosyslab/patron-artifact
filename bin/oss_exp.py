#!/usr/bin/env python3
import build
import sparrow
import config

def run_full():
    config.setup("TOP")
    build.run()
    sparrow.sparrow(config.configuration["SPARROW_TARGET_FILES"])
    patron.run()
    
def main():
    config.setup("TOP")
    if config.configuration["CRWAL_ONLY"]:
        build.crawl()
    if config.configuration["BUILD_ONLY"]:
        build.smake()
    if config.configuration["SPARROW_ONLY"]:
        sparrow.sparrow(config.configuration["SPARROW_TARGET_FILES"])
    # if config.configuration["PATRON_ONLY"]:
    #     patron.run()
    return
    
    
if __name__ == '__main__':
    main()
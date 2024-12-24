#!/usr/bin/env python3
import logger

expriment_ready_to_go = {
    "patron": [
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13",
        "14", "15", "16", "17", "18", "19", "20"
    ],
    "PWBench": [
        "1", "2-1", "2-2", "3", "4", "5", "6", "7", "8", "9-1", "9-2", "10",
        "12-1", "12-2", "12-3", "13", "17", "19", "21", "22", "23", "24"
    ],
    "test": ["2", "7", "11", "13", "17", "21", "22", "25"]
}


def all_exist(input, data):
    for i in input:
        if i not in data:
            return False
    return True


def load(ID, benchmark):
    benchmark_list = []
    # TODO: add this for running all benchmarks
    # for i in benchmark["id"]:
    #     benchmark_list.append(i)

    for v in ID:
        benchmark_list.append(v)
    return benchmark_list

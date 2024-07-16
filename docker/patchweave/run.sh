#!/bin/bash

PATCHWEAVE_PATH=$(realpath /patchweave/experiment/patchweave)
SCRIPT_PATH=$(realpath /patchweave/experiment/patchweave/bin/run.py)
echo "====================================="
echo "Running PatchWeave"
echo "Check out the results in /patchweave/"
mv $PATCHWEAVE_PATH/meta-data $PATCHWEAVE_PATH/meta-data-orig
mv $PATCHWEAVE_PATH/meta-data-paper $PATCHWEAVE_PATH/meta-data
cd $PATCHWEAVE_PATH
python3 $SCRIPT_PATH
echo "====================================="
echo "RESULT_LOCATION: $PATCHWEAVE_PATH/result"
echo "LOG_LOCATION: $PATCHWEAVE_PATH/logs"
echo "TIME_RECORD: $PATCHWEAVE_PATH/time_duration.tsv"
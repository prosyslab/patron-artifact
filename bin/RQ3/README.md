# Script Manual

## appscript

These scripts are for Google Spreadsheet.
They are for pruning Debian Experiment results you can find in <Project Root>/out/<Experiment Time>_patch/results_combined/status.tsv.

Open an empty Spreadsheet, and Go to [Extensions > app script] on the menu and copy the following scripts

- `mark_binary_dupicates.gs`: this gets rid off the duplicate patches due to shared libraries commonly used in cross projects.
- `mark_duplicate_patchs.hs`: this gets rid off the duplicate patches due to multiple patch patterns matched to a bug location.

To run this script, you need to copy the status.tsv to your target Spreadsheet.

## pattern_translator.py

This is a dubbugging script.
When DB is made, you can find patterns written in quantified variables rather than the concrete one.
Running this script converts the quantified ones to concrete one.

Usage: python3 pattern_translator.py <pattern.chc> <datalog_dir>

<pattern.chc> is within the DB directories.
<datalog_dir> is under the directory where CIL parsed source code (donor directories under `data`). sparrow-out/taint/datalog/<target-alarm No.>

For <datalog_dir>, you need to know the target alarm number which is usually written in each `label.json`

## merge_db.py

This is a simple script that combines multiple Database directories.

Usage: python3 pattern_translator.py <DB-dir1> <DB-dir2> <DB-dir3> ...

The result is `combined-DB` at the project root.
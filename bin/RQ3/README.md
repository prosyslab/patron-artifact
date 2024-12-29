# Script Manual

## 1. Get the List of Debian Packages
We already have run this process and collected the list at `data/RQ3/DebianBench/crawling_result`. 

Each text files refer to the list of packages based on different categories.

However, to update this list run the following command.

```
./bin/RQ3/run.py -crwal
```

## 2. Preprocess Packages for Patron
Run the following command to preprocess the packages for Patron

```
./bin/RQ3/run.py --preprocess --projects <Debian Project1> <Debian Project2> ...

```
Here, each Debian Projects must be from the result in the first step.

You can also run

```
./bin/RQ3/run.py --preprocess --project-list <Path to Debian List>
```
in case you have list of debian projects as a `.txt` file


This process includes,
```
1. build the package to obtain *.i files and combine them to *.c files depending on the different main functions the project has
2. taint analysis via Sparrow
```

Each step can be separately run through the below subsections as well.

### __2.1. Building Debian Packages

Run the following command to build given packages

```
./bin/RQ3/build.py --projects <Debian Project1> <Debian Project2> ...
```

If you don't specify projects, the script attempts to build entire 113 packages.

`*.c` files from the above process are saved at `data/RQ3/DebianBench/analysis_target_<current time>`.

### __2.2. Taint Analysis via Sparrow
At the `data/RQ3/DebianBench/analysis_target_<current time>` directory, there are lists of directories named after the package names.

Each directories have a sub-directory based on different `main()` functions of the package.

For example,
```
analysis-target
            |-- argyll
            |   `-- gamut
            |       |-- GenRMGam
            |       |   `-- GenRMGam.c
            |       |-- fakegam
            |       |   `-- fakegam.c
            |       |-- maptest
            |       |   `-- maptest.c
            |       `-- smthtest
            |           `-- smthtest.c
            |-- ccast
            |   |-- cgat
            |   |   `-- cgat.c
            |   `-- dpat
            |       `-- dpat.c
            ...
```

Run the following command to taint-analyze target *.c files
```
./bin/RQ3/sparrow.py --target-directory <target_dir> <target_dir2> <target_dir3> ... <-io | -tio | -pio | -mio | -sio | -dz | -bo>
```
The options at the end refer to the purpose of the analysis, which are
```
-io    Analyze Integer Overflow
-tio   Analyze Times Integer Overflow(Mult)
-pio   Analyze Puls Integer Overflow(Add)
-mio   Analyze Minus Integer Overflow(Sub)
-sio   Analyze Shift Integer Overflow
-dz    Analyze Division by Zero
-bo    Analyze Buffer Overrun
```
At least one of these options must be given to run this step.

In the above directory tree, if
```
./bin/RQ3/sparrow.py --target-directory path/to/argyll -io
```
is executed, `GenRMGam.c`, `fakegam.c`, `maptest.c`, `smthtest.c` will be the analysis targets for Integer Overflow bugs

Analysis Results will be saved in `sparrow-out` directory under the directory of each target file

### __2.3. Patch Transplantation via Patron

#### __2.3.1. Generating DB

We have 3 different bug-patch collections at `data/RQ3/patternDatabase`.
```
1. PWBench-patches : From PWBench
2. CVE-patches     : Manually collected from CVE entries
3. CWE-patches     : Collected from Juliet-testcases
```

You can make database from one of the above collections by running
```
./bin/RQ3/run.py --database <Directory Path>
```

You can also make a database straight from RQ1-2 data by running
```
./bin/RQ3/run.py --database data/RQ1-2/PWBench
```

Similarly, if you set up a custom database by following the structure of the above collections and `label.json`

#### __2.3.2. Patch Transplantation
Run the following command to run Patron for patch transplantation on the debian packages
`./bin/patron.py -d <dir1> <dir2>... [-p <# of processes>]`
```
./bin/RQ3/run.py --transplant --projects <target_dir1> <target_dir2> ... --database-path <path to database> [-p <# of processes>]
```
The target dirs are output of above preprocessing.
`-p` option determines the number of multiprocesses.

### Debugging

All the necessary information (building status for example) is saved under
`out/` directory


### Merging Multiple Database

Run the following command to merge databases

```
merge_db.py <DB-dir1> <DB-dir2> <DB-dir3> ...
```
This is a simple script that combines multiple Database directories.

The result is `combined-DB` at the project root.
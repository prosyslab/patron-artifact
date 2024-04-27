# patron-artifact

## Experiment 1.

## Experiment 2.

## Experiment 3.

### Get the List of Debian Packages
We already have run this process and collected the list at `pkg/lists/*.txt`. Each text files refer to the list of packages based on different categories.

However, to update this list run the following command.
`./bin/oss_exp.py -crwal`

### Preprocess Packages for Patron
Run the following command to preprocess the packages for Patron
`./oss_exp.py -pipe <.txt file>`

The `.txt` file is output of the above crawlling step.
This process includes,
```
1. download the package
2. build the package to obtain *.i files
3. combine *.i files to *.c files depending on the different main functions the project has
4. taint analysis via Sparrow
```

Each step can be separately run through the below subsections as well.

#### Building Debian Packages
At `pkg/lists/*.txt`, we have the full lists of Debian packages written separately based on their categories. 
ex) `pkg/lists/sound.txt`, `pkg/lists/graphics.txt` 

Run the following command to build packages listed in the target `.txt` file(s). 
```
./bin/oss_exp.py -build <path_to_txt_file1> <path_to_txt_file2> <path_to_txt_file3> ...
```
If you don't specify a path after the `-build` option, the script attempts to build entire packages.

`*.i` files from the above process are saved at `pkg/i_files/` with the directory named after the package names.

#### Taint Analysis via Sparrow
At `pkg/analysis-target` directory, there are lists of directories named after the package names.
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
./bin/oss_exp.py -sparrow <target_dir1> <target_dir2> <target_dir3> ... <-io | -tio | -pio | -mio | -sio | -dz | -bo>
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
`./bin/oss_exp.py -sparrow pkg/argyll -io` is executed, `GenRMGam.c`, `fakegam.c`, `maptest.c`, `smthtest.c` will be the analysis targets for Integer Overflow bugs

Analysis Results will be saved in `sparrow-out` directory under the directory of each target file

### Patch Transplantation via Patron
Run the following command to run Patron for patch transplantation on the debian packages
`./bin/patron.py -d <dir1> <dir2>... [-p <# of processes>]`

The target dirs are output of above preprocessing.
`-p` option determines the number of multiprocesses.

### Generating DB
We already have database pused in this repository. However, to make a custom database, the following command can be helpful.
`./bin/patron -db`

However, to make a custom database, `patron-experiment/benchmark` has to be updated.

### Debugging

All the necessary information (building status for example) is saved at
`out/` directory

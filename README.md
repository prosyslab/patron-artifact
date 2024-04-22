# patron-artifact

## Experiment 1.

## Experiment 2.

## Experiment 3.

### Building Debian Packages
At `pkg/lists/*.txt`, we have the full lists of Debian packages written separately based on their categories. 
ex) `pkg/lists/sound.txt`, `pkg/lists/graphics.txt` 

Run the following command to build packages listed in the target `.txt` file(s). 
```
./bin/oss_exp.py -build <path_to_txt_file1> <path_to_txt_file2> <path_to_txt_file3> ...
```
If you don't specify a path after the `-build` option, the script attempts to build entire packages.

`*.i` files from the above process are saved at `pkg/i_files/` with the directory named after the package names.

### Taint Analysis via Sparrow
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
### Debugging

All the necessary information (building status for example) is saved at
`out/` directory

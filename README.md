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

### Debugging

All the necessary information (building status for example) is saved at
`out/` directory

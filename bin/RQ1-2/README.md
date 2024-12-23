# RQ1 Experiment
## Setup
First, build both Sparrow and Patron

Please, refer to [sparrow_manual](https://github.com/prosyslab/sparrow-incubator/blob/master/README.md) for building sparrow and [patron_manual](https://github.com/prosyslab/patron/blob/main/README.md) for building patron


## Reproduce
Run the following command at the project root to fully reproduce the experiment.
```
./bin/experiment.sh
```

If you would like to reproduce a specific benchmark set, run
```
./bin/experiment.sh <target_benchmark_set>
```

The <target_benchmark_set> is either `patron` or `patchweave`

If you wan to check the result of the experiment, go to [Experiment Result](#experiment-result)

## Usage

You can also run specific id(s) of the target benchmark as the following.
```
./bin/experiment.sh <target_benchmark_set> -id 1 2 5
```

For example,
```
./bin/experiment.sh patchweave -id 1 2 5
```
will run patchweave benchmark id No.1, 2, and 5 sequentially.

**The Experiment Process contains 2 processes**
  
1. **Sparrow Analysis**

2. **Patch Generation via Patron**

If you would like to run each step separately, run the following command

```
./bin/run.py <target_benchmark_set> [-sparrow || -patron] [options] 
```

For example, 

```
./bin/run.py -sparrow patchweave
```
will run sparrow analysis for all benchmarks available under patchweave's benchmark, and

```
./bin/run.py -patron patchweave
```

However, it is also possible to run the individual steps at a time using the options below.
will run patron process for all benchmarks available under patchweave's benchmark

```
options:
  -h, --help            show help message and exit
  
  procedure options:
    -sparrow              run sparrow analysis only
    -patron               run patron only
  if none of the above flags is given, it will run the whole pipeline on the given benchmark

  target benchmark options:
    -id ID [ID ...]       run specific id(s) of the given benchmark (e.g. -id 1,2,3 (skipping this option will run all ids))
    -range RANGE [RANGE ...]
                          run a range of ids. overrides -id option (e.g. -range 1 10 (run id 1 to 10))
    -dug                  run saprrow with -dug option
    -timeout TIMEOUT      set timeout for each benchmark
    -cpu CPU              set desirable cpu core on the experiment(default = half the cores)
    -t TIMERECORD         record time of each process
    -p PARALLEL           run multiple processes parallel
```
## Example

You can also run a specific program(s) in the target benchmark by giving id No. (using -id or -range options)
For example,
```
$ ./bin/run.py -sparrow patchweave -id 5 
$ ./bin/run.py -patron patchweave -id 1 2 3
$ ./bin/run.py -patron patron -range 1 10
```

## Experiment Result

### High Level Results

Experiment logs are written at ```/out/``` directory

If experiment was run fully by `experiment.sh` outputs will be divided into two directories under `/out/`.

One for sparrow analysis and the other for patron.

Results are given as both .tsv and human-readable .txt file

Otherwise, logs are recorded in log.txt


### Low Level Logs

Details are logged depending on the process.

For Example,

- Sparrow Analysis Process
```
benchmark/<benchmark project>/<ProjectID>/sparrow_log 
ex) benchmark/patchweave/1/sparrow_log
```

- Patron Extraction Process
```
out/<datetime of your experiment>/out-patron-<ProjectID>/log.txt
```

## Debugging

All the information regarding the patron process(facts and rules fed to the z3, mapping results, etc.)  will be dumped under


```
out/<datetime of your experiment>/out-patron-<ID>/
```

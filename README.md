# Patron: Static Patch Transplantation for Recurring Software Vulnerabilities (Paper Artifact)

This is the artifact of the paper *Static Patch Transplantation for Recurring Software Vulnerabilities*.

## 1. Getting Started

We assume that the following environment settings are met.
- Ubuntu 22.04
- Docker
- python 3.8+
- pip3
- Ocaml 3.16.0
- Dune 3.16.0
- Opam 2.1.2

### 1.1. Get Image from Dockerhub.

Get the pre-built image by running.

```
docker pull prosyslab/patron-artifact
```

### 1.2. Build Your Own Image.

To build your own image, run the following commands.

```
git clone https://github.com/prosyslab/patron --recursive
cd docker/patron
docker build . -t prosyslab/patron-artifact
```

### 1.3. Build it on Your Machine.

For the Python dependencies required to run the experiment scripts, run
```
yes | pip3 install -r requirements.txt
```

Then, run
```
./build.sh
```

&nbsp;

## 2. Directory structure

```
├─ README.md                        <- The top-level README (this file)
│   
├─ bin                              <- Scripts to run Patron and other Supplementry tools
│  │
│  ├─ run_patron                    <- The top-level script to run experiments
│  │
│  ├─ RQ1-2                         <- Directory with low-level scripts to reproduce RQ1 and RQ2 experiment
│  │  ├─ experiment.sh              <- The mid-level script to run the experiment with various settings
│  │  ├─ ...
│  │  ├─ README.md                  <- A manual for RQ1-2 scripts
│  │  └─ run.py                     <- The low-level scripts for RQ1-2
│  │
│  └─ RQ3                           <- Directory with low-level scripts to run Patron against Debian projects
│     ├─ run.py                     <- The mid-level script to configure details for Patron
│     ├─ ...
│     └─ README.md                  <- A manual for RQ3 scripts
│
├─ data
│  │
│  ├─ RQ1-2                         <- Directory with benchmark data for RQ1 and 2
│  │  ├─ PWBench                    <- PatchWeave Benchmarks
│  │  └─ ...
│  └─ RQ3                           <- Directory with benchmark data for RQ3
│     ├─ DebianBench                <- Directory with meta-data for DebianBench
│     │    ├─ target_list.txt       <- List of 113 Debian projects used in the experiments
│     │    ├─ crawling_result       <- Directory with all Debian projects crawled from web (Can be updated by running `./bin/RQ3/crawl.py`)
│     │    ├─ smake_out             <- An automatically generated directory after preprocessing Debian projects
│     │    ├─ reproduction_packages <-
│     │    └─ ...
│     │
│     └─ patternDatabase
│          ├─ ...
│          ├─ CVE-patches           <- Manually collected bug-patch program pairs from CVE 
│          ├─ CWE-patches           <- Bug-patch program pairs collected from Juliet-Testcase (CWE)
│          └─ reprod-patches        <- Simplified database to reproduce the experiment results
│
├─ patron                           <- Implementation of Patron, the patch transplantation tool
│
├─ sparrow                          <- Implementation of Sparrow, the static analyzer
│
├─ smake                            <- Implementation of Smake, the program analysis preparation tool
│
├─ out                              <- An automatically generated directory for logs, statistics, and results
│
├─ docker                           <- Docker-related scripts to get images for Patron and baseline tools
│  │
│  ├─ patron                        
│  │  ├─ Dockerfile                 <- Dockerfile used to make the Patron artifact image
│  │  └─ ...
│  ├─ patchweave                    
│  │  ├─ build.sh                   <- The script to generate PatchWeave image and also to run the experiment
│  │  ├─ proof_for_wrong_patches    <- PoCs that show PatchWeave's patch result can still be vulnerable
│  │  └─ ...
│  └─ vulnfix
│     ├─ build.sh                   <- The script to generate VulnFix image and also to reproduce the experiment
│     └─ ...
│
├─ build.sh                         <- The script to build Patron
│
└─ requirements.txt                 <- Python requirements for the scripts
```

## 3. Experiment Reproduction

### 3.1. RQ 1, 2 - Accuracy, Scalability.

If you would like to check out the experimental outcomes beforehand, refer to [RQ1 spreadsheet](https://docs.google.com/spreadsheets/d/1Mj6vHFTsFxV7hkIJ6hqLFhdKB-YUEd8fEpcrrrdCrkQ/edit?usp=sharing)

#### 3.1.1. Our Tool (Patron)

Run the following command to reproduce Experiment for the RQ1 and RQ2.

`./bin/run_experiment --reproduce-RQ1-2`

The output to the experiment which you could also found in our paper is located at 

`./out/<experment_time>_RQ1-2`

Please, read [RQ1-2_manual](https://github.com/prosyslab/patron-artifact/blob/master/bin/RQ1-2/README.md) for more details about the experiment reproduction.

#### 3.1.2. Patchweave

To run the Patchweave artifact to see experiment results

```
cd <project root>/docker/patchweave
./build.sh
./run.sh
```

Unfortunately, Patchweave artifact is not provided fully reproducible.

For more details, visit [https://patchweave.github.io/](https://patchweave.github.io/)

#### 3.1.3. VulnFix

To run the VulnFix artifact to see experiment results

```
cd <project root>/docker/vulnfix
./build.sh
./run.sh
```

#### 3.1.4. IntRepair

[IntRepair](https://github.com/TeamVault/IntRepair?tab=readme-ov-file)'s artifact is incompletely provided, we follow the algorithm provided in the [paper](https://ieeexplore.ieee.org/abstract/document/8862860/) to simulate the patches.

These manually synthesized patches can be found in [here](https://docs.google.com/spreadsheets/d/1Mj6vHFTsFxV7hkIJ6hqLFhdKB-YUEd8fEpcrrrdCrkQ/edit?usp=sharing)

### 3.2. RQ 3 - Generalizability.

This section inculdes how to reproduce the experiment results for RQ 3.

The list of 113 target Debian projects are at `./data/RQ3/DebianBench/target_list.txt`

If you want to run against all 113 projects, refer to [RQ3 manual](https://github.com/prosyslab/patron-artifact/blob/master/bin/RQ3/README.md)

#### 3.2.1. Making Pattern Database

Run the following command to construct the minimal pattern database.

```
./bin/run_patron --construct-database
```

If you want to try building other databases, please refer to [RQ3 manual](https://github.com/prosyslab/patron-artifact/blob/master/bin/RQ3/README.md)

#### 3.2.2. Preprocessing Target Projects

This process includes build and analysis steps for Patron to work.

Run the following command to preprocess target donee projects

```
./bin/run_patron --preprocess-target --projects <Debian Project1> <Debian Project2> ...
```

Note that <Debian Project> is sensitive to package name.

To know more about various Debian Projects, refer to [RQ3 manual](https://github.com/prosyslab/patron-artifact/blob/master/bin/RQ3/README.md)

#### 3.2.3. Run Patron on the Target Projects

Run the following command to run patron on target directories.

```
./bin/run_patron --transplant-target <Target Dir1> <Target Dir2> ... 
```

Each <Target Dir> must be from the output of the preprocess step.

## 4. Patron on Custom Settings

For this version of the artifact, there are two main challenges to use Patron on custom settings.

## 4.1. Running Patron on an Arbitrary Project.

This artifact offers to automatically preprocess the Debian projects only.

If the project has a `Makefile`, run `smake/smake` file at the same directory where the `Makefile` is present.

Then, the result of the smake will be under the automatically generated directory `sparrow` at your current directory.

Usually, `sparrow` directory has several subdirectories based on different main functions.

Choose one of the subdirectory as a target, and run the following command.

```
<Sparrow Bin Path> -il -frontenc claml <Chosen Subdirectory>/*.i > out.c
```

If the project does not have a `Makefile`, run the command with all the .c files you are targeting.

For example,
```
sparrow -il -frontenc claml path/to/file1.c path/to/file2.c ... > out.c
```

Finally, run `bin/RQ3/sparrow.py` to continue with the analysis.

The details of `sparrow.py` is written [here](https://github.com/prosyslab/patron-artifact/blob/master/bin/RQ3/README.md).

## 4.2. Preparing a custom pattern database

To prepare a custom pattern database, your donor directory must have the following directory structure.

```
Database
├─ donor1            
│   ├─ bug
│   │   └─ buggy.c   <- a buggy version of CIL-parsed program. The name does not matter
│   ├─ patch
│   │   └─ patch.c   <- a patched version of CIL-parsed program. The name does not matter
│   └─ label.json    <- meta information
├─ donor2
│   ├─ bug
│   │   └─ buggy.c
│   ├─ patch
│   │   └─ patch.c
│   └─ label.json
...
```

each `buggy.c` and `patch.c` files must be in CIL format, meaning that you must run
```
<Sparrow Bin Path> -il -frontenc claml <your file1> <your .c file2> ... > buggy.c
```
This is identical to the command in section 4.1.

The `label.json` must have the following fields.
```
1. TYPE     : IO, TIO, MIO, PIO, DZ, BO, ND
2. ALARM-LOC: CIL line number of the bug in the buggy.c (a CIL file contains #line 000 in each line)
3. ALARM-DIR: directory name for the target sparrow alarm
```

Here, to know `ALARM-DIR`, you must first run the sparrow analysis on your `buggy.c` file.

Then, `sparrow-out` directory will be created at your current directory.

Under `sparrow-out/taint/datalog/` directory, there will be directories named with digits.

Find your target alaram by referencing `sparrow-out/taint/datalog/Alarm.map`.

Once these are ready, you can continue to make your custom database by running `bin/RQ3/run.py`

For the instruction for this script, refer to [here](https://github.com/prosyslab/patron-artifact/blob/master/bin/RQ3/README.md).
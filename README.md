# Patron: Static Patch Transplantation for Recurring Software Vulnerabilities (Paper Artifact)

This is the artifact of the paper *Static Patch Transplantation for Recurring Software Vulnerabilities*.

## 1. Getting Started

<!-- ### __1.1. Get Image from Dockerhub. -->

### __1.1. Build Your Own Image.

To build your own image, run the following commands.

```
git clone https://github.com/prosyslab/patron --recursive
cd docker/patron
docker build . -t prosyslab/patron-artifact
```

### __1.2. Build it on Your Machine.

We assume that the following environment settings are met.
- Ubuntu 22.04
- Docker
- python 3.8+
- pip3
- Opam 2.1.2+

For the Python dependencies required to run the experiment scripts, run
```
yes | pip3 install -r requirements.txt
```

Then, run
```
./build.sh
```

&nbsp;

## 2. __Directory structure__

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

### __3.1. RQ 1, 2 - Accuracy, Scalability.

If you would like to check out the experimental outcomes beforehand, refer to [RQ1 spreadsheet](https://docs.google.com/spreadsheets/d/1Mj6vHFTsFxV7hkIJ6hqLFhdKB-YUEd8fEpcrrrdCrkQ/edit?usp=sharing)

#### __3.1.1. Our Tool (Patron)

Run the following command to reproduce Experiment for the RQ1 and RQ2.

`./bin/run_experiment --reproduce-RQ1-2`

The output to the experiment which you could also found in our paper is located at 

`./out/<experment_time>_RQ1-2`

Please, read [RQ1-2_manual](https://github.com/prosyslab/patron-artifact/blob/master/bin/RQ1-2/README.md) for more details about the experiment reproduction.

#### __3.1.2. Patchweave

To run the Patchweave artifact to see experiment results

```
cd <project root>/docker/patchweave
./build.sh
./run.sh
```

Unfortunately, Patchweave artifact is not provided fully reproducible.

For more details, visit [https://patchweave.github.io/](https://patchweave.github.io/)

#### __3.1.3. VulnFix

To run the VulnFix artifact to see experiment results

```
cd <project root>/docker/vulnfix
./build.sh
./run.sh
```

#### __3.1.4. IntRepair

[IntRepair](https://github.com/TeamVault/IntRepair?tab=readme-ov-file)'s artifact is incompletely provided, we follow the algorithm provided in the [paper](https://ieeexplore.ieee.org/abstract/document/8862860/) to simulate the patches.

These manually synthesized patches can be found in [here](https://docs.google.com/spreadsheets/d/1Mj6vHFTsFxV7hkIJ6hqLFhdKB-YUEd8fEpcrrrdCrkQ/edit?usp=sharing)

### __3.2. RQ 3 - Generalizability.

This section inculdes how to reproduce the experiment results for RQ 3.

The list of 113 target Debian projects are at `./data/RQ3/DebianBench/target_list.txt`

If you want to run against all 113 projects, refer to [RQ3 manual](https://github.com/prosyslab/patron-artifact/blob/master/bin/RQ3/README.md)

#### __3.2.1. Making Pattern Database

```
./bin/run_patron --construct-database
```

#### __3.2.2. Preprocessing Target Projects

```
./bin/run_patron --preprocess-target --projects [Debian Project1] [Debian Project2] ...
```

#### __3.2.3. Run Patron on the Target Projects

```
./bin/run_patron --transplant-target
```

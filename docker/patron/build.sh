#!/bin/bash -eux
SRC=/src
mkdir -p $SRC
cd $SRC; git clone https://github.com/prosyslab/patron-artifact.git --recursive

pip install -r $SRC/patron-artifact/requirements.txt
chmod +x $SRC/patron-artifact/build.sh
$SRC/patron-artifact/build.sh
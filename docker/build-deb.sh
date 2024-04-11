#!/usr/bin/env bash

PKG_NAME=$1

error_exit() {
  echo $1 1>&2
  exit 1
}

find_target() {
  num_dir=$(ls -d */ | wc -l)
  if [[ $num_dir == "1" ]]; then
    cd $(ls -d */)
  else
    exit 1
  fi
}

# 0. update package list
apt update -y
apt upgrade -y

# 1. download target source
apt source $PKG_NAME || error_exit "Error: download target source"

# 2. find target src dir
find_target || error_exit "Error: find target"

# 3. install dependencies
apt build-dep -y $PKG_NAME || error_exit "Error: install dependencies"

# 4. build the package with bear and create compilation database
bear dpkg-buildpackage -us -uc -d || error_exit "Error: dpkg-buildpackage"

# 5. run infer capture and copy
$INFER_BIN capture --compilation-database compile_commands.json --keep-going || error_exit "Error: infer capture"
cp -r infer-out $OUT    
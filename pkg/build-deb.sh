#!/usr/bin/env bash

FILE_PATH=$(dirname $(realpath $0))
PKG_LIST=$FILE_PATH/pkg_list.txt

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
# read package list and get each line
while read PKG_NAME; do
  BUILD_SCRIPT=$FILE_PATH/$PKG_NAME/build.sh
  # 0. update package list
  apt update -y
  apt upgrade -y
  cd $FILE_PATH/$PKG_NAME

  # 1. download target source
  apt source $PKG_NAME || error_exit "Error: download target source"

  # 2. find target src dir
  find_target || error_exit "Error: find target"

  # 3. install dependencies
  apt build-dep -y $PKG_NAME || error_exit "Error: install dependencies"

  # 4. build package
  bash $BUILD_SCRIPT || error_exit "Error: build package"
done < $PKG_LIST



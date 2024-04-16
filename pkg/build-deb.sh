#!/usr/bin/env bash

PKG_NAME=$1
SCRIPT_DIR=$(cd $(dirname $0); pwd)
OUT_DIR=$SCRIPT_DIR/$PKG_NAME
TMP='_tmp'
TMP_DIR=$SCRIPT_DIR/$TMP
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

# 1. download target source to the tmp directory
mkdir $TMP_DIR
cd $TMP_DIR
apt source $PKG_NAME || error_exit "Error: downloading package"

# 2. find target src dir
find_target || error_exit "Error: find target"

# 3. install dependencies
apt build-dep -y $PKG_NAME || error_exit "Error: install dependencies"

# 4. build the binary for the env settings
dpkg-buildpackage -us -uc -d || error_exit "Error: dpkg-buildpackage"

# 5. clear the build history
make distclean || make clean || error_exit "Error: distclean failed"

# 6. configure the package according to the pre-set env settings
dh_auto_configure || error_exit "Error: dh_auto_configure failed"

# 7. build the package
$SMAKE_BIN --init
$SMAKE_BIN -j || error_exit "Error: SMAKE failed"

# 8. install the package
mv sparrow $OUT_DIR || error_exit "Error: mv sparrow failed"

# 9. clean the tmp directory
rm -rf $TMP_DIR
#!/usr/bin/env bash

PKG_NAME=$1
SCRIPT_DIR=$(cd $(dirname $0); pwd)
OUT_DIR=$SCRIPT_DIR/smake_out/$PKG_NAME


TMP='_tmp'
TMP_DIR=$SCRIPT_DIR/smake_out/$PKG_NAME$TMP

if [ $PKG_NAME == "dvdauthor" ]; then
  apt-get install magick-dev
fi

clean() {
  cd $1
  rm -rf $2
}

error_exit() {
  echo $1 1>&2
  clean $2 $3
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

build_package() {
  CC=$1
  CXX=$2

  # 4. build the binary for the env settings
  dpkg-buildpackage -us -uc -d || return 1

  # 5. clear the build history
  make distclean || make clean || echo "No make file to clean"

  # 6. configure the package according to the pre-set env settings
  dh_auto_configure || return 1

  # 7. build the package
  if [ -f "Makefile" ]; then
    $SMAKE_BIN --init
    $SMAKE_BIN -j || return 1
  elif [ -f "CMakeLists.txt" ]; then
    /smake/scmake
  fi

  return 0
}

# remove lock files
# rm /var/lib/apt/lists/lock ;rm /var/cache/apt/archives/lock;rm /var/lib/dpkg/lock*

# package reset
dpkg --configure -a

# 0. update package list
apt update -y
apt upgrade -y

# 1. download target source to the tmp directory
mkdir $TMP_DIR
cd $TMP_DIR
apt source $PKG_NAME || error_exit "Error: downloading package" $SCRIPT_DIR $TMP_DIR

# 2. find target src dir
find_target || error_exit "Error: find target" $SCRIPT_DIR $TMP_DIR

# 3. install dependencies
apt build-dep -y $PKG_NAME || error_exit "Error: install dependencies" $SCRIPT_DIR $TMP_DIR

# Try building with gcc and g++
build_package gcc g++
if [ $? -ne 0 ]; then
  echo "GCC build failed, trying with Clang"
  # Try building with clang and clang++
  build_package clang clang++ || error_exit "Error: both GCC and Clang builds failed" $SCRIPT_DIR $TMP_DIR
fi

# 8. install the package
mv sparrow/* $OUT_DIR || error_exit "Error: mv sparrow failed" $SCRIPT_DIR $TMP_DIR

# 9. clean the tmp directory
clean $SCRIPT_DIR/smake_out $TMP_DIR

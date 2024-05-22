#!/usr/bin/env bash

PKG_NAME=$1
SCRIPT_DIR=$(cd $(dirname $0); pwd)
if [ -n "$2" ]; then
  OUT_DIR=$SCRIPT_DIR/i_files/$2/$PKG_NAME
else
  OUT_DIR=$SCRIPT_DIR/i_files/$PKG_NAME
fi

TMP='_tmp'
TMP_DIR=$SCRIPT_DIR/i_files/$PKG_NAME$TMP

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

# 4. build the binary for the env settings
dpkg-buildpackage -us -uc -d || error_exit "Error: dpkg-buildpackage" $SCRIPT_DIR $TMP_DIR

# 5. clear the build history
make distclean || make clean || echo "No make file to clean"

# 6. configure the package according to the pre-set env settings
dh_auto_configure || error_exit "Error: dh_auto_configure failed" $SCRIPT_DIR $TMP_DIR

# 7. build the package
if [ -f "Makefile" ]; then
  $SMAKE_BIN --init
  $SMAKE_BIN -j || error_exit "Error: SMAKE failed" $SCRIPT_DIR $TMP_DIR
elif [ -f "CMakeLists.txt" ]; then
  /smake/scmake
fi


# 8. install the package
echo sparrow $OUT_DIR
mv sparrow $OUT_DIR || error_exit "Error: mv sparrow failed" $SCRIPT_DIR $TMP_DIR

# 9. clean the tmp directory
clean $SCRIPT_DIR/i_files $TMP_DIR

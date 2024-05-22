#!/bin/bash
# export CFLAGS="-ftrapv -g"
# export CXXFLAGS="-static -fsanitize=integer -g"
# export CC="clang"
# export CXX="clang++"
# export CFLAGS="-static -g -O0 -fPIC -fsanitize=integer"
# export CXXFLAGS="-g -O0  -fPIC"
git clone https://github.com/uclouvain/openjpeg.git source
cd source/
git checkout version.1.5.1
sed -i "s/get_file_format(infile)/JP2_CFMT/g" applications/codec/j2k_to_image.c
autoreconf -i
./configure
# CFLAGS="-ftrapv" make -j10
make CFLAGS="-static -fsanitize=address,undefined,signed-integer-overflow -g" CXXFLAGS="-static -fsanitize=address,undefined,signed-integer-overflow -g" -j10

cp applications/codec/j2k_to_image ../

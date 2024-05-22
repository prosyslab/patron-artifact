#!/bin/bash
git clone https://github.com/uclouvain/openjpeg.git source
cd source/
git checkout 7720188
sed -i "s/get_file_format(infile)/J2K_CFMT/g" applications/codec/j2k_to_image.c


# cmake -DCMAKE_CC=clang -DCMAKE_CXX=clang++ -DCMAKE_C_FLAGS='-g -O0 -fsanitize=integer' -DCMAKE_CXX_FLAGS='-g -O0 -fsanitize=integer'  -DALLOW_IN_SOURCE_BUILD=1 .
autoreconf -i
CFLAGS="-static -ftrapv -g" ./configure
# CXXFLAGS="-static -fsanitize=address,undefined -g" ./configure
make CFLAGS="-static -fsanitize=address,undefined -g" CXXFLAGS="-static -fsanitize=address,undefined -g" -j10


cp applications/codec/j2k_to_image ../
 
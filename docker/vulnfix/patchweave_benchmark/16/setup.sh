#!/bin/bash
git clone https://github.com/uclouvain/openjpeg.git source
cd source/
git checkout version.1.5.2
sed -i "s/get_file_format(infile)/JP2_CFMT/g" applications/codec/j2k_to_image.c
# CC=clang CXX=clang++ CFLAGS="-fsanitize=address,null,integer,unsigned-integer-overflow -g" CXXFLAGS="-fsanitize=address,integer,null,unsigned-integer-overflow -g" cmake .
# make -j10
autoreconf -i
./configure
make CFLAGS='-ftrapv -fsanitize=address,undefined' -j10
cp applications/codec/j2k_to_image ..

#!/bin/bash
git clone https://github.com/uclouvain/openjpeg.git source
cd source/
git checkout c02f145cd1f8714727178d8a74cdd21a5327b107
sed -i "s/get_file_format(infile)/J2K_CFMT/g" applications/codec/j2k_to_image.c

autoreconf -i
./bootstrap.sh
./configure
make CFLAGS="-static -fsanitize=address -g" CXXFLAGS="-static -fsanitize=address -g" -j10

cp applications/codec/j2k_to_image ../

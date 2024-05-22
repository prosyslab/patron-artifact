#!/bin/bash
git clone https://github.com/uclouvain/openjpeg.git source
cd source/
git checkout c0cb119c0e6a18b6a9ac2ee4305acfb71b06a63c
# sed -i "s/get_file_format(infile)/JP2_CFMT/g" src/bin/jp2/opj_dump.c
# sed -i "2109i assert((int)((int)l_image->y1 - (int)l_cp->ty0) > 0);" src/lib/openjp2/j2k.c

sed -i "2111,2116d" src/lib/openjp2/j2k.c
cmake -DCMAKE_C_COMPILER=clang -DBUILD_SHARED_LIBS=off -DCMAKE_C_FLAGS="-g -O0 -ftrapv -fsanitize=integer,undefined,address" .
make
cp bin/opj_dump ..

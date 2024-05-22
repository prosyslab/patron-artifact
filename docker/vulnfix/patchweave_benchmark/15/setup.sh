#!/bin/bash
git clone https://github.com/uclouvain/openjpeg.git source
cd source/
git checkout version.2.1
sed -i "s/get_file_format(infile)/JP2_CFMT/g" src/bin/jp2/opj_dump.c
sed -i "118i assert((int)((int)p_cp->tx0 + (int)p_cp->tw * (int)p_cp->tdx) > 0);" src/lib/openjp2/image.c
sed -i "2100i assert((int)((int)l_image->x1 - (int)l_cp->tx0) > 0);" src/lib/openjp2/j2k.c
CC=clang CXX=clang++ CFLAGS="-fsanitize=address,integer,unsigned-integer-overflow -g" CXXFLAGS="-fsanitize=address,integer,unsigned-integer-overflow -g" cmake .
make -j10
cp bin/opj_dump ..


#!/bin/bash
git clone https://github.com/webmproject/libwebp.git source
cd source/
git checkout v0.2.0
sed -i -e '206d' examples/jpegdec.c
sed -i -e '28,30d' src/dsp/dsp.h

autoreconf -i
CC=clang CXX=clang++ CFLAGS="-fsanitize=address,integer,unsigned-integer-overflow -g" CXXFLAGS="-fsanitize=address,integer,unsigned-integer-overflow -g" ./configure --disable-shared
make -j10

cp examples/cwebp ../

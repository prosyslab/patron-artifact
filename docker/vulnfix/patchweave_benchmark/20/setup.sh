#!/bin/bash
git clone https://github.com/libming/libming.git source
cd source/
git checkout 19e7127

./autogen.sh
CC=clang CXX=clang++ CFLAGS='-static -fsanitize=address,undefined' ./configure --disable-freetype --disable-shared
make -j10
cp util/listmp3 ..

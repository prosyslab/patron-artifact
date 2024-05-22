#!/bin/bash
git clone https://github.com/mdadams/jasper.git source
cd source/
git checkout version-1.900.8

autoreconf -i
CC=clang CXX=clang++ CFLAGS="-fsanitize=address,undefined -g" CXXFLAGS="-fsanitize=address,undefined -g" ./configure --disable-shared
make -j10
cp src/appl/imginfo ..

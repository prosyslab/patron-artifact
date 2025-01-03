#!/bin/bash
git clone https://github.com/mdadams/jasper.git source
cd source/
git checkout version-1.900.13
rm aclocal.m4
autoreconf -i
CC=clang CXX=clang++ CFLAGS="-fsanitize=address,integer,unsigned-integer-overflow -g" CXXFLAGS="-fsanitize=address,integer,unsigned-integer-overflow -g" ./configure --disable-shared
make -j10

cp src/appl/imginfo ../

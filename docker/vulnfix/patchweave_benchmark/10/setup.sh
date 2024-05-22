#!/bin/bash
git clone https://github.com/mdadams/jasper.git source
cd source/
git checkout e5463624837d08d404dc64bba74eca8ce0ded9a3

autoreconf -i
CC=clang CXX=clang++ CFLAGS="-fsanitize=address,integer,unsigned-integer-overflow -g" CXXFLAGS="-fsanitize=address,integer,unsigned-integer-overflow -g" ./configure --disable-shared
make -j10

cp src/appl/imginfo ../

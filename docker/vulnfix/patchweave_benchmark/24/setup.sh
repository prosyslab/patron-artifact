#!/bin/bash
git clone https://github.com/nih-at/libzip.git source
cd source/
git checkout rel-1-1-2


cmake -DCMAKE_CC=clang -DCMAKE_CXX=clang++ -DCMAKE_C_FLAGS='-g -O0 -static' -DCMAKE_CXX_FLAGS='-g -O0'  -DALLOW_IN_SOURCE_BUILD=1 .
# cmake .
# CFLAGS="-fsanitize=address,undefined -g" CXXFLAGS="-fsanitize=address,undefined -g" make -j10
make CC=clang CXX=clang++ CFLAGS="-fsanitize=address,undefined,integer -g" CXXFLAGS="-fsanitize=address,undefined,integer -g" -j10
cp src/ziptool ..

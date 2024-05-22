#!/bin/bash
git clone https://github.com/mdadams/jasper.git source
cd source/
git checkout version-1.900.30

rm aclocal.m4
autoreconf -i
./configure
make CFLAGS="-static -fsanitize=address,undefined,signed-integer-overflow -g" CXXFLAGS="-static -fsanitize=address,undefined,signed-integer-overflow -g" -j10

cp src/appl/imginfo ../

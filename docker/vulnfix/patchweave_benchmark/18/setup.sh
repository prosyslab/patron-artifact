#!/bin/bash
git clone https://github.com/mdadams/jasper.git source
cd source/
git checkout version-1.900.8

autoreconf -i
./configure --disable-shared
make CFLAGS='-ftrapv -fsanitize=address,undefined' -j10
cp src/appl/imginfo ..

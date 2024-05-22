#!/bin/bash
git clone https://github.com/vadz/libtiff.git source
cd source/
git checkout Release-v4-0-0

autoreconf -i
./configure --disable-shared
make CFLAGS="-fsanitize=address,undefined -g" CXXFLAGS="-fsanitize=address,undefined -g" -j10
cp tools/tiff2ps ..

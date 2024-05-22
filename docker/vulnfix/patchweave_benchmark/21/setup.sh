#!/bin/bash
git clone https://github.com/libming/libming.git source
cd source/
git checkout 19e7127

./autogen.sh
./configure
make CFLAGS="-fsanitize=address,undefined -g" CXXFLAGS="-fsanitize=address,undefined -g" -j10
cp util/listmp3 ..

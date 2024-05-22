#!/bin/bash
git clone https://github.com/erikd/libsndfile.git source
cd source/
git checkout 1.0.26

autoreconf -i
./configure --disable-shared
make CFLAGS="-fsanitize=address,undefined -g" CXXFLAGS="-fsanitize=address,undefined -g" -j10
cp programs/sndfile-convert ..

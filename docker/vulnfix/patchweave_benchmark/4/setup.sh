#!/bin/bash
git clone https://github.com/mdadams/jasper.git source
cd source/
git checkout b9be3d9f35fccb7811ff68bbd6a57156f0192427

autoreconf -i
./configure
make CFLAGS="-static -fsanitize=address,undefined,signed-integer-overflow -g" CXXFLAGS="-static -fsanitize=address,undefined,signed-integer-overflow -g" -j10

cp src/appl/imginfo ../

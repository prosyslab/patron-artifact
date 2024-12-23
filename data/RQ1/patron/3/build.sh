mkdir full_patch
mkdir patch
mkdir bug
git clone https://github.com/vadz/libtiff/ tmp
cd tmp;
git checkout 21d39de1002a5e69caa0574b2cc05d795d6fbfad;
./configure;
$SMAKE_BIN --init;
$SMAKE_BIN --j;
sparrow -il -frontend claml sparrow/tools/.libs/tiffcrop/*.i > libtiff.c;
cd ..;
mv tmp/libtiff.c full_patch/
rm -rf tmp
sed -E -i 's/\b(.+?)\s*=\s*("[^"]*")/strcpy((char \*)\1, \2);/g' full_patch/libtiff.c
cp full_patch/libtiff.c patch/
sed -i '108645,108701d' patch/libtiff.c
sed -i '108800,108856d' patch/libtiff.c
sed -i '108299,108355d' patch/libtiff.c
cp patch/libtiff.c bug/
sed -i '108240,108296d' bug/libtiff.c
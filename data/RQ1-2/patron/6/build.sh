mkdir full_patch
mkdir patch
mkdir bug
git clone https://github.com/vadz/libtiff/ tmp
cd tmp;
git checkout 3fb9c79269f45c8026ea2c748ed58e590a32b2bd;
./autogen.sh
./configure;
$SMAKE_BIN --init;
$SMAKE_BIN --j;
sparrow -il -frontend claml sparrow/tools/.libs/tiffmedian/*.i > libtiff.c;
cd ..;
mv tmp/libtiff.c full_patch/
rm -rf tmp
sed -E -i 's/\b(.+?)\s*=\s*("[^"]*")/strcpy((char \*)\1, \2);/g' full_patch/libtiff.c
cp full_patch/libtiff.c patch/
sed -i '106896s/blue = (int )\*__cil_tmp19 & (255 >> 3);/blue = (int )\*__cil_tmp19 >> 3;/' patch/libtiff.c
sed -i '106890s/green = (int )\*__cil_tmp18 & (255 >> 3);/green = (int )\*__cil_tmp18 >> 3;/' patch/libtiff.c
cp patch/libtiff.c bug/
sed -i '106884s/red = (int )\*__cil_tmp17 & (255 >> 3);/red = (int )\*__cil_tmp17 >> 3;/' bug/libtiff.c
mkdir full_patch
mkdir patch
mkdir bug
git clone https://github.com/vadz/libtiff/ tmp
cd tmp;
git checkout 531a87ec56c682d65fa1c09f0474124cfb2a1dda;
./configure;
$SMAKE_BIN --init;
$SMAKE_BIN --j;
sparrow -il -frontend claml sparrow/tools/.libs/gif2tiff/*.i > libtiff.c;
cd ..;
mv tmp/libtiff.c full_patch/
rm -rf tmp
sed -E -i 's/\b(.+?)\s*=\s*("[^"]*")/strcpy((char \*)\1, \2);/g' full_patch/libtiff.c
cp full_patch/libtiff.c patch/
sed -i '106416s/if (! (count > 0 && count <= 255)) {/if (! (count > 0)) {/' patch/libtiff.c
cp patch/libtiff.c bug/
sed -i '106322s/if (! (count && count <= 255)) {/if (! (count)) {/' bug/libtiff.c
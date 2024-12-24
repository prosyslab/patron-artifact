mkdir full_patch
mkdir patch
mkdir bug
git clone https://github.com/vadz/libtiff/ tmp
cd tmp;
git checkout 4519fa4e32461862a20982949fd53a46ecc09529;
./autogen.sh
./configure;
$SMAKE_BIN --init;
$SMAKE_BIN --j;
sparrow -il -frontend claml sparrow/tools/.libs/rgb2ycbcr/*.i > libtiff.c;
cd ..;
mv tmp/libtiff.c full_patch/
rm -rf tmp
sed -E -i 's/\b(.+?)\s*=\s*("[^"]*")/strcpy((char \*)\1, \2);/g' full_patch/libtiff.c
cp full_patch/libtiff.c patch/
sed -i '51500s/m = img->UaToAa + ((size_t )a2 << 8);/m = img->UaToAa + (a2 << 8);/' patch/libtiff.c
sed -i '51215s/m = img->UaToAa + ((size_t )av << 8);/m = img->UaToAa + (av << 8);/' patch/libtiff.c
cp patch/libtiff.c bug/
sed -i '49454s/m = img->UaToAa + ((size_t )a << 8);/m = img->UaToAa + (a << 8);/' bug/libtiff.c
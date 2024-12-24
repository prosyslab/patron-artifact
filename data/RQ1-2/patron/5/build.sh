mkdir full_patch
mkdir patch
mkdir bug
git clone https://github.com/vadz/libtiff/ tmp
cd tmp;
git checkout c978029edc0dfe0e20013cf40b0c9984af3e272f;
./autogen.sh
./configure;
$SMAKE_BIN --init;
$SMAKE_BIN --j;
sparrow -il -frontend claml sparrow/tools/.libs/tiffdump/*.i > libtiff.c;
cd ..;
mv tmp/libtiff.c full_patch/
rm -rf tmp
sed -E -i '/^[[:space:]]*(static|char[[:space:]]+const)/!s/\b\*?([^[:space:]]+)\s*=\s*("[^"\\]*"|[^[:space:]]+)\s*;/strcpy((char \*)\1, \2);/g' libtiff.c
cp full_patch/libtiff.c patch/
sed -i '107578,107585d' patch/libtiff.c
sed -i '107579s/datasize = (uint64 )tmp___2;/datasize = count * typewidth;/' patch/libtiff.c
sed -i '107556,107563d' patch/libtiff.c
sed -i '107557s/datasize = (uint64 )tmp___1;/datasize = count * typewidth;/' patch/libtiff.c
cp patch/libtiff.c bug/
sed -i '107475,107482d' bug/libtiff.c
sed -i '107476s/datasize = (uint64 )tmp___0;/datasize = count * typewidth;/' bug/libtiff.c
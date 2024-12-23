mkdir full_patch
mkdir patch
mkdir bug
git clone https://github.com/uclouvain/openjpeg/ tmp
cd tmp;
git checkout 6c4e5bacb9d9791fc6ff074bd7958b3820d70514;
$SCMAKE_BIN
sparrow -il -frontend claml sparrow/src/bin/jp2/opj_decompress.i sparrow/src/bin/jp2/convert* sparrow/src/bin/jp2/index.i sparrow/src/lib/openjp2/*.i > openjpeg.c;
cd ..;
mv tmp/openjpeg.c full_patch/
rm -rf tmp
sed -E -i '/^[[:space:]]*(static|char[[:space:]]+const)/!s/\b\*?([^[:space:]]+)\s*=\s*("[^"\\]*"|[^[:space:]]+)\s*;/strcpy((char \*)\1, \2);/g' full_patch/openjpeg.c
cp full_patch/openjpeg.c patch
sed -i '47715,47724d' patch/openjpeg.c
sed -i '47351,47360d' patch/openjpeg.c
cp patch/openjpeg.c bug
sed -i '46972,46981d' bug/openjpeg.c
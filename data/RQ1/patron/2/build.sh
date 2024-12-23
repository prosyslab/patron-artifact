mkdir full_patch
mkdir patch
mkdir bug
git clone https://github.com/jasper-software/jasper/ tmp
cd tmp;
git checkout d8c2604cd438c41ec72aff52c16ebd8183068020;
autoreconf -i;
./configure;
$SMAKE_BIN --init;
$SMAKE_BIN --j;
sparrow -il -frontend claml sparrow/src/appl/.libs/imginfo/*.i > jasper.c;
cd ..;
mv tmp/jasper.c full_patch/
rm -rf tmp
sed -E -i '/^[[:space:]]*(static|char[[:space:]]+const)/!s/\b\*?([^[:space:]]+)\s*=\s*("[^"\\]*"|[^[:space:]]+)\s*;/strcpy((char \*)\1, \2);/g' full_patch/jasper.c
cp full_patch/jasper.c patch/
sed -i '71081,71110d' patch/jasper.c
cp patch/jasper.c bug/
sed -i '71051,71080d' bug/jasper.c
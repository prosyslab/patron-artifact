mkdir full_patch
mkdir patch
mkdir bug
git clone https://github.com/jasper-software/jasper/ tmp
cd tmp;
git checkout a6e6f98f1301595352e88021a7110d47c553f59d;
$SCMAKE_BIN
sparrow -il -frontend claml sparrow/src/libjasper/base/*.i sparrow/src/libjasper/jpc/*.i sparrow/src/appl/imginfo.i > jasper.c;
cd ..;
mv tmp/jasper.c full_patch/
rm -rf tmp
sed -E -i '/^[[:space:]]*(static|char[[:space:]]+const)/!s/\b\*?([^[:space:]]+)\s*=\s*("[^"\\]*"|[^[:space:]]+)\s*;/strcpy((char \*)\1, \2);/g' full_patch/jasper.c
cp full_patch/jasper.c patch/
sed -i '14210,14219d' patch/jasper.c
sed -i '14016,14025d' patch/jasper.c
cp patch/jasper.c bug/
sed -i '13714,13723d' bug/jasper.c
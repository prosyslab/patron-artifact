mkdir full_patch
mkdir patch
mkdir bug
git clone https://github.com/uclouvain/openjpeg/ tmp
cd tmp;
git checkout 7f8f284ee5ee05200f62266dfff0284551407a83;
$SCMAKE_BIN
sparrow -il -frontend claml sparrow/src/bin/common/*.i sparrow/src/bin/jp2/opj_decompress.i sparrow/src/bin/jp2/convert* sparrow/src/bin/jp2/index.i sparrow/src/lib/openjp2/tcd.i sparrow/src/lib/openjp2/bio.i sparrow/src/lib/openjp2/cio.i sparrow/src/lib/openjp2/event.i sparrow/src/lib/openjp2/function_list.i  sparrow/src/lib/openjp2/image.i sparrow/src/lib/openjp2/invert.i sparrow/src/lib/openjp2/j2k.i sparrow/src/lib/openjp2/jp2.i sparrow/src/lib/openjp2/mqc.i sparrow/src/lib/openjp2/openjpeg.i sparrow/src/lib/openjp2/opj_clock.i sparrow/src/lib/openjp2/pi.i sparrow/src/lib/openjp2/t2.i sparrow/src/lib/openjp2/raw.i sparrow/src/lib/openjp2/t1.i sparrow/src/lib/openjp2/tcd.i sparrow/src/lib/openjp2/tgt.i > openjpeg.c;
cd ..;
mv tmp/openjpeg.c full_patch/
rm -rf tmp
sed -E -i '/^[[:space:]]*(static|char[[:space:]]+const)/!s/\b\*?([^[:space:]]+)\s*=\s*("[^"\\]*"|[^[:space:]]+)\s*;/strcpy((char \*)\1, \2);/g' full_patch/openjpeg.c
cp full_patch/openjpeg.c patch
sed -i '32955,32971d' patch/openjpeg.c
cp patch/openjpeg.c bug
sed -i '32901,32917d' bug/openjpeg.c

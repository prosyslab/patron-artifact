mkdir full_patch
mkdir patch
mkdir bug
git clone https://github.com/uclouvain/openjpeg/ tmp
cd tmp;
git checkout 5c5319984b81e2aa32d1d83abdef0cdb8dbe7b18;
$SCMAKE_BIN
sparrow -il -frontend claml sparrow/src/bin/jp2/opj_decompress.i sparrow/src/bin/jp2/convert* sparrow/src/bin/jp2/index.i sparrow/src/lib/openjp2/*.i > openjpeg.c;
cd ..;
mv tmp/openjpeg.c full_patch/
rm -rf tmp
sed -E -i '/^[[:space:]]*(static|char[[:space:]]+const)/!s/\b\*?([^[:space:]]+)\s*=\s*("[^"\\]*"|[^[:space:]]+)\s*;/strcpy((char \*)\1, \2);/g' full_patch/openjpeg.c
sed -i '46762s/.*/\t\t\t\t\ttrx0 = ((pi->tx0 + (OPJ_INT32 )(comp->dx << levelno)) - 1) \/ (OPJ_INT32 )(comp->dx << levelno);/g' full_patch/openjpeg.c
sed -i '46764s/.*/\t\t\t\t\ttry0 = ((pi->ty0 + (OPJ_INT32 )(comp->dy << levelno)) - 1) \/ (OPJ_INT32 )(comp->dy << levelno);/g' full_patch/openjpeg.c
sed -i '46766s/.*/\t\t\t\t\ttrx1 = ((pi->tx1 + (OPJ_INT32 )(comp->dx << levelno)) - 1) \/ (OPJ_INT32 )(comp->dx << levelno);/g' full_patch/openjpeg.c
sed -i '46768s/.*/\t\t\t\t\ttry1 = ((pi->ty1 + (OPJ_INT32 )(comp->dy << levelno)) - 1) \/ (OPJ_INT32 )(comp->dy << levelno);/g' full_patch/openjpeg.c
sed -i '46435s/.*/\t\t\t\t\ttrx0 = ((pi->tx0 + (OPJ_INT32 )(comp->dx << levelno)) - 1) \/ (OPJ_INT32 )(comp->dx << levelno);/g' full_patch/openjpeg.c
sed -i '46437s/.*/\t\t\t\t\ttry0 = ((pi->ty0 + (OPJ_INT32 )(comp->dy << levelno)) - 1) \/ (OPJ_INT32 )(comp->dy << levelno);/g' full_patch/openjpeg.c
sed -i '46439s/.*/\t\t\t\t\ttrx1 = ((pi->tx1 + (OPJ_INT32 )(comp->dx << levelno)) - 1) \/ (OPJ_INT32 )(comp->dx << levelno);/g' full_patch/openjpeg.c
sed -i '46441s/.*/\t\t\t\t\ttry1 = ((pi->ty1 + (OPJ_INT32 )(comp->dy << levelno)) - 1) \/ (OPJ_INT32 )(comp->dy << levelno);/g' full_patch/openjpeg.c
sed -i '46088s/.*/\t\t\t\t\ttrx0 = ((pi->tx0 + (OPJ_INT32 )(comp->dx << levelno)) - 1) \/ (OPJ_INT32 )(comp->dx << levelno);/g' full_patch/openjpeg.c
sed -i '46090s/.*/\t\t\t\t\ttry0 = ((pi->ty0 + (OPJ_INT32 )(comp->dy << levelno)) - 1) \/ (OPJ_INT32 )(comp->dy << levelno);/g' full_patch/openjpeg.c
sed -i '46092s/.*/\t\t\t\t\ttrx1 = ((pi->tx1 + (OPJ_INT32 )(comp->dx << levelno)) - 1) \/ (OPJ_INT32 )(comp->dx << levelno);/g' full_patch/openjpeg.c
sed -i '46094s/.*/\t\t\t\t\ttry1 = ((pi->ty1 + (OPJ_INT32 )(comp->dy << levelno)) - 1) \/ (OPJ_INT32 )(comp->dy << levelno);/g' full_patch/openjpeg.c
cp full_patch/openjpeg.c patch/
sed -i '46750,46759d' patch/openjpeg.c
sed -i '46423,46432d' patch/openjpeg.c
cp patch/openjpeg.c bug/
sed -i '46076,46085d' bug/openjpeg.c
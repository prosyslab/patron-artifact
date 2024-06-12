pc=jasper-1.900.2
pc_url=https://github.com/mdadams/jasper.git
pc_commit=version-1.900.2
dir_name=$pc-patch

git clone $pc_url $dir_name
cd $dir_name
git checkout $pc_commit
rm aclocal.m4
sed -i '1174a \if (((int)siz->xoff<0)||((int)dec->xend<0)||((int)siz->yoff<0)||((int)dec->yend<0)) {' src/libjasper/jpc/jpc_dec.c
sed -i '1175a \return -1;' src/libjasper/jpc/jpc_dec.c
sed -i '1176a \}' src/libjasper/jpc/jpc_dec.c
autoreconf -i;./configure;make

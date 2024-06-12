pc=jasper-1.900.30
pc_url=https://github.com/mdadams/jasper.git
pc_commit=version-1.900.30
dir_name=$pc-patch

git clone $pc_url $dir_name
cd $dir_name
git checkout $pc_commit
rm aclocal.m4
sed -i '281a \ if ((int)box->len < 0) {' src/libjasper/jp2/jp2_cod.c
sed -i '282a \ \ \ \ \ ' src/libjasper/jp2/jp2_cod.c
sed -i '283a \ \ \ \ \ return OPJ_FALSE; // TODO: actually check jp2_read_boxhdr'\''s return value' src/libjasper/jp2/jp2_cod.c
sed -i '284a \ }' src/libjasper/jp2/jp2_cod.c
sed -i '89a \ #define OPJ_FALSE 0' src/libjasper/jp2/jp2_cod.c

autoreconf -i;./configure;make



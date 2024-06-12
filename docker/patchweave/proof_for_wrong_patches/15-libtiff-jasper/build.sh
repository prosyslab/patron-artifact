pc=jasper-1.900.8
pc_url=https://github.com/mdadams/jasper.git
pc_commit=version-1.900.8
dir_name=$pc-patch

git clone $pc_url $dir_name
cd $dir_name
git checkout $pc_commit
sed -i '363a \ uint32 offset, size; ' src/libjasper/bmp/bmp_dec.c
sed -i '364a \  if (!(uint32)info->width || !info->depth' src/libjasper/bmp/bmp_dec.c
sed -i '365a \    		    || (size - 31) / info->depth != (uint32)info->width ) ' src/libjasper/bmp/bmp_dec.c
sed -i '366a \		{' src/libjasper/bmp/bmp_dec.c
sed -i '367a \return -1;' src/libjasper/bmp/bmp_dec.c
sed -i '368a \		}' src/libjasper/bmp/bmp_dec.c
rm aclocal.m4
autoreconf -i;./configure;make

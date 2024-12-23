I_PATH=sparrow/programs/.libs/sndfile-info
mkdir full_patch
mkdir patch
mkdir bug
git clone https://github.com/libsndfile/libsndfile tmp;
cd tmp;
git checkout cb3c87aa3bba868dd6477d35cf4b86d67c3e1f77;
./autogen.sh;
$SMAKE_BIN --init;
$SMAKE_BIN --j;
mv $I_PATH/3a.039.gsm_destroy.o.i 3a.039.gsm_destroy.o.i.x;
mv $I_PATH/3a.039.gsm_destroy.o.i 3a.039.gsm_destroy.o.i.x;
mv $I_PATH/3b.03a.gsm_encode.o.i 3a.039.gsm_destroy.o.i.x;
mv $I_PATH/3c.03b.gsm_option.o.i 3a.039.gsm_destroy.o.i.x;
mv $I_PATH/3d.03c.long_term.o.i 3a.039.gsm_destroy.o.i.x;
mv $I_PATH/43.042.g721.o.i 3a.039.gsm_destroy.o.i.x;
mv $I_PATH/44.043.g723_16.o.i 3a.039.gsm_destroy.o.i.x;
mv $I_PATH/45.044.g723_24.o.i 3a.039.gsm_destroy.o.i.x;
mv $I_PATH/46.045.g723_40.o.i 3a.039.gsm_destroy.o.i.x;
mv $I_PATH/47.046.g72x.o.i 3a.039.gsm_destroy.o.i.x;
sparrow -il -frontend *.i > libsndfile.c;


check_and_build() {
    if [ -d $$1/$2 ]; then
        TARGET_PATH=$1/$2
        if [ ls $TARGET_PATH | wc -l -eq 0 ]; then
            # rm -rf $TARGET_PATH
            echo "remove"
        else
            echo "exist"
        fi
    else
        git clone https://github.com/prosyslab/$2 $1/$2
    fi
}

SCRIPT_PATH=$(dirname $(realpath $0))
check_and_build $SCRIPT_PATH patron-experiment
EXP_PATH=$SCRIPT_PATH/patron-experiment

check_and_build $EXP_PATH patron
PATRON_PATH=$EXP_PATH/patron

check_and_build $EXP_PATH sparrow-incubator
SPARROW_PATH=$EXP_PATH/sparrow-incubator
mv $SPARROW_PATH $EXP_PATH/sparrow

opam option depext=false
cd $PATRON_PATH
./build.sh
opam switch patron-4.13.1
eval $(opam env)
make

cd ../sparrow
git checkout patron
./build.sh
opam switch sparrow-4.13.1+flambda
eval $(opam env)
make

cd ../../docker/vulnfix
rm -rf vulnfix
git clone https://github.com/yuntongzhang/vulnfix/

rm -rf patron
rm -rf sparrow
git clone https://github.com/prosyslab/patron
git clone https://github.com/prosyslab/sparrow-incubator

mv sparrow-incubator sparrow
cd patron
./build.sh
opam switch patron-4.13.1
eval $(opam env)
make
cd ../sparrow
git checkout patron
./build.sh
opam switch sparrow-4.13.1+flambda
eval $(opam env)
make
cd ../../docker/vulnfix
rm -rf vulnfix
git clone https://github.com/yuntongzhang/vulnfix/

echo "export PATH=\"\$PATH:/root/patron-artifact/patron-experiment/sparrow/bin\"" >> /root/.bashrc
source /root/.bashrc
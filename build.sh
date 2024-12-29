SCRIPT_PATH=$(dirname $(realpath $0))
PATRON_PATH=$SCRIPT_PATH/patron
SPARROW_PATH=$SCRIPT_PATH/sparrow

opam option depext=false
cd $PATRON_PATH
./build.sh
opam switch patron-4.13.1
eval $(opam env)
make

cd $SPARROW_PATH
./build.sh
opam switch sparrow-4.13.1+flambda
eval $(opam env)
make

echo "export PATH=\"\$PATH:$SCRIPT_PATH/sparrow/bin\"" >> /root/.bashrc
echo "export PATH=\"\$PATH:$SCRIPT_PATH/smake\"" >> /root/.bashrc
echo "SMAKE_BIN=$SCRIPT_PATH/smake/smake" >> /root/.bashrc
source /root/.bashrc

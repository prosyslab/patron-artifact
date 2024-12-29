
check_and_build() {
    if [ $2 == "sparrow-incubator" ]; then
        TOOL_NAME="sparrow"
    else
        TOOL_NAME=$2
    fi
    echo "Checking $TOOL_NAME..."
    if [ -d $1/$TOOL_NAME ]; then
        TARGET_PATH=$1/$TOOL_NAME
        if [ ls $TARGET_PATH | wc -l -eq 0 ]; then
            rm -rf $TARGET_PATH
        else
            echo "$TOOL_NAME already exists."
            return
        fi
    fi
    echo "$TOOL_NAME does not exist."
    echo "Cloning $TOOL_NAME..."
    git clone https://github.com/prosyslab/$2 $1/$2
}

SCRIPT_PATH=$(dirname $(realpath $0))
check_and_build $SCRIPT_PATH patron
PATRON_PATH=$SCRIPT_PATH/patron
check_and_build $SCRIPT_PATH sparrow-incubator
SPARROW_PATH=$SCRIPT_PATH/sparrow

opam option depext=false
cd $PATRON_PATH
./build.sh
opam switch patron-4.13.1
eval $(opam env)
make

cd $SPARROW_PATH
git checkout patron
./build.sh
opam switch sparrow-4.13.1+flambda
eval $(opam env)
make

echo "export PATH=\"\$PATH:$SCRIPT_PATH/sparrow/bin\"" >> /root/.bashrc
echo "export PATH=\"\$PATH:$SCRIPT_PATH/smake\"" >> /root/.bashrc
echo "SMAKE_BIN=$SCRIPT_PATH/smake/smake" >> /root/.bashrc
source /root/.bashrc

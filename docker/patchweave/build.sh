FILE_PATH=$(realpath $0)
DIR_PATH=$(dirname $FILE_PATH)

cd $DIR_PATH
docker pull rshariffdeen/patchweave:experiments
docker run -it --memory=30g --name patchweave rshariffdeen/patchweave:experiments
docker cp proof_for_wrong_patches patchweave:/
docker cp bin patchweave:/patchweave/experiment/patchweave
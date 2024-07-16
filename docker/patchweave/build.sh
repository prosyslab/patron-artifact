FILE_PATH=$(realpath $0)
DIR_PATH=$(dirname $FILE_PATH)

cd $DIR_PATH
docker pull rshariffdeen/patchweave:experiments
docker run -it -d --memory=30g --name patchweave rshariffdeen/patchweave:experiments
docker cp proof_for_wrong_patches patchweave:/
docker cp run.sh patchweave:/
docker cp bin patchweave:/patchweave/experiment/patchweave
docker cp meta-data-paper patchweave:/patchweave/experiment/patchweave
echo "====================================="
echo "run ./run.sh to start the experiment replication"
docker exec -it patchweave /bin/bash

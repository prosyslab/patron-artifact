FILE_PATH=$(realpath $0)
DIR_PATH=$(dirname $FILE_PATH)

cd $DIR_PATH
docker pull yuntongzhang/vulnfix:latest-manual
docker run -it -d --memory=30g --name vulnfix yuntongzhang/vulnfix:latest-manual
docker cp patchweave_benchmark vulnfix:/home/yuntong/vulnfix/data
docker cp run.sh vulnfix:/home/yuntong/vulnfix
echo "====================================="
echo "run ./run.sh to start the experiment replication"
echo "If you want to see the details of setup, run ./run.sh -v"
docker exec -it vulnfix /bin/bash
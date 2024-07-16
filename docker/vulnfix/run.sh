echo "======================================"
echo "Starting the experiment replication"
echo "Building Benchmark projects (This may take a while)"
cd /home/yuntong/vulnfix/data/patchweave_benchmark

SETUP_START=$(date +%s)

if [ "$1" == "-v" ]; then
    python3 run.py build
else
    python3 run.py build &> /dev/null
fi

SETUP_END=$(date +%s)
SETUP_ELAPSED=$(($SETUP_END - $SETUP_START))
echo "======================================"
echo "Benchmark projects built in $SETUP_ELAPSED seconds"
echo "======================================"
echo "Starting VulnFix"
python3 run.py patch
echo "======================================"
echo "VulnFix completed"
echo "Experiment Results are stored in /home/yuntong/vulnfix/logs"
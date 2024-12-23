#!/bin/bash
FILE=$(readlink -f $0)
DIR=$(dirname $FILE)
ROOT=$(dirname $(dirname $DIR))
OUT=$ROOT/out
DATE=$(date +"%Y%m%d%H%M%S_RQ1-2")

function usage {
    echo ""
    echo "Usage: $0 <benchmark> [-id]"
    echo "Run the experiment for the given benchmark"
    echo "Options:"
    echo "  -id Run experiment on the specified ID"
    exit 1
}

function safety_check {
    if [ ! -z "$1" ]; then
        if [ "$1" != "patchweave" ] && [ "$1" != "patron" ] && [ "$1" != "test" ]; then
            echo "$1 is not a valid benchmark title"
            echo "Please provide a valid benchmark title for the experiment"
            echo "We support patchweave and patron"
            usage
            exit 1
        fi
    fi
    if [ "$2" != "-id" ] && [ ! -z "$2" ]; then
        echo "Please provide a valid option for the experiment"
        usage
        exit 1
    fi
}

function run_full {
    python3 $DIR/run.py patchweave -sparrow -t -o $OUT/$DATE -lt SPARROW
    if [ $? -ne 0 ]; then
        echo "Failed to run sparrow"
        exit 1
    fi
    python3 $DIR/sep_true_alrams.py patchweave -o $OUT/$DATE
    if [ $? -ne 0 ]; then
        echo "Failed to run sep_true_alarms"
        exit 1
    fi
    python3 $DIR/run.py patchweave -patron -t -o $OUT/$DATE -lt PATRON
    if [ $? -ne 0 ]; then
        echo "Failed to run patron"
        exit 1
    fi

    python3 $DIR/run.py patron -sparrow -t -o $OUT/$DATE -lt SPARROW
    if [ $? -ne 0 ]; then
        echo "Failed to run sparrow"
        exit 1
    fi
    python3 $DIR/sep_true_alrams.py patron -o $OUT/$DATE
    if [ $? -ne 0 ]; then
        echo "Failed to run sep_true_alarms"
        exit 1
    fi
    python3 $DIR/run.py patron -patron -t -o $OUT/$DATE -lt PATRON
    if [ $? -ne 0 ]; then
        echo "Failed to run patron"
        exit 1
    fi
}

function run_on_benchmark {
    python3 $DIR/run.py "$1" -sparrow -t -o $OUT/$DATE -lt SPARROW
    if [ $? -ne 0 ]; then
        echo "Failed to run sparrow"
        exit 1
    fi
    python3 $DIR/sep_true_alrams.py "$1" -o $OUT/$DATE
    if [ $? -ne 0 ]; then
        echo "Failed to run sep_true_alarms"
        exit 1
    fi
    python3 $DIR/run.py "$1" -patron -t  -o $OUT/$DATE -lt PATRON
    if [ $? -ne 0 ]; then
        echo "Failed to run patron"
        exit 1
    fi
}

function run_on_ids {
    args=("${@:3}")
    re='^[0-9]+$|^[0-9]+-[0-9]+$'
    for arg in "${args[@]}"; do
        if ! [[ $arg =~ $re ]] ; then
            echo "error: Not a valid input for argument $arg" >&2
            usage
            exit 1
        fi
    done    
    python3 $DIR/run.py "$1" -sparrow -t -id "${args[@]}" -o $OUT/$DATE -lt SPARROW
    if [ $? -ne 0 ]; then
        echo "Failed to run sparrow"
        exit 1
    fi
    python3 $DIR/sep_true_alrams.py "$1" -id "${args[@]}" -o $OUT/$DATE
    if [ $? -ne 0 ]; then
        echo "Failed to run sep_true_alarms"
        exit 1
    fi
    python3 $DIR/run.py "$1" -patron -t -id "${args[@]}" -o $OUT/$DATE -lt PATRON
    if [ $? -ne 0 ]; then
        echo "Failed to run patron"
        exit 1
    fi
}

function patron_test {
    python3 $DIR/run.py patchweave -patron -t -o $OUT/$DATE -lt PATRON
    if [ $? -ne 0 ]; then
        echo "Failed to run patron"
        exit 1
    fi
    python3 $DIR/run.py patron -patron -t -o $OUT/$DATE -lt PATRON
    if [ $? -ne 0 ]; then
        echo "Failed to run patron"
        exit 1
    fi
}

function patron_test_id {
    args=("${@:3}")
    re='^[0-9]+$|^[0-9]+-[0-9]+$'
    for arg in "${args[@]}"; do
        if ! [[ $arg =~ $re ]] ; then
            echo "error: Not a valid input for argument $arg" >&2
            usage
            exit 1
        fi
    done    
    python3 $DIR/run.py patchweave -patron -t -id "${args[@]}" -o $OUT/$DATE -lt PATRON
    if [ $? -ne 0 ]; then
        echo "Failed to run patron"
        exit 1
    fi
}

safety_check "$@"
if [ "$1" == "test" ]; then
    if [ -z "$2" ]; then
        patron_test
    else
        patron_test_id "$@"
    fi
elif [ -z "$1" ]; then
    run_full
elif [ -z "$2" ]; then
    run_on_benchmark "$1"]
else
    run_on_ids "$@"
fi

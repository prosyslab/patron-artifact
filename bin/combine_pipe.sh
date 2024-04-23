parse () {
    sparrow -il -frontend claml $1
}

com () {
    local filename="$1"
    local filename_no_ext="${filename%.*}"  # Extract filename without extension
    local directory="/root/patron-artifact/pkg/analysis-target/$filename_no_ext"
    echo $filename
    echo $filename_no_ext
    echo $directory
    # Create the directory if it doesn't exist
    mkdir -p "$directory"

    # Move the file to the specified directory
    mv "$filename" "$directory/"
}

pipe() {
   local dir=$(basename "$(pwd)")
   local filename=$dir.c
   err
   parse *.i > $filename
   com $filename
}

pipe
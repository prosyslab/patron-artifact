parse () {
    sparrow -il -frontend claml *.i > $1
}

com () {
    local filename="$1"
    local filename_no_ext="${filename%.*}"  # Extract filename without extension
    local directory="$2/$filename_no_ext"
    # Create the directory if it doesn't exist
    mkdir -p "$directory"

    # Move the file to the specified directory
    mv "$filename" "$directory/"
}

pipe() {
   local dir=$(basename "$(pwd)")
   local filename=$dir.c
#    err
   parse $filename
   com $filename $1
}

pipe $1
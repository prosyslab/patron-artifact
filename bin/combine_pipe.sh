remove_error_prone_i_files() {
    for file in *.i; do sed -i 's/\bconst\b//g' $file; done
    for file in *.i; do sed -i 's/(int (char \* ))/(char \*)/g' "$file"; done
    for file in *.i; do sed -i '/_Float/,/;/d' "$file"; done
    for file in *.i; do sed -i '/#line [1-9][0-9]\{0,7\}/!{/# [1-9][0-9]\{0,7\}/!s/"\([^"\\]*\|\\.\)*"/"-"/g}' "$file"; done
}

remove_error_prone_c_files() {
    for file in *.c; do sed -i 's/\bconst\b//g' $file; done
    for file in *.c; do sed -i 's/(int (char \* ))/(char \*)/g' "$file"; done
    for file in *.c; do sed -i '/strfromf32/,/;/d' $file; done
    for file in *.c; do sed -i '/_Float/,/;/d' "$file"; done
    for file in *.i; do sed -i '/#line [1-9][0-9]\{0,7\}/!{/# [1-9][0-9]\{0,7\}/!s/"\([^"\\]*\|\\.\)*"/"-"/g}' "$file"; done
}

parse () {
    remove_error_prone_i_files
    sparrow -il -frontend claml *.i > $1
    remove_error_prone_c_files
}

com () {
    local filename="$1"
    # Extract filename without extension
    local filename_no_ext="${filename%.*}"  
    local directory="$2/$filename_no_ext"
    # Create the directory if it doesn't exist
    mkdir -p "$directory"

    # Move the file to the specified directory
    cp "$filename" "$directory/"
}

pipe() {
   local dir=$(basename "$(pwd)")
   local filename=$dir.c
   parse $filename
   com $filename $1
}

pipe $1
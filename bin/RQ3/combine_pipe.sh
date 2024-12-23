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

pipe() {
   local dir=$(basename "$(pwd)")
   local filename=$dir.c
   parse $filename
}

pipe
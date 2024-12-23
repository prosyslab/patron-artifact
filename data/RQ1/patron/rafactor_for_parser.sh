#!/bin/bash

# Iterate through all directories in the current directory
for dir in */; do
    dir=${dir%/}  # Remove trailing slash

    # Check if the directory contains .c files in each specified subdirectory
        sed -E -i 's/\b(.+?)\s*=\s*("[^"]*")/strcpy((char \*)\1, \2)/g' "$dir/bug"/*.c
        sed -E -i 's/\b(.+?)\s*=\s*("[^"]*")/strcpy((char \*)\1, \2)/g' "$dir/full_patch"/*.c
        sed -E -i 's/\b(.+?)\s*=\s*("[^"]*")/strcpy((char \*)\1, \2)/g' "$dir/patch"/*.c
    
done
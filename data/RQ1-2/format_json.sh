#!/bin/bash

# Function to run js-beautify on a JSON file
beautify_json() {
  local file="$1"
  echo "Beautifying $file"
  js-beautify -r -n "$file"
}

# Function to process directories
process_directories() {
  local dir="$1"
  # Check if .json file exists in the current directory
  

  # Recursively process subdirectories
  for subdirectory in "$dir"/*; do
    if [ -d "$subdirectory" ]; then
        echo "Processing $subdirectory"
      if [ -e "$subdirectory/label.json" ]; then
            beautify_json "$subdirectory/label.json"
      fi
    fi
  done
}

# Start processing directories from the current directory
for subdirectory in "."/*; do
    process_directories "$subdirectory"
done
echo "Finished processing directories."

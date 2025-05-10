#!/bin/bash

# Script to clean the datalake while preserving its structure
# This will remove all files but keep the directory structure intact

echo "Cleaning datalake..."

# Function to clean a directory while preserving its structure
clean_directory() {
    local dir=$1
    if [ -d "$dir" ]; then
        echo "Cleaning $dir..."
        # Remove all files and subdirectories
        find "$dir" -mindepth 1 -delete
        # Recreate the directory to ensure it exists
        mkdir -p "$dir"
    fi
}

# Clean each main directory in the datalake
clean_directory "datalake/raw/patents"
clean_directory "datalake/prepared/patents"
clean_directory "datalake/archived/patents"
clean_directory "datalake/transformed/patents"
clean_directory "datalake/raw/logs"
clean_directory "datalake/raw/metadata"

echo "Datalake cleaned successfully!" 
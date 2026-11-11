#!/bin/bash


timestamp=$(date +"%Y%m%d_%H%M%S")

output_dir="result/pet/fine"
powerstat_output_file="$output_dir/powerstat_$timestamp.txt"

if [ ! -d "$output_dir" ]; then
    mkdir -p "$output_dir"
fi

echo "Starting powerstat..."
powerstat -R 10 990 > "$powerstat_output_file" 2>&1

echo "Power consumption data has been saved to $powerstat_output_file"
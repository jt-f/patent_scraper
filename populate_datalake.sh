#!/bin/bash

# Script to populate the datalake from staging files
# This simulates the download process by copying files from staging to raw
STAGING_DIR="datalake/staging"

echo "Populating Joe's datalake from staging..."

# Copy all ZIP files from staging to raw
if [ -z "$(ls -A $STAGING_DIR/*.zip 2>/dev/null)" ]; then
    echo "No ZIP files found in $STAGING_DIR"
    exit 1
fi

# Copy each ZIP file to raw
for zip_file in "$STAGING_DIR"/*.zip; do
    if [ -f "$zip_file" ]; then
        filename=$(basename "$zip_file")
        echo "Copying $filename to raw..."
        cp "$zip_file" "datalake/raw/patents/"
    fi
done

echo "Datalake populated successfully!"
echo "Files are now in datalake/raw/patents/"
echo "You can now run the data_ingest.py script to process these files:"
echo "% poetry run python patent_scraper/src/data_ingest.py"
#!/bin/bash

# Define the root directory for the data lake
DATALAKE_ROOT="datalake"

# Create main zones
ZONES=(
    "raw"           # Raw ingested data
    "prepared"      # Cleaned and prepared data
    "transformed"   # Transformed and enriched data
    "archived"      # Archived historical data
)

# Create subdirectories for each zone
RAW_SUBDIRS=(
    "patents"       # Raw patent XML files
    "metadata"      # Associated metadata
    "logs"          # Ingestion logs
)

PREPARED_SUBDIRS=(
    "patents"       # Cleaned patent data
    "validated"     # Validated records
    "rejected"      # Records that failed validation
)

TRANSFORMED_SUBDIRS=(
    "enriched"      # Enriched patent data
    "aggregated"    # Aggregated statistics
    "reports"       # Generated reports
)

ARCHIVED_SUBDIRS=(
    "raw"           # raw data    
    "prepared"      # cleaned data
    "transformed"   # transformed data
)

# Create the root directory
echo "Creating data lake root directory: $DATALAKE_ROOT"
mkdir -p "$DATALAKE_ROOT"

# create a staging directory to mock the uspto remote store
# Put zip files you want to process in the staging directory to simulate the uspto remote store
STAGING_DIR="staging"
mkdir -p "$STAGING_DIR"

# Create main zones
for zone in "${ZONES[@]}"; do
    echo "Creating zone: $zone"
    mkdir -p "$DATALAKE_ROOT/$zone"
done

# Create subdirectories for raw zone
echo "Creating raw zone subdirectories..."
for subdir in "${RAW_SUBDIRS[@]}"; do
    mkdir -p "$DATALAKE_ROOT/raw/$subdir"
    # Create a sample file in each raw subdirectory
    touch "$DATALAKE_ROOT/raw/$subdir/.gitkeep"
done

# Create subdirectories for prepared zone
echo "Creating prepared zone subdirectories..."
for subdir in "${PREPARED_SUBDIRS[@]}"; do
    mkdir -p "$DATALAKE_ROOT/prepared/$subdir"
    touch "$DATALAKE_ROOT/prepared/$subdir/.gitkeep"
done

# Create subdirectories for transformed zone
echo "Creating transformed zone subdirectories..."
for subdir in "${TRANSFORMED_SUBDIRS[@]}"; do
    mkdir -p "$DATALAKE_ROOT/transformed/$subdir"
    touch "$DATALAKE_ROOT/transformed/$subdir/.gitkeep"
done

# Create subdirectories for archived zone
echo "Creating archived zone subdirectories..."
for subdir in "${ARCHIVED_SUBDIRS[@]}"; do
    mkdir -p "$DATALAKE_ROOT/archived/$subdir"
    touch "$DATALAKE_ROOT/archived/$subdir/.gitkeep"
done

echo "Data lake structure created successfully!"
echo "Structure:"
find "$DATALAKE_ROOT" -type d | sort | sed -e "s/[^-][^\/]*\//  |/g" -e "s/|\([^ ]\)/|-\1/"
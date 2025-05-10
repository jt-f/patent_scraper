import os
import glob
from pathlib import Path
import logging

from data_prepare import process_patent_zip, process_all_xml_files
from data_transform import extract_patent_data_from_xml_docs, store_patent_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_uspto_zip(year, file_name, data_type="grant"):
    """
    Download a USPTO patent data ZIP archive.

    Args:
        year (str): The year of the data file (e.g., "2024").
        file_name (str): The name of the ZIP file (e.g., "ipg240507.zip").
        data_type (str): "grant" for patent grants, "application" for applications.

    Returns:
        str or None: Path to the downloaded file if it exists, otherwise None.
    """
    download_dir = os.path.join("datalake", "raw", "patents")
    os.makedirs(download_dir, exist_ok=True)

    if data_type == "grant":
        base_url = f"https://data.uspto.gov/ui/datasets/products/files/PTGRXML/{year}/"
    elif data_type == "application":
        base_url = f"https://data.uspto.gov/ui/datasets/products/files/APPXML/{year}/"
    else:
        raise ValueError(f"Unknown data_type '{data_type}'. Choose 'grant' or 'application'.")

    download_url = base_url + file_name
    local_file_path = os.path.join(download_dir, file_name)

    # Not implemented: instruct user to download manually
    logger.info(f"Manual download required: {download_url} to {local_file_path}")
    logger.info("Place the file in the staging directory and run the populate_datalake.sh script.")

    if os.path.exists(local_file_path):
        return local_file_path
    return None


def process_zip_file(zip_file_path):
    """Process a single zip file and return the path to the stored JSON file."""
    logger.info(f"Processing zip file: {zip_file_path}")
    
    prepared_dir = process_patent_zip(zip_file_path)
    if not prepared_dir:
        logger.error(f"Failed to process ZIP file: {zip_file_path}")
        return None
    
    logger.info(f"Files ready in: {prepared_dir}")
    xml_docs = process_all_xml_files(prepared_dir)
    if not xml_docs:
        logger.error(f"Failed to process XML files in: {prepared_dir}")
        return None
    
    # Generate a unique output directory based on the zip filename
    zip_basename = os.path.basename(zip_file_path).split('.')[0]
    output_dir = os.path.join("datalake", "transformed", "patents", zip_basename)
    
    stored_file = extract_patent_data_from_xml_docs(xml_docs, output_dir)
    if stored_file:
        logger.info(f"Patent data stored in: {stored_file}")
        return stored_file
    
    logger.error(f"Failed to extract and store patent data from: {zip_file_path}")
    return None


def process_all_zip_files():
    """Process all ZIP files in the raw patents directory."""
    raw_dir = os.path.join("datalake", "raw", "patents")
    zip_files = glob.glob(os.path.join(raw_dir, "*.zip"))
    
    if not zip_files:
        logger.warning(f"No ZIP files found in {raw_dir}")
        return []
    
    logger.info(f"Found {len(zip_files)} ZIP files to process")
    results = []
    
    for zip_file in zip_files:
        result = process_zip_file(zip_file)
        if result:
            results.append(result)
    
    return results


def main():
    """
    Process all patent ZIP files in the raw directory.
    """
    logger.info("Starting patent data ingestion process")
    
    # Process all existing ZIP files
    processed_files = process_all_zip_files()
    
    if processed_files:
        logger.info(f"Successfully processed {len(processed_files)} ZIP files:")
        for file_path in processed_files:
            logger.info(f"  - {file_path}")
    else:
        logger.warning("No files were successfully processed")
        logger.info("Please download patent ZIP files to datalake/raw/patents directory")


if __name__ == "__main__":
    main()


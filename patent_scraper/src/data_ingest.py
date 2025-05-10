import os
import zipfile
import shutil
from datetime import datetime

def download_uspto_zip(year, file_name, data_type="grant"):
    """
    Downloads a weekly USPTO patent data ZIP archive.

    Args:
        year (str): The year of the data file (e.g., "2024").
        file_name (str): The name of the ZIP file (e.g., "ipg240507.zip").
        data_type (str): "grant" for patent grants, "application" for applications.
    """
    # Ensure the download directory exists
    download_dir = os.path.join("datalake", "raw", "patents")
    os.makedirs(download_dir, exist_ok=True)

    if data_type == "grant":
        base_url = f"https://data.uspto.gov/ui/datasets/products/files/PTGRXML/{year}/"
    elif data_type == "application":
        base_url = f"https://data.uspto.gov/ui/datasets/products/files/APPXML/{year}/"
    else:
        print(f"Error: Unknown data_type '{data_type}'. Choose 'grant' or 'application'.")
        return None

    download_url = base_url + file_name
    local_file_path = os.path.join(download_dir, file_name)

    print(f"Attempting to download {download_url} to {local_file_path}...")
    print(f"Unfortunately for now, this is not implemented, and you need to manually download:")
    print(f"{download_url} to {local_file_path}")
    print(f"to the staging directory, and then run the populate_datalake.sh script")
            
    # if file already exists,return success 
    if os.path.exists(local_file_path):
        return local_file_path

    return None

def archive_raw_file(zip_file_path, batch_dir):
    """
    Moves the raw ZIP file to the archive directory after successful processing.
    
    Args:
        zip_file_path (str): Path to the raw ZIP file
        batch_dir (str): Path to the prepared batch directory (for reference)
        
    Returns:
        bool: True if archiving was successful, False otherwise
    """
    try:
        # Create archive directory path
        archive_dir = os.path.join("datalake", "archived", "patents")
        os.makedirs(archive_dir, exist_ok=True)
        
        # Get the batch timestamp from the prepared directory name
        batch_name = os.path.basename(batch_dir)
        
        # Create archive filename with batch reference
        archive_filename = f"{os.path.basename(zip_file_path)}.{batch_name}"
        archive_path = os.path.join(archive_dir, archive_filename)
        
        # Move the file
        shutil.move(zip_file_path, archive_path)
        print(f"Archived raw file to: {archive_path}")
        return True
        
    except Exception as e:
        print(f"Error archiving raw file: {e}")
        return False

def process_patent_zip(zip_file_path):
    """
    Uncompresses a patent ZIP file and moves it to the prepared directory.
    
    Args:
        zip_file_path (str): Path to the ZIP file in the raw directory
        
    Returns:
        str: Path to the uncompressed directory in prepared, or None if failed
    """
    if not os.path.exists(zip_file_path):
        print(f"Error: ZIP file not found at {zip_file_path}")
        return None
        
    # Create prepared directory path
    prepared_dir = os.path.join("datalake", "prepared", "patents")
    os.makedirs(prepared_dir, exist_ok=True)
    
    # Create a timestamped directory for this batch
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_dir = os.path.join(prepared_dir, f"batch_{timestamp}")
    os.makedirs(batch_dir, exist_ok=True)
    
    try:
        print(f"Uncompressing {zip_file_path} to {batch_dir}...")
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(batch_dir)
            
        # Verify extraction
        extracted_files = os.listdir(batch_dir)
        if not extracted_files:
            print("Error: No files were extracted from the ZIP")
            shutil.rmtree(batch_dir)
            return None
            
        print(f"Successfully extracted {len(extracted_files)} files to {batch_dir}")
        
        # Archive the raw file after successful processing
        if not archive_raw_file(zip_file_path, batch_dir):
            print("Warning: Failed to archive raw file")
            
        return batch_dir
        
    except zipfile.BadZipFile:
        print(f"Error: {zip_file_path} is not a valid ZIP file")
        if os.path.exists(batch_dir):
            shutil.rmtree(batch_dir)
        return None
    except Exception as e:
        print(f"Error during extraction: {e}")
        if os.path.exists(batch_dir):
            shutil.rmtree(batch_dir)
        return None

# Example for a recent patent grant file
# To run this, you would first check https://data.uspto.gov/bulkdata/datasets/PTGRXML
# for a valid recent file name for the specified year.
# For instance, if 'ipg240507.zip' (May 7, 2024) is listed for year 2024:
# downloaded_file = download_uspto_zip(year="2024", file_name="ipg240507.zip", data_type="grant")

# Example for a recent patent application file
# Check https://data.uspto.gov/bulkdata/datasets/APPXML for a valid file.
# E.g., if 'ipa240502.zip' (May 2, 2024) is listed for year 2024:
# downloaded_file = download_uspto_zip(year="2024", file_name="ipa240502.zip", data_type="application")
if __name__ == "__main__":
    # Example usage
    year = "2025"
    file_name = "ipg250506.zip"
    data_type = "grant"
    downloaded_file = download_uspto_zip(year, file_name, data_type)
    
    if downloaded_file:
        print(f"Successfully found file: {downloaded_file}")
        # Process the downloaded file
        prepared_dir = process_patent_zip(downloaded_file)
        if prepared_dir:
            print(f"Files ready for processing in: {prepared_dir}")
        else:
            print("Failed to process ZIP file")
    else:
        print("Please download manually")


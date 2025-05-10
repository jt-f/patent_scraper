import os

from data_prepare import process_patent_zip, process_all_xml_files
from data_transform import extract_patent_data_from_xml_docs,store_patent_data

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
            # Process the files in the prepared directory
            xml_docs = process_all_xml_files(prepared_dir)
            if xml_docs:
                stored_file = extract_patent_data_from_xml_docs(xml_docs)
                if stored_file:
                    print(f"Successfully stored all patent data in: {stored_file}")
                else:
                    print("Failed to extract and store patent data")
            else:
                print("Failed to process XML files")
        else:
            print("Failed to process ZIP file")
    else:
        print("Please download manually")


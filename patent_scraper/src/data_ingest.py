import os

from data_prepare import process_patent_zip, process_all_xml_files
from data_transform import extract_patent_data_from_xml_docs, store_patent_data

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
    print(f"Manual download required: {download_url} to {local_file_path}")
    print("Place the file in the staging directory and run the populate_datalake.sh script.")

    if os.path.exists(local_file_path):
        return local_file_path
    return None


def main():
    """
    Example usage for ingesting a patent ZIP file.
    """
    year = "2025"
    file_name = "ipg250506.zip"
    data_type = "grant"
    try:
        downloaded_file = download_uspto_zip(year, file_name, data_type)
    except ValueError as err:
        print(f"Error: {err}")
        return

    if downloaded_file:
        print(f"Found file: {downloaded_file}")
        prepared_dir = process_patent_zip(downloaded_file)
        if prepared_dir:
            print(f"Files ready in: {prepared_dir}")
            xml_docs = process_all_xml_files(prepared_dir)
            if xml_docs:
                stored_file = extract_patent_data_from_xml_docs(xml_docs)
                if stored_file:
                    print(f"Patent data stored in: {stored_file}")
                else:
                    print("Failed to extract and store patent data.")
            else:
                print("Failed to process XML files.")
        else:
            print("Failed to process ZIP file.")
    else:
        print("Please download the file manually.")


if __name__ == "__main__":
    main()


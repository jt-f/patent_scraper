import os
import zipfile
import shutil
from datetime import datetime
import argparse

def archive_raw_file(zip_file_path, batch_dir):
    """
    Move the raw ZIP file to the archive directory after successful processing.

    Args:
        zip_file_path (str): Path to the raw ZIP file
        batch_dir (str): Path to the prepared batch directory (for reference)

    Returns:
        bool: True if archiving was successful, False otherwise
    """
    try:
        archive_dir = os.path.join("datalake", "archived", "patents")
        os.makedirs(archive_dir, exist_ok=True)
        batch_name = os.path.basename(batch_dir)
        archive_filename = f"{os.path.basename(zip_file_path)}.{batch_name}"
        archive_path = os.path.join(archive_dir, archive_filename)
        shutil.move(zip_file_path, archive_path)
        print(f"Archived raw file to: {archive_path}")
        return True
    except Exception as exc:
        print(f"Error archiving raw file: {exc}")
        return False

def process_patent_zip(zip_file_path):
    """
    Uncompress a patent ZIP file and move it to the prepared directory.

    Args:
        zip_file_path (str): Path to the ZIP file in the raw directory

    Returns:
        str or None: Path to the uncompressed directory in prepared, or None if failed
    """
    if not os.path.exists(zip_file_path):
        print(f"Error: ZIP file not found at {zip_file_path}")
        return None
    prepared_dir = os.path.join("datalake", "prepared", "patents")
    os.makedirs(prepared_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_dir = os.path.join(prepared_dir, f"batch_{timestamp}")
    os.makedirs(batch_dir, exist_ok=True)
    try:
        print(f"Uncompressing {zip_file_path} to {batch_dir}...")
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(batch_dir)
        extracted_files = os.listdir(batch_dir)
        if not extracted_files:
            print("Error: No files were extracted from the ZIP")
            shutil.rmtree(batch_dir)
            return None
        print(f"Successfully extracted {len(extracted_files)} files to {batch_dir}")
        if not archive_raw_file(zip_file_path, batch_dir):
            print("Warning: Failed to archive raw file")
        return batch_dir
    except zipfile.BadZipFile:
        print(f"Error: {zip_file_path} is not a valid ZIP file")
        if os.path.exists(batch_dir):
            shutil.rmtree(batch_dir)
        return None
    except Exception as exc:
        print(f"Error during extraction: {exc}")
        if os.path.exists(batch_dir):
            shutil.rmtree(batch_dir)
        return None

def split_concatenated_xml(concatenated_xml_file_path):
    """
    Split a concatenated USPTO XML file into a list of individual XML document strings.

    Args:
        concatenated_xml_file_path (str): Path to the concatenated XML file.

    Returns:
        list: A list of strings, where each string is a complete individual XML document.
    """
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'
    individual_xml_documents = []

    if not os.path.exists(concatenated_xml_file_path):
        print(f"Error: Concatenated XML file not found at {concatenated_xml_file_path}")
        return individual_xml_documents

    print(f"Splitting {concatenated_xml_file_path} into individual documents...")
    try:
        with open(concatenated_xml_file_path, 'r', encoding='UTF-8', errors='replace') as f:
            content = f.read()
        
        # Determine if it's a grant or application file to use the correct root tag
        base_filename = os.path.basename(concatenated_xml_file_path).lower()
        is_grant_file = "ipg" in base_filename or "pg" in base_filename
        is_application_file = "ipa" in base_filename or "pa" in base_filename

        # Find all complete patent documents by looking for start and end tags
        if is_grant_file:
            start_tag = "<us-patent-grant"
            end_tag = "</us-patent-grant>"
        elif is_application_file:
            start_tag = "<us-patent-application"
            end_tag = "</us-patent-application>"
        else:
            # If type unknown, look for either type
            start_tags = ["<us-patent-grant", "<us-patent-application"]
            end_tags = ["</us-patent-grant>", "</us-patent-application>"]
            
            # Find all potential document starts
            doc_starts = []
            for tag in start_tags:
                pos = 0
                while True:
                    pos = content.find(tag, pos)
                    if pos == -1:
                        break
                    # Find the previous XML declaration
                    xml_decl_pos = content.rfind(xml_declaration, 0, pos)
                    if xml_decl_pos != -1:
                        doc_starts.append(xml_decl_pos)
                    pos += len(tag)
            
            # Sort and deduplicate start positions
            doc_starts = sorted(set(doc_starts))
            
            # Extract complete documents
            for i, start_pos in enumerate(doc_starts):
                end_pos = -1
                # Look for the matching end tag
                for tag in end_tags:
                    pos = content.find(tag, start_pos)
                    if pos != -1 and (end_pos == -1 or pos < end_pos):
                        end_pos = pos + len(tag)
                
                if end_pos != -1:
                    doc_content = content[start_pos:end_pos].strip()
                    if doc_content:
                        individual_xml_documents.append(doc_content)
            
            print(f"Found {len(individual_xml_documents)} potential individual patent documents.")
            return individual_xml_documents

        # For known file types, use simpler logic
        pos = 0
        while True:
            # Find the start of a document
            start_pos = content.find(start_tag, pos)
            if start_pos == -1:
                break
                
            # Find the previous XML declaration
            xml_decl_pos = content.rfind(xml_declaration, 0, start_pos)
            if xml_decl_pos == -1:
                pos = start_pos + len(start_tag)
                continue
                
            # Find the matching end tag
            end_pos = content.find(end_tag, start_pos)
            if end_pos == -1:
                pos = start_pos + len(start_tag)
                continue
                
            # Extract the complete document
            doc_content = content[xml_decl_pos:end_pos + len(end_tag)].strip()
            if doc_content:
                individual_xml_documents.append(doc_content)
            
            pos = end_pos + len(end_tag)

        print(f"Found {len(individual_xml_documents)} potential individual patent documents.")
        

    except Exception as e:
        print(f"Error splitting XML file {concatenated_xml_file_path}: {e}")
        

    return individual_xml_documents

def process_all_xml_files(directory_path):
    """
    Process all XML files in the given directory and split them into individual documents.
    
    Args:
        directory_path (str): Path to the directory containing XML files
        
    Returns:
        dict: A dictionary mapping original XML filenames to lists of individual documents
    """
    if not os.path.exists(directory_path):
        print(f"Error: Directory not found at {directory_path}")
        return {}
        
    results = {}
    xml_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.xml')]
    
    if not xml_files:
        print(f"No XML files found in {directory_path}")
        return results
        
    print(f"Found {len(xml_files)} XML files to process")
    
    for xml_file in xml_files:
        file_path = os.path.join(directory_path, xml_file)
        print(f"\nProcessing {xml_file}...")
        individual_docs = split_concatenated_xml(file_path)

        results[xml_file] = individual_docs
        
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process patent XML files')
    parser.add_argument('--file', help='Path to a single XML file to process')
    parser.add_argument('--dir', help='Path to directory containing XML files to process')
    args = parser.parse_args()
    
    if args.file:
        split_concatenated_xml(args.file)
    elif args.dir:
        process_all_xml_files(args.dir)
    else:
        print("Please provide either --file or --dir argument")
        parser.print_help()

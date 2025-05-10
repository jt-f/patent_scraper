import xml.etree.ElementTree as ET
import re # For stripping DOCTYPE if needed
import json
import os
from datetime import datetime

def parse_single_patent_xml(xml_string_content):
    """
    Parses a single patent XML document string.

    Args:
        xml_string_content (str): A string containing a single, well-formed XML patent document.

    Returns:
        xml.etree.ElementTree.Element: The root element of the parsed XML tree, or None if parsing fails.
    """
    try:
        # ElementTree's default parser usually doesn't fetch external DTDs, which is often fine.
        # If DTD validation causes issues (e.g., network errors trying to fetch DTD),
        # one might strip the DOCTYPE declaration.
        # Example of stripping DOCTYPE (use with caution, may affect some advanced parsing):
        # xml_string_content_no_dtd = re.sub(r'<!DOCTYPE[^>]*>', '', xml_string_content, flags=re.IGNORECASE)
        # root = ET.fromstring(xml_string_content_no_dtd)
        
        root = ET.fromstring(xml_string_content)
        # print("Successfully parsed a sample XML document.")
        return root
    except ET.ParseError as e:
        print(f"Error parsing XML document: {e}")
        # print("Problematic XML content snippet (first 500 chars):")
        # print(xml_string_content[:500])
        return None
    except Exception as ex:
        print(f"An unexpected error occurred during parsing: {ex}")
        return None

def extract_patent_data(root_element):
    """
    Extracts key information from a parsed patent XML root element.
    Assumes a patent grant XML structure (e.g., us-patent-grant DTD).
    """
    patent_data = {
        "inventors": [],
        "assignees": [],
        "publication_date": "",
        "application_filing_date": "",
        "invention_title": "",
        "abstract": "",
        "cpc_classifications": []
    }

    if root_element is None:
        return patent_data

    # Path for bibliographic data
    bibliographic_data = root_element.find("./us-bibliographic-data-grant")
    if bibliographic_data is None: # Try application structure if grant not found
        bibliographic_data = root_element.find("./us-bibliographic-data-application")

    if bibliographic_data is not None:
        # Inventors
        # Find the <us-parties> element first
        us_parties_element = bibliographic_data.find("./us-parties")

        if us_parties_element is not None:
            # Then find the <inventors> element within <us-parties>
            inventors_element = us_parties_element.find("./inventors")
            if inventors_element is not None:
                for inventor_node in inventors_element.findall("./inventor"):
                    addressbook = inventor_node.find("./addressbook")
                    if addressbook is not None:
                        last_name = addressbook.findtext("./last-name", default="").strip()
                        first_name = addressbook.findtext("./first-name", default="").strip()
                        if last_name or first_name:
                            patent_data["inventors"].append(f"{first_name} {last_name}".strip())

        # If, for some reason, inventors might still be listed under us-applicants
        # (though not in your provided example for individual inventors),
        # you might adapt the first part of your original logic.
        # However, for the XML you've shown, the above block is the one that will work.
        # If you still want to keep the check for inventors disguised as applicants:

        if not patent_data["inventors"] and us_parties_element is not None:
            us_applicants_element = us_parties_element.find("./us-applicants")
            if us_applicants_element is not None:
                # Note: The attribute data-format='inventor' is speculative based on your original code.
                # You'd need to confirm if inventors are ever actually tagged this way under <us-applicant>.
                for applicant_node in us_applicants_element.findall("./us-applicant[@data-format='inventor']"):
                    addressbook = applicant_node.find("./addressbook")
                    if addressbook is not None:
                        # Typically, if an orgname is present, it's not an individual inventor.
                        if addressbook.find("./orgname") is None:
                            last_name = addressbook.findtext("./last-name", default="").strip()
                            first_name = addressbook.findtext("./first-name", default="").strip()
                            if last_name or first_name:
                                patent_data["inventors"].append(f"{first_name} {last_name}".strip())

        # Assignees/Companies
        assignees_found = False
        
        # Method 1: Standard USPTO format
        assignees_element = bibliographic_data.find("./assignees")
        if assignees_element is not None:
            for assignee in assignees_element.findall("./assignee"):
                addressbook = assignee.find("./addressbook")
                if addressbook is not None:
                    orgname = addressbook.findtext("./orgname", default="").strip()
                    if orgname:
                        patent_data["assignees"].append(orgname)
                        assignees_found = True
                    else: # Individual assignee
                        last_name = addressbook.findtext("./last-name", default="").strip()
                        first_name = addressbook.findtext("./first-name", default="").strip()
                        if last_name or first_name:
                            patent_data["assignees"].append(f"{first_name} {last_name}".strip())
                            assignees_found = True
        
        # Method 2: Alternate location within parties
        if not assignees_found:
            assignees_element = bibliographic_data.find("./parties/assignees")
            if assignees_element is not None:
                for assignee in assignees_element.findall("./assignee"):
                    addressbook = assignee.find("./addressbook")
                    if addressbook is not None:
                        orgname = addressbook.findtext("./orgname", default="").strip()
                        if orgname:
                            patent_data["assignees"].append(orgname)
                            assignees_found = True
                        else: # Individual assignee
                            last_name = addressbook.findtext("./last-name", default="").strip()
                            first_name = addressbook.findtext("./first-name", default="").strip()
                            if last_name or first_name:
                                patent_data["assignees"].append(f"{first_name} {last_name}".strip())
                                assignees_found = True
        
        # Method 3: Very old format with assignee-name
        if not assignees_found:
            for assignee in root_element.findall(".//assignee-name"):
                if assignee.text:
                    patent_data["assignees"].append(assignee.text.strip())
        
        # Publication Date
        pub_date_element = bibliographic_data.find("./publication-reference/document-id/date")
        if pub_date_element is not None:
            patent_data["publication_date"] = pub_date_element.text.strip() if pub_date_element.text else ""

        # Application Filing Date
        app_date_element = bibliographic_data.find("./application-reference/document-id/date")
        if app_date_element is not None:
            patent_data["application_filing_date"] = app_date_element.text.strip() if app_date_element.text else ""

        # Invention Title
        title_element = bibliographic_data.find("./invention-title")
        if title_element is not None:
            patent_data["invention_title"] = title_element.text.strip() if title_element.text else ""

        # CPC Classifications
        classifications_cpc = bibliographic_data.find("./classifications-cpc")
        if classifications_cpc is not None:
            # Main CPC(s)
            for main_cpc_node in classifications_cpc.findall("./main-cpc/classification-cpc"):
                section = main_cpc_node.findtext("./section", default="")
                cpc_class_val = main_cpc_node.findtext("./class", default="")
                subclass = main_cpc_node.findtext("./subclass", default="")
                main_group = main_cpc_node.findtext("./main-group", default="")
                subgroup = main_cpc_node.findtext("./subgroup", default="")
                full_cpc = f"{section}{cpc_class_val}{subclass}{main_group}/{subgroup}".replace(" ","")
                if full_cpc and full_cpc!= "/": # Ensure it's not empty
                    patent_data["cpc_classifications"].append(full_cpc)
            
            # Further CPC(s)
            for further_cpc_node_list in classifications_cpc.findall("./further-cpc"):
                for further_cpc_node in further_cpc_node_list.findall("./classification-cpc"):
                    section = further_cpc_node.findtext("./section", default="")
                    cpc_class_val = further_cpc_node.findtext("./class", default="")
                    subclass = further_cpc_node.findtext("./subclass", default="")
                    main_group = further_cpc_node.findtext("./main-group", default="")
                    subgroup = further_cpc_node.findtext("./subgroup", default="")
                    full_cpc = f"{section}{cpc_class_val}{subclass}{main_group}/{subgroup}".replace(" ","")
                    if full_cpc and full_cpc!= "/": # Ensure it's not empty
                        patent_data["cpc_classifications"].append(full_cpc)
        # Remove duplicates from CPC list
        patent_data["cpc_classifications"] = sorted(list(set(patent_data["cpc_classifications"])))


    # Abstract/Summary (relative to root element)
    abstract_element = root_element.find("./abstract")
    if abstract_element is not None:
        abstract_paragraphs = []
        for p_element in abstract_element.findall("./p"):
            if p_element.text:
                abstract_paragraphs.append(p_element.text.strip())
        patent_data["abstract"] = " ".join(abstract_paragraphs)
        
    return patent_data

def store_patent_data(patent_data_list, output_dir=None):
    """
    Stores all patent data in a single JSON file in the transformed directory of the datalake.
    
    Args:
        patent_data_list (list): List of dictionaries containing patent information
        output_dir (str, optional): Custom output directory. If None, uses default datalake/transformed/patents
    
    Returns:
        str: Path to the stored JSON file
    """
    if output_dir is None:
        output_dir = os.path.join("datalake", "transformed", "patents")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"patents_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Write all data to a single JSON file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(patent_data_list, f, indent=2, ensure_ascii=False)
    
    return filepath

def extract_patent_data_from_xml_docs(xml_docs):
    print(f"Found {len(xml_docs)} XML documents to process")
    all_patent_data = []
    
    for x in xml_docs:
        print(f"Processing batch {x}")
        print(f"Found {len(xml_docs[x])} XML documents to process")
        for y in xml_docs[x]:
            root = parse_single_patent_xml(y)
            patent_data = extract_patent_data(root)
            all_patent_data.append(patent_data)
    
    # Store all patent data in a single file
    if all_patent_data:
        stored_file = store_patent_data(all_patent_data)
        return stored_file
    return None
import xml.etree.ElementTree as ET
import re
import json
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

def parse_single_patent_xml(xml_string_content):
    """
    Parse a single patent XML document string and return the root element.
    Returns None if parsing fails.
    """
    try:
        root = ET.fromstring(xml_string_content)
        return root
    except ET.ParseError as e:
        logging.error(f"Error parsing XML document: {e}")
        return None
    except Exception as ex:
        logging.error(f"Unexpected error during parsing: {ex}")
        return None

def extract_patent_data(root_element):
    """
    Extract key information from a parsed patent XML root element.
    Assumes a patent grant XML structure.
    Returns a dictionary of patent data fields.
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
    bibliographic_data = root_element.find("./us-bibliographic-data-grant")
    if bibliographic_data is None:
        bibliographic_data = root_element.find("./us-bibliographic-data-application")
    if bibliographic_data is not None:
        us_parties_element = bibliographic_data.find("./us-parties")
        if us_parties_element is not None:
            inventors_element = us_parties_element.find("./inventors")
            if inventors_element is not None:
                for inventor_node in inventors_element.findall("./inventor"):
                    addressbook = inventor_node.find("./addressbook")
                    if addressbook is not None:
                        last_name = addressbook.findtext("./last-name", default="").strip()
                        first_name = addressbook.findtext("./first-name", default="").strip()
                        if last_name or first_name:
                            patent_data["inventors"].append(f"{first_name} {last_name}".strip())
        if not patent_data["inventors"] and us_parties_element is not None:
            us_applicants_element = us_parties_element.find("./us-applicants")
            if us_applicants_element is not None:
                for applicant_node in us_applicants_element.findall("./us-applicant[@data-format='inventor']"):
                    addressbook = applicant_node.find("./addressbook")
                    if addressbook is not None and addressbook.find("./orgname") is None:
                        last_name = addressbook.findtext("./last-name", default="").strip()
                        first_name = addressbook.findtext("./first-name", default="").strip()
                        if last_name or first_name:
                            patent_data["inventors"].append(f"{first_name} {last_name}".strip())
        assignees_found = False
        assignees_element = bibliographic_data.find("./assignees")
        if assignees_element is not None:
            for assignee in assignees_element.findall("./assignee"):
                addressbook = assignee.find("./addressbook")
                if addressbook is not None:
                    orgname = addressbook.findtext("./orgname", default="").strip()
                    if orgname:
                        patent_data["assignees"].append(orgname)
                        assignees_found = True
                    else:
                        last_name = addressbook.findtext("./last-name", default="").strip()
                        first_name = addressbook.findtext("./first-name", default="").strip()
                        if last_name or first_name:
                            patent_data["assignees"].append(f"{first_name} {last_name}".strip())
                            assignees_found = True
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
                        else:
                            last_name = addressbook.findtext("./last-name", default="").strip()
                            first_name = addressbook.findtext("./first-name", default="").strip()
                            if last_name or first_name:
                                patent_data["assignees"].append(f"{first_name} {last_name}".strip())
                                assignees_found = True
        if not assignees_found:
            for assignee in root_element.findall(".//assignee-name"):
                if assignee.text:
                    patent_data["assignees"].append(assignee.text.strip())
        pub_date_element = bibliographic_data.find("./publication-reference/document-id/date")
        if pub_date_element is not None and pub_date_element.text:
            patent_data["publication_date"] = pub_date_element.text.strip()
        app_date_element = bibliographic_data.find("./application-reference/document-id/date")
        if app_date_element is not None and app_date_element.text:
            patent_data["application_filing_date"] = app_date_element.text.strip()
        title_element = bibliographic_data.find("./invention-title")
        if title_element is not None and title_element.text:
            patent_data["invention_title"] = title_element.text.strip()
        classifications_cpc = bibliographic_data.find("./classifications-cpc")
        if classifications_cpc is not None:
            for main_cpc_node in classifications_cpc.findall("./main-cpc/classification-cpc"):
                section = main_cpc_node.findtext("./section", default="")
                cpc_class_val = main_cpc_node.findtext("./class", default="")
                subclass = main_cpc_node.findtext("./subclass", default="")
                main_group = main_cpc_node.findtext("./main-group", default="")
                subgroup = main_cpc_node.findtext("./subgroup", default="")
                full_cpc = f"{section}{cpc_class_val}{subclass}{main_group}/{subgroup}".replace(" ","")
                if full_cpc and full_cpc != "/":
                    patent_data["cpc_classifications"].append(full_cpc)
            for further_cpc_node_list in classifications_cpc.findall("./further-cpc"):
                for further_cpc_node in further_cpc_node_list.findall("./classification-cpc"):
                    section = further_cpc_node.findtext("./section", default="")
                    cpc_class_val = further_cpc_node.findtext("./class", default="")
                    subclass = further_cpc_node.findtext("./subclass", default="")
                    main_group = further_cpc_node.findtext("./main-group", default="")
                    subgroup = further_cpc_node.findtext("./subgroup", default="")
                    full_cpc = f"{section}{cpc_class_val}{subclass}{main_group}/{subgroup}".replace(" ","")
                    if full_cpc and full_cpc != "/":
                        patent_data["cpc_classifications"].append(full_cpc)
            patent_data["cpc_classifications"] = sorted(set(patent_data["cpc_classifications"]))
    abstract_element = root_element.find("./abstract")
    if abstract_element is not None:
        abstract_paragraphs = [p.text.strip() for p in abstract_element.findall("./p") if p.text]
        patent_data["abstract"] = " ".join(abstract_paragraphs)
    return patent_data

def store_patent_data(patent_data_list, output_dir=None):
    """
    Store all patent data in a single JSON file in the transformed directory of the datalake.
    Returns the path to the stored JSON file.
    """
    if output_dir is None:
        output_dir = os.path.join("datalake", "transformed", "patents")
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"patents_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(patent_data_list, f, indent=2, ensure_ascii=False)
    return filepath

def extract_patent_data_from_xml_docs(xml_docs, output_dir=None):
    """
    Process a dictionary of XML document batches and store extracted patent data.
    Returns the path to the stored JSON file or None if no data was processed.
    
    Args:
        xml_docs: Dictionary of XML documents to process
        output_dir: Optional directory to store the output JSON file
    """
    logging.info(f"Found {len(xml_docs)} XML documents to process")
    all_patent_data = []
    for batch_name in xml_docs:
        logging.info(f"Processing batch {batch_name}")
        logging.info(f"Found {len(xml_docs[batch_name])} XML documents to process")
        for xml_content in xml_docs[batch_name]:
            root = parse_single_patent_xml(xml_content)
            patent_data = extract_patent_data(root)
            all_patent_data.append(patent_data)
    if all_patent_data:
        stored_file = store_patent_data(all_patent_data, output_dir)
        return stored_file
    return None
from flask import Flask, jsonify, request
import json
import os
from datetime import datetime
from typing import List, Dict, Set
from pathlib import Path
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Directory containing patent JSON files
PATENTS_DIR = Path("datalake/transformed/patents")

# Global variable to store loaded patents
PATENTS_DATA = []

def load_patent_data() -> List[Dict]:
    """Load all patent JSON files from the patents directory."""
    patents = []
    
    logger.info(f"Attempting to load patents from: {PATENTS_DIR.absolute()}")
    
    if not PATENTS_DIR.exists():
        logger.error(f"Directory does not exist: {PATENTS_DIR.absolute()}")
        return patents
    
    json_files = list(PATENTS_DIR.glob("*.json"))
    logger.info(f"Found {len(json_files)} JSON files")
    
    for json_file in json_files:
        try:
            logger.info(f"Loading file: {json_file}")
            with open(json_file, 'r', encoding='utf-8') as f:
                patent_data = json.load(f)
                patents.append(patent_data)
                logger.info(f"Successfully loaded {json_file}")
        except Exception as e:
            logger.error(f"Error loading {json_file}: {str(e)}")
    

    logger.info(f"Total patent files loaded: {len(patents)}")
    return patents

def get_distinct_inventors(patents: List[Dict]) -> Set[str]:
    """Get all distinct inventors from the patent data."""
    inventors = set()
    for patent in patents:
        if patent.get('inventors'):
            print(patent['inventors'])
            for a in patent['inventors']:
                inventors.add(a)
    return inventors

def get_distinct_assignees(patents: List[Dict]) -> Set[str]:
    """Get all distinct assignees from the patent data."""
    assignees = set()
    for patent in patents:
        if patent.get('assignees'):
            print(patent['assignees'])
            for a in patent['assignees']:
                assignees.add(a)
            
    return assignees

def get_distinct_titles(patents: List[Dict]) -> Set[str]:
    """Get all distinct patent titles."""
    titles = set()
    for patent in patents:
        if patent.get('invention_title'):
            titles.add(patent['invention_title'])
    return titles

def filter_by_cpc_classification(patents: List[Dict], cpc_class: str, use_regex: bool = False) -> List[Dict]:
    """Filter patents by CPC classification."""
    if use_regex:
        pattern = re.compile(cpc_class)

        results = []
        for patent_file in patents:

            for p in patent_file:
                if p.get('cpc_classifications'):
                    for cpc in p['cpc_classifications']:
                        if pattern.search(cpc):
                            results.append(p)
                        break
        print(results)
        print('*******')
        return results
    else:
        return [p for p in patents 
                if 'cpc_classifications' in p and 
                any(cpc_class in cpc for cpc in p['cpc_classifications'])]

# Flask routes
@app.route('/api/inventors', methods=['GET'])
def get_inventors():
    cpc_class = request.args.get('cpc_class')
    use_regex = request.args.get('use_regex', 'false').lower() == 'true'
    
    patents = PATENTS_DATA
    if cpc_class:
        patents = filter_by_cpc_classification(patents, cpc_class, use_regex)
    else:
        patents = PATENTS_DATA[0]
    inventors = get_distinct_inventors(patents)
    return jsonify(list(inventors))

@app.route('/api/assignees', methods=['GET'])
def get_assignees():
    cpc_class = request.args.get('cpc_class')
    use_regex = request.args.get('use_regex', 'false').lower() == 'true'
    
    patents = PATENTS_DATA
    if cpc_class:
        patents = filter_by_cpc_classification(patents, cpc_class, use_regex)
    else:
        patents = PATENTS_DATA[0]
    assignees = get_distinct_assignees(patents)
    return jsonify(list(assignees))

@app.route('/api/titles', methods=['GET'])
def get_titles():
    cpc_class = request.args.get('cpc_class')
    use_regex = request.args.get('use_regex', 'false').lower() == 'true'
    
    if cpc_class:
        patents = filter_by_cpc_classification(PATENTS_DATA, cpc_class, use_regex)
    else:
        patents = PATENTS_DATA[0]
    
    titles = get_distinct_titles(patents)
    return jsonify(list(titles))

@app.route('/api/summary', methods=['GET'])
def get_summary():
    cpc_class = request.args.get('cpc_class')
    use_regex = request.args.get('use_regex', 'false').lower() == 'true'
    
    if cpc_class:
        patents = filter_by_cpc_classification(PATENTS_DATA, cpc_class, use_regex)
    else:
        patents = PATENTS_DATA[0]
    
    summary = {
        'inventors': list(get_distinct_inventors(patents)),
        'assignees': list(get_distinct_assignees(patents)),
        'titles': list(get_distinct_titles(patents))
    }
    return jsonify(summary)

@app.route('/api/debug', methods=['GET'])
def debug_data():
    """Endpoint to debug the structure of the loaded patent data."""
    if not PATENTS_DATA:
        return jsonify({"error": "No patent data loaded"})
    
    sample = PATENTS_DATA[0][0] if PATENTS_DATA[0] else {}
    
    result = {
        "patent_data_length": len(PATENTS_DATA),
        "first_file_length": len(PATENTS_DATA[0]) if PATENTS_DATA else 0,
        "sample_keys": list(sample.keys()) if sample else [],
        "inventors_field": sample.get("inventors", []) if sample else [],
        "assignees_field": sample.get("assignees", []) if sample else [],
        "title_field": sample.get("invention_title", "") if sample else ""
    }
    
    return jsonify(result)

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Looking for patents in: {PATENTS_DIR.absolute()}")
    
    # Load patent data at startup
    logger.info("Loading patent data...")
    PATENTS_DATA = load_patent_data()
    logger.info(f"Loaded {len(PATENTS_DATA)} patents into memory")
    
    app.run(debug=True, port=5000)

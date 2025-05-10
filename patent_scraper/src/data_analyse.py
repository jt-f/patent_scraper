from flask import Flask, jsonify, request
import json
import os
from datetime import datetime
from typing import List, Dict, Set
from pathlib import Path
import logging
import re
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Directory containing patent JSON files
PATENTS_DIR = Path("datalake/transformed/patents")
PATENTS_DATA: List[Dict] = []

def load_flattened_patent_data() -> List[Dict]:
    """Load and flatten all patent JSON files from the patents directory into a single list of patent dicts."""
    patents = []
    
    logger.info(f"Attempting to load patents from: {PATENTS_DIR.absolute()}")
    
    if not PATENTS_DIR.exists():
        logger.error(f"Directory does not exist: {PATENTS_DIR.absolute()}")
        return patents
    
    # Find all JSON files in the main directory and all subdirectories
    json_files = list(PATENTS_DIR.glob('**/*.json'))
    logger.info(f"Found {len(json_files)} JSON files")
    
    for json_file in json_files:
        try:
            logger.info(f"Loading file: {json_file}")
            with open(json_file, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
                if isinstance(file_data, list):
                    patents.extend(file_data)
                elif isinstance(file_data, dict):
                    patents.append(file_data)
            logger.info(f"Successfully loaded {json_file}")
        except Exception as e:
            logger.error(f"Error loading {json_file}: {str(e)}")
    
    logger.info(f"Total patent records loaded: {len(patents)}")
    return patents

# Helper functions for extracting distinct fields

def get_distinct_inventors(patents: List[Dict]) -> Set[str]:
    """Return all distinct inventors from the patent data."""
    return {inventor for patent in patents for inventor in patent.get('inventors', [])}

def get_distinct_assignees(patents: List[Dict]) -> Set[str]:
    """Return all distinct assignees from the patent data."""
    return {assignee for patent in patents for assignee in patent.get('assignees', [])}

def get_distinct_titles(patents: List[Dict]) -> Set[str]:
    """Return all distinct patent titles."""
    return {patent['invention_title'] for patent in patents if patent.get('invention_title')}

# Filtering logic

def filter_patents_by_cpc(patents: List[Dict], cpc_class: str = None, use_regex: bool = False) -> List[Dict]:
    """Filter patents by CPC classification, supporting regex if specified."""
    if not cpc_class:
        return patents
    if use_regex:
        try:
            pattern = re.compile(cpc_class)
        except re.error as e:
            logger.error(f"Invalid regex pattern for CPC class: {cpc_class} ({e})")
            return []
        return [p for p in patents if any(pattern.search(cpc) for cpc in p.get('cpc_classifications', []))]
    return [p for p in patents if any(cpc_class in cpc for cpc in p.get('cpc_classifications', []))]

# Decorator for extracting and filtering query params

def with_filtered_patents(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        cpc_class = request.args.get('cpc_class')
        use_regex = request.args.get('use_regex', 'false').lower() == 'true'
        filtered = filter_patents_by_cpc(PATENTS_DATA, cpc_class, use_regex)
        return func(filtered, *args, **kwargs)
    return wrapper

@app.route('/api/inventors', methods=['GET'])
@with_filtered_patents
def api_inventors(filtered_patents):
    """Return a list of distinct inventors from the loaded patent data."""
    if not filtered_patents:
        return jsonify([])
    return jsonify(sorted(get_distinct_inventors(filtered_patents)))

@app.route('/api/assignees', methods=['GET'])
@with_filtered_patents
def api_assignees(filtered_patents):
    """Return a list of distinct assignees from the loaded patent data."""
    if not filtered_patents:
        return jsonify([])
    return jsonify(sorted(get_distinct_assignees(filtered_patents)))

@app.route('/api/titles', methods=['GET'])
@with_filtered_patents
def api_titles(filtered_patents):
    """Return a list of distinct patent titles from the loaded patent data."""
    if not filtered_patents:
        return jsonify([])
    return jsonify(sorted(get_distinct_titles(filtered_patents)))

@app.route('/api/summary', methods=['GET'])
@with_filtered_patents
def api_summary(filtered_patents):
    """Return a summary of inventors, assignees, and titles from the loaded patent data."""
    if not filtered_patents:
        return jsonify({'inventors': [], 'assignees': [], 'titles': []})
    summary = {
        'inventors': sorted(get_distinct_inventors(filtered_patents)),
        'assignees': sorted(get_distinct_assignees(filtered_patents)),
        'titles': sorted(get_distinct_titles(filtered_patents))
    }
    return jsonify(summary)



if __name__ == '__main__':
    logger.info("Starting Flask application...")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Looking for patents in: {PATENTS_DIR.absolute()}")
    logger.info("Loading patent data...")
    PATENTS_DATA = load_flattened_patent_data()
    logger.info(f"Loaded {len(PATENTS_DATA)} patent records into memory")
    app.run(debug=True, port=5000)

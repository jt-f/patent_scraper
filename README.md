# patent_scraper

## Introduction
`patent_scraper` is a modular Python project for scraping, storing, and analyzing patent data. It provides tools to build a local datalake, ingest patent data, and run analytics via a web server.

## Overview of Modules
- **data_ingest.py**: Handles ingestion of patent data into the datalake.
- **data_prepare.py**: Prepares and cleans patent data for further processing.
- **data_transform.py**: Transforms raw or prepared data into analysis-ready formats.
- **data_analyse.py**: Provides analytics and reporting on patent data.

## Prerequisites
- Python 3.13.2 (recommended to use [pyenv](https://github.com/pyenv/pyenv#installation))
- [Poetry](https://python-poetry.org/docs/) for dependency management
- Bash shell (for running provided scripts)

## Quickstart
1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd patent_scraper
   ```
2. **Set up Python**
   ```bash
   pyenv update
   pyenv local 3.13.2
   ```
3. **Install dependencies**
   ```bash
   pip install poetry==1.8.4
   poetry install
   ```

## Build the Datalake
To create a mock datalake structure:
```bash
./create_datalake.sh
```
## Get some data
Place any downloaded patent zip files into the appropriate datalake directory as needed.
Currently supports: https://data.uspto.gov/ui/datasets/products/files/PTGRXML/{year}/*.zip
Recommended: https://data.uspto.gov/ui/datasets/products/files/PTGRXML/2025/ipg250506.zip

place it in the staging directory:
```bash
cd ./datalake/staging/
```

## Clean and Populate the Datalake
To clean and populate the datalake, use the following scripts:

- **Clean the datalake:**
  ```bash
  ./datalake/clean_datalake.sh
  ```
  everything historical has been removed, except from staging.
  You can use this script again to cleanup later before running again, if desired.

- **Populate the datalake:**
  ```bash
  ./datalake/populate_datalake.sh
  ```
  files have now been moved from staging to raw

## Ingest Data
Run the ingestion script to process and load data from staging into the datalake:
```bash
poetry run python patent_scraper/src/data_ingest.py
```

## Run the Analytics Server
Start the Flask analytics server:
```bash
poetry run python patent_scraper/src/data_analyse.py
```
The server will be available at [http://localhost:5000](http://localhost:5000).

## Use the Analytics Server
- Use the API endpoints to query patent data


## Control & Message Flow
```mermaid
graph TD
    A[User] -->|Uploads Data| B[Ingest Module]
    B -->|Stores| C[Datalake]
    C -->|Feeds| D[Analytics Server]
    D -->|Serves| E[Web/API Client]
```

## FUTURE
- Validation of XML files

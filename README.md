# patent_scraper

## Installation
Use pyenv to install a local python version
https://github.com/pyenv/pyenv#installation

### make sure you have the latest pyenv versions
```bash
cd patent_scraper
pyenv update
```

### We'll use python 3.13.2
```bash
pyenv local 3.13.2
```

### We'll use poetry for dependency management
https://python-poetry.org/docs/

```bash
 pip install poetry==1.8.4
 poetry install
 ```

### Create a mock datalake!
./create_datalake.sh

### Populate with any zip files you've downloaded



### FUTURE:
- validation of xml files

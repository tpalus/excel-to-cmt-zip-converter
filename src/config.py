"""
Configuration for Excel to XML conversion.
"""

from pathlib import Path
from typing import Dict, List

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Default project settings
DEFAULT_PROJECT = "project1"

# Input/Output paths
INPUT_DIR = BASE_DIR / "inputs"
OUTPUT_DIR = BASE_DIR / "outputs"

# Column filtering configuration
# Entity name -> list of column names to keep
# Empty list [] = all columns
# Prefixed with '-' = exclude these columns
# Otherwise = include only specified columns
COLUMNS_TO_KEEP: Dict[str, List[str]] = {
    # 'account': [],
    # 'contact': [],
    # 'phonecall': [],
    # 'partylist_phonecall': [],
    # Add your entities here
}

# File names
EXCEL_FILE_NAME = "inputdata.xlsx"
SCHEMA_FILE_NAME = "data_schema.xml"
DATA_OUTPUT_FILE = "data.xml"
ZIP_OUTPUT_FILE = "data.zip"

# Content Types XML - Fixed content for all projects
CONTENT_TYPES_XML = """<?xml version="1.0" encoding="utf-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/octet-stream" /></Types>"""

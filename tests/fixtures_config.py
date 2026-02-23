"""
Test configuration for fixture data.
"""

from pathlib import Path

# Test fixtures directory (for reference copies and expected output)
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
FIXTURES_PROJECT_DIR = FIXTURES_DIR / "test_project"

# Test input data (used by converter - matches inputs/ structure)
from src.config import INPUT_DIR
TEST_PROJECT_INPUT_DIR = INPUT_DIR / "test_project"

# Reference and expected output files
EXCEL_FILE_REFERENCE = FIXTURES_PROJECT_DIR / "excel-to-data-xml-converter-testing-file.xlsx"
SCHEMA_FILE_REFERENCE = FIXTURES_PROJECT_DIR / "data_schema.xml"
EXPECTED_OUTPUT = FIXTURES_DIR / "expected_data.xml"

# Actual input files used during conversion
EXCEL_FILE = TEST_PROJECT_INPUT_DIR / "inputdata.xlsx"
SCHEMA_FILE = TEST_PROJECT_INPUT_DIR / "data_schema.xml"

# Testing Framework

This directory contains test fixtures and tests for the Excel to XML converter.

## Test Structure

```
tests/
├── __init__.py                  # Test package
├── test_converter.py           # Main test suite
├── fixtures_config.py          # Test fixture configuration
└── fixtures/                   # Sample test data
    ├── __init__.py
    ├── expected_data.xml       # Expected conversion output
    └── test_project/
        ├── data_schema.xml     # Test schema
        └── excel-to-data-xml-converter-testing-file.xlsx (reference)

inputs/
└── test_project/               # Test input data (used by tests)
    ├── inputdata.xlsx          # Test Excel file (matched to config)
    └── data_schema.xml         # Test schema
```

## Running Tests

### Run all tests:
```bash
python -m pytest tests/ -v
```

### Run specific test class:
```bash
python -m pytest tests/test_converter.py::TestConversionIntegration -v
```

### Run with coverage report:
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

### Run unit tests only (skip integration tests):
```bash
python -m pytest tests/test_converter.py::TestUtilityFunctions -v
```

## Test Files

### `test_converter.py`
Contains three test classes:

1. **TestConverterSetup**
   - Validates module imports
   - Checks required directories exist
   - Verifies test fixtures are present

2. **TestUtilityFunctions**
   - Tests `safe_str()` value conversion
   - Tests `normalize_datetime_value()` formatting
   - Covers edge cases (None, NaN, empty values)

3. **TestConversionIntegration**
   - Full end-to-end conversion test with sample data
   - Validates XML structure and format
   - Checks entity and record counts
   - Verifies field values match expected output
   - Tests partylist relationships
   - Validates many-to-many relationships
   - Checks entity reference lookups
   - Verifies datetime and boolean conversions

## Sample Test Data

The test fixtures include:

- **4 contact records** with details like name, email, and parent relationships
- **2 appointment records** with:
  - Multiple required attendees (partylist)
  - DateTime conversion (DD.MM.YYYY HH:MM:SS → ISO format)
  - Contact relationships
- **3 sport category records** (ntg_sportcategory)
- **Many-to-many relationships** between contacts and sport categories
- **Entity references** (owner, account references)

## Expected Output

The `expected_data.xml` file contains the baseline output that the converter should produce from the test Excel file. Key features:

- Timestamp is present but not validated (varies per run)
- All entity, record, and field structures must match
- All relationship types must be correctly formatted
- All data type conversions must be correct

## Regression Testing

When you make changes to the converter logic:

1. **Run the full test suite** to ensure nothing breaks:
   ```bash
   python -m pytest tests/ -v
   ```

2. **If tests fail**, review the failure details:
   - Check which entity/field is causing issues
   - Verify the change is intentional
   - Update `expected_data.xml` if the change is correct

3. **Record expected output** after major changes:
   ```bash
   # Run converter on test data
   python -m src.converter
   
   # Copy outputs/data.xml to tests/fixtures/expected_data.xml
   Copy-Item "outputs/data.xml" "tests/fixtures/expected_data.xml"
   ```

## Validating Against Expected Output

The `TestConversionIntegration::test_output_consistency()` test compares:

- Number of entities
- Entity names
- Record count per entity

To perform a more detailed validation after major logic changes:

1. Generate new output:
   ```bash
   # Ensure DEFAULT_PROJECT = "test_project" in src/config.py
   python -m src.converter
   ```

2. Compare files:
   ```bash
   # View the generated XML
   type outputs/data.xml
   
   # Compare with expected
   diff outputs/data.xml tests/fixtures/expected_data.xml
   ```

3. If changes are correct, update expected output:
   ```bash
   Copy-Item outputs/data.xml tests/fixtures/expected_data.xml -Force
   ```

## Test Data Characteristics

The test dataset is designed to cover:
- ✅ Multiple entities
- ✅ String, number, boolean, datetime fields
- ✅ Entity references and owner fields
- ✅ Partylist (complex nested structures)
- ✅ Many-to-many relationships
- ✅ Multiple record counts per entity
- ✅ Datetime format conversion
- ✅ Boolean value conversion

## Debugging Tests

### View actual vs expected XML:

```python
# In test, add temporary code to print:
import xml.dom.minidom
generated_pretty = xml.dom.minidom.parseString(ET.tostring(self.xml_root)).toprettyxml()
expected_pretty = xml.dom.minidom.parseString(open(EXPECTED_OUTPUT).read()).toprettyxml()
print("GENERATED:")
print(generated_pretty)
print("\nEXPECTED:")
print(expected_pretty)
```

### Run converter directly on test data:

```bash
# Update src/config.py:
DEFAULT_PROJECT = "test_project"

# Run converter
python -m src.converter

# Check output/data.xml
```

## Adding New Tests

To add a new test:

1. Add test method to appropriate class in `test_converter.py`
2. Follow naming convention: `test_<what_you_are_testing>`
3. Include docstring explaining the test
4. Run `pytest` to verify it works

Example:
```python
def test_account_records(self):
    """Test that account records are correctly populated."""
    account_entity = self.xml_root.find(".//entity[@name='account']")
    records = account_entity.findall(".//record")
    self.assertGreater(len(records), 0, "Should have account records")
```

## Continuous Integration

When committing changes:
1. Run all tests: `python -m pytest tests/ -v`
2. Fix any failures
3. Update expected output if intentional changes
4. Commit both code changes and updated `expected_data.xml`

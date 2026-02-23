# Testing Guide

This guide explains how the testing framework works and how to use it when developing new features or making changes to the converter.

## Overview

The Excel to XML Converter includes a comprehensive testing framework with:

- **Unit Tests** - Testing individual functions and utilities
- **Integration Tests** - Full end-to-end conversion tests with sample data
- **Regression Tests** - Automated validation against expected output
- **Sample Test Data** - Real-world example with contacts, appointments, and relationships

## Quick Start

### Install Testing Dependencies

```bash
pip install pytest pytest-cov
```

### Run All Tests

```bash
# Using pytest
python -m pytest tests/ -v

# Or using the provided batch script (Windows)
run_tests.bat

# Or using the provided shell script (Linux/Mac)
bash run_tests.sh
```

### Run Specific Test Categories

```bash
# Unit tests only
python -m pytest tests/test_converter.py::TestConverterSetup -v
python -m pytest tests/test_converter.py::TestUtilityFunctions -v

# Integration tests only
python -m pytest tests/test_converter.py::TestConversionIntegration -v

# With coverage report
python -m pytest tests/ --cov=src --cov-report=html
```

## What Gets Tested

### Unit Tests (TestConverterSetup)
- ✅ All required modules can be imported
- ✅ Expected directories exist
- ✅ Fixture files are present

### Unit Tests (TestUtilityFunctions)
- ✅ `safe_str()` converts values correctly
  - None → empty string
  - NaN → empty string
  - Integers/floats → proper formatting
  - Booleans → "True"/"False"
- ✅ `normalize_datetime_value()` converts dates
  - Full datetime: `25.08.2020 11:30:00` → `2020-08-25T11:30:00.0000000Z`
  - Date only: `15.01.2020` → `2020-01-15T00:00:00.0000000Z`
  - Invalid dates → returns original value

### Integration Tests (TestConversionIntegration)

Uses real sample data with:
- 4 contact records with parent relationships
- 2 appointment records with complex partylist relationships
- 3 sport category records
- Many-to-many relationships

Tests validate:
- ✅ XML structure (root element, required attributes)
- ✅ Entity count and names match expectations
- ✅ Record counts per entity are correct
- ✅ Contact fields are properly populated
- ✅ Appointment records with partylist relationships
- ✅ Many-to-many relationships are correctly formatted
- ✅ Entity reference fields have correct lookup information
- ✅ DateTime values are normalized to ISO format
- ✅ Boolean values are converted to "True"/"False"
- ✅ Output structure matches expected baseline

## Sample Test Data

Location: `inputs/test_project/`

### Files
- `inputdata.xlsx` - Excel file with named tables
- `data_schema.xml` - Entity schema definition

### Fixture References
Location: `tests/fixtures/test_project/`

- `excel-to-data-xml-converter-testing-file.xlsx` - Original test file
- `data_schema.xml` - Original schema
- `expected_data.xml` - Baseline expected output

### Data Structure

**Contact Entity** (4 records)
```
- Timotej Palus (timpal@gmail.com)
- John Doe (johndeo@gmail.com)
- David King (davidking.2000@gmail.com)
- Michal Great (michalgreat2000@gmail.com)
```

**Appointment Entity** (2 records)
```
- Test App 1 (2020-08-25, 10:00-11:30, 3 attendees)
- Test App 2 (2020-01-13, 09:00-09:30, 1 attendee)
```

**Sport Category Entity** (3 records)
```
- Tenis
- Snooker
- Hockey
```

**Relationships**
- Contacts → Accounts (parent customer references)
- Appointments → Contacts (regarding object)
- Contacts → Sport Categories (M2M relationships)

## Regression Testing Workflow

When you make changes to the converter:

### 1. Run Tests to Check for Breakage

```bash
python -m pytest tests/ -v
```

If a test fails, it means your change broke existing functionality.

### 2. Review the Failure

```
FAILED tests/test_converter.py::TestConversionIntegration::test_output_consistency
AssertionError: Should have same number of entities as expected
```

This tells you:
- Which test failed
- What the assertion was
- What was expected vs. what was found

### 3. Fix the Issue

Modify your code to fix the problem. Common issues:

- **Entity counts don't match** - Check entity filtering logic
- **Field values are wrong** - Review field processing
- **Missing partylist entries** - Check partylist indexing
- **Datetime format incorrect** - Verify normalization function

### 4. Run Tests Again

```bash
python -m pytest tests/ -v
```

### 5. If Tests Pass, You're Done

Congratulations! Your changes maintain backward compatibility.

## Updating Expected Output

If you make intentional changes to the conversion logic that change the output:

### 1. Run Converter on Test Data

```bash
# Update config.py if needed
# Ensure DEFAULT_PROJECT = "test_project"

python -m src.converter
```

### 2. Review Generated Output

```bash
# Look at the generated output
type outputs\data.xml

# Compare with expected
# (review key differences)
```

### 3. Update Expected Output

If the changes are correct and intentional:

```bash
# Copy new output to expected
Copy-Item outputs\data.xml tests\fixtures\expected_data.xml -Force
```

### 4. Run Tests Again

```bash
python -m pytest tests/test_converter.py::TestConversionIntegration::test_output_consistency -v
```

Tests should now pass.

## Debugging Test Failures

### View Detailed XML Output

To see exactly what was generated vs. expected:

```python
# Add to test method temporarily:
import xml.dom.minidom

# Pretty-print generated XML
generated_str = ET.tostring(self.xml_root, encoding='unicode')
generated_pretty = xml.dom.minidom.parseString(generated_str).toprettyxml()
print("GENERATED:")
print(generated_pretty[:2000])  # First 2000 chars

# Load and pretty-print expected XML
with open(EXPECTED_OUTPUT) as f:
    expected_pretty = xml.dom.minidom.parse(f).toprettyxml()
print("\nEXPECTED:")
print(expected_pretty[:2000])
```

### Check Individual Entity

```python
# In test, add:
contact_entity = self.xml_root.find(".//entity[@name='contact']")
if contact_entity is not None:
    print(f"Contact records: {len(contact_entity.findall('.//record'))}")
    first_record = contact_entity.find(".//record")
    if first_record is not None:
        for field in first_record.findall("field"):
            print(f"  {field.get('name')}: {field.get('value')}")
```

### Run Converter Manually

To debug conversion logic:

```bash
# Update src/config.py:
DEFAULT_PROJECT = "test_project"

# Run converter with debug output:
python -c "
from src import ExcelToXmlConverter
try:
    c = ExcelToXmlConverter('test_project')
    root, path = c.process()
    print(f'Conversion successful: {path}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
"
```

## Adding New Tests

When adding new features, add corresponding tests:

```python
def test_my_new_feature(self):
    \"\"\"Test that my new feature works correctly.\"\"\"
    # Arrange
    entity = self.xml_root.find(".//entity[@name='contact']")
    
    # Act
    records = entity.findall(".//record")
    
    # Assert
    self.assertGreater(len(records), 0, "Should have records")
    self.assertEqual(records[0].get("id"), "expected-id")
```

1. Use the Arrange-Act-Assert pattern
2. Write clear docstrings
3. Include descriptive assertion messages
4. Run your test to verify it works

## Continuous Integration

For team development, integrate tests into CI/CD:

```bash
# Before committing:
python -m pytest tests/ -v --cov=src

# All tests must pass
# Coverage should be >= 80% for modified files
```

## Test Coverage

To see which parts of the code are tested:

```bash
python -m pytest tests/ --cov=src --cov-report=html
```

Open `htmlcov/index.html` to see coverage report.

Target: **80%+ coverage** on all modified code.

## Troubleshooting

### "Test fixture not found"
- Ensure files are in `inputs/test_project/`
- Check `tests/fixtures_config.py` has correct paths

### "Excel file not found"
- Verify `inputdata.xlsx` exists in `inputs/test_project/`
- Check file permissions

### "Schema file not found"
- Verify `data_schema.xml` exists in `inputs/test_project/`
- Check file is not corrupted

### Test passes locally but fails in CI
- Compare Python versions
- Check file paths (use relative paths)
- Verify all dependencies are in requirements.txt

### Output doesn't match expected
- Check timestamps (timestamps vary, not compared in tests)
- Verify datetime format normalization
- Check entity ordering (alphabetical)

## Further Reading

- [pytest documentation](https://docs.pytest.org/)
- [Python unittest documentation](https://docs.python.org/3/library/unittest.html)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## Questions?

Refer to:
1. `tests/README.md` - Detailed testing framework docs
2. `DEVELOPMENT.md` - Development setup and guidelines
3. `README.md` - Main project documentation

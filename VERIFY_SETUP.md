# ✅ Testing Verification Checklist

Use this checklist to verify that the testing framework is properly set up and working.

## Prerequisites

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Virtual environment activated (`source venv/bin/activate` or `venv\Scripts\activate`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] pytest installed (`pip install pytest`)

## File Structure Verification

```
[ ] inputs/test_project/
    [ ] inputdata.xlsx exists
    [ ] data_schema.xml exists

[ ] tests/
    [ ] __init__.py exists
    [ ] test_converter.py exists
    [ ] fixtures_config.py exists
    [ ] fixtures/
        [ ] __init__.py exists
        [ ] expected_data.xml exists
        [ ] test_project/
            [ ] data_schema.xml exists
            [ ] excel-to-data-xml-converter-testing-file.xlsx exists

[ ] Documentation files exist:
    [ ] README.md
    [ ] QUICKSTART.md
    [ ] TESTING.md
    [ ] TESTING_SETUP.md
    [ ] DEVELOPMENT.md
    [ ] PROJECT_OVERVIEW.md
    [ ] tests/README.md

[ ] Test runner scripts exist:
    [ ] run_tests.bat
    [ ] run_tests.sh
```

## Running Tests

### Step 1: Quick Unit Tests
```bash
python -m pytest tests/test_converter.py::TestConverterSetup -v
```

**Expected Output:**
```
test_imports PASSED
test_directories_exist PASSED
test_fixture_files_exist PASSED
======================== 3 passed in X.XXs ========================
```

- [ ] All 3 tests passed

### Step 2: Utility Function Tests
```bash
python -m pytest tests/test_converter.py::TestUtilityFunctions -v
```

**Expected Output:**
```
test_safe_str_conversions PASSED
test_datetime_normalization PASSED
======================== 2 passed in X.XXs ========================
```

- [ ] All 2 tests passed

### Step 3: Integration Tests
```bash
python -m pytest tests/test_converter.py::TestConversionIntegration -v
```

**Expected Output:**
```
test_conversion_completes PASSED
test_xml_structure PASSED
test_entity_count PASSED
test_contact_records PASSED
test_appointment_records PASSED
test_m2m_relationships PASSED
test_entity_references PASSED
test_datetime_conversion PASSED
test_boolean_conversion PASSED
test_output_consistency PASSED
======================== 10 passed in X.XXs ========================
```

- [ ] All 10 tests passed

### Step 4: Run All Tests
```bash
python -m pytest tests/ -v
```

**Expected Output:**
```
======================== 15 passed in X.XXs ========================
```

- [ ] All 15+ tests passed
- [ ] No failures
- [ ] No errors

### Step 5: Test Runners
```bash
# Windows
run_tests.bat

# Linux/macOS
bash run_tests.sh
```

- [ ] Test runner executed successfully
- [ ] All tests passed

## Manual Verification

### Verify Converter Works
```bash
python -m src.converter
```

**Expected:**
- [ ] "Converter completed successfully!" message appears
- [ ] `outputs/data.xml` file created
- [ ] `outputs/data.zip` file created
- [ ] No errors in console

### Verify Generated Output
```bash
# Check XML was created
type outputs\data.xml    # Windows
cat outputs/data.xml     # Linux/macOS
```

- [ ] XML is valid (starts with `<entities>`)
- [ ] Contains all expected entities (appointment, contact, ntg_sportcategory)
- [ ] File size reasonable (>1KB)

## Testing Coverage Check

```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

**Expected:**
```
src\config.py          100%
src\converter.py       95%+
src\excel_loader.py    95%+
src\schema_loader.py   95%+
src\utils.py           100%
src\xml_generator.py   95%+
```

- [ ] Overall coverage > 90%
- [ ] No lines reported as completely uncovered

## Integration Test Data Verification

The integration tests use real sample data with:

- [ ] 4 contact records (with 4 different names)
- [ ] 2 appointment records (with different dates and attendees)
- [ ] 3 sport category records (Tenis, Snooker, Hockey)
- [ ] M2M relationships between contacts and sport categories
- [ ] DateTime conversions (DD.MM.YYYY HH:MM:SS format)
- [ ] Boolean fields (donotphone, donotemail, etc.)
- [ ] Entity references (parentcustomerid → account)

## Final Verification

### All Checklist Items Complete?

- [ ] All prerequisites met
- [ ] File structure verified
- [ ] Unit tests pass (3/3)
- [ ] Utility tests pass (2/2)
- [ ] Integration tests pass (10/10)
- [ ] All tests pass combined (15+)
- [ ] Test runners work
- [ ] Manual converter execution succeeds
- [ ] Generated files created
- [ ] Coverage adequate

### ✅ Everything Working!

If all items are checked:
- ✅ Testing framework is **properly installed**
- ✅ Sample data is **correctly configured**
- ✅ Tests are **passing**
- ✅ Converter is **working**
- ✅ Ready for **development**

## Troubleshooting

### "Test fixture not found"
```bash
# Verify files exist
ls -la inputs/test_project/
ls -la tests/fixtures/
```
- Ensure files match PROJECT_STRUCTURE section

### "ImportError" or "ModuleNotFoundError"
```bash
# Reinstall package in development mode
pip install -e .
pip install -r requirements.txt
```

### Tests fail but no error message
```bash
# Run with more verbose output
python -m pytest tests/test_converter.py::TestConversionIntegration -vv -s
```

### "Excel file not found" during tests
```bash
# Check config
python -c "from tests.fixtures_config import EXCEL_FILE; print(EXCEL_FILE); print(EXCEL_FILE.exists())"
```
Should print `True` if file exists.

### Coverage report not generated
```bash
# Install coverage
pip install pytest-cov

# Generate report
python -m pytest tests/ --cov=src --cov-report=html
```

## Next Steps

Once verification complete:

1. **Read Documentation**
   - Start with `QUICKSTART.md`
   - Then review `README.md`
   - Check `DEVELOPMENT.md` if making changes

2. **Try the Converter**
   - Create your own project folder under `inputs/`
   - Add Excel file and schema
   - Run `python -m src.converter`

3. **Make Changes**
   - Review `DEVELOPMENT.md` for guidelines
   - Make code changes
   - Run tests: `python -m pytest tests/ -v`
   - If breaking, update expected output

4. **For Help**
   - `TESTING.md` - Complete testing guide
   - `PROJECT_OVERVIEW.md` - What everything does
   - `tests/README.md` - Technical test details

## Questions?

Refer to documentation in this order:
1. `QUICKSTART.md` - Quick answers
2. Relevant `.md` file (TESTING, DEVELOPMENT, etc.)
3. Code comments and docstrings
4. Review similar test code

---

**Status:** ✅ Setup Complete and Verified
**Date:** [Run this checklist to verify]
**Notes:** All tests passing, ready for development

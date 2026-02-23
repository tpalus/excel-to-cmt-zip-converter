# Quick Start Guide

## 5-Minute Setup

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Prepare Your Data

1. Create a folder: `inputs/your_project/`
2. Place your files there:
   - `Excel file.xlsx` (with named tables)
   - `data_schema.xml`

Example:
```
inputs/
└── my_project/
    ├── MyData.xlsx
    └── data_schema.xml
```

### Step 3: Configure (if needed)

Edit `src/config.py`:

```python
DEFAULT_PROJECT = "my_project"  # Change this to your folder name

# Optional: Filter columns
COLUMNS_TO_KEEP = {
    'entity_name': [],  # Empty = all columns
    # or
    'contact': ['name', 'email'],  # Only these
    # or
    'account': ['-phone'],  # All except phone
}
```

### Step 4: Run

```bash
python -m src.converter
```

Output files appear in `outputs/`:
- `data.xml` - Converted XML
- `data.zip` - Packaged archive

## Configuration Examples

### Example 1: Export All Data

```python
COLUMNS_TO_KEEP = {}  # or remove entries entirely
```

### Example 2: Export Specific Columns

```python
COLUMNS_TO_KEEP = {
    'contact': ['firstname', 'lastname', 'email'],
    'account': ['name', 'accountnumber'],
}
```

### Example 3: Exclude Columns

```python
COLUMNS_TO_KEEP = {
    'contact': ['-internalcomments', '-notes'],  # Skip these columns
    'account': [],  # Keep everything else
}
```

## Excel File Format Requirements

1. **Use Named Tables:**
   - Select your data range
   - Insert → Table
   - Table name must match entity name in schema

2. **First Row = Headers:**
   - Headers must match field names in schema
   - Case-sensitive

3. **No Merged Cells:**
   - Each cell = one value

4. **Data Types:**
   - Dates: `DD.MM.YYYY` or `DD.MM.YYYY HH:MM:SS`
   - Numbers: Standard format
   - Text: Any text content

## Advanced Excel Scenarios

For complex relationship types, see [EXCEL_SCENARIOS.md](EXCEL_SCENARIOS.md):

- **Polymorphic Lookups** with `*_entityreference` columns
- **Many-to-Many (M2M)** relationships  
- **Partylist** (nested attendee lists)
- **Owner** fields (system user references)
- Complete real-world examples

## Schema File Format

```xml
<?xml version="1.0" encoding="utf-8"?>
<schema>
  <entity name="contact" displayname="Contact" primaryidfield="contactid">
    <fields>
      <field name="contactid" type="string" displayname="Contact ID"/>
      <field name="firstname" type="string" displayname="First Name"/>
      <field name="ownerid" type="owner" displayname="Owner"/>
    </fields>
  </entity>
</schema>
```

Key elements:
- `name`: Must match Excel table name
- `primaryidfield`: Unique identifier column
- `displayname`: Display name for documentation
- Field `type`: `string`, `number`, `entityreference`, `owner`, etc.

## Best Practices

### Start Small, Test First

**DO THIS:**
1. Create Excel with **only a few rows** (5-10 test records)
2. Run converter and verify output looks correct
3. Once everything works, add more data

**WHY:**
- Large Excel files (1000+ rows) are slow to open and edit
- Easier to debug issues with small test datasets
- Can catch schema/format errors early
- Once structure is validated, scale up

### Example Workflow

```bash
# Step 1: Start with minimal data
# Create: inputs/myproject/test.xlsx (10 rows)
python -m src.converter

# Step 2: Check output
# Review: outputs/data.xml
# Verify: Contacts, relationships, fields look right

# Step 3: Scale up
# Replace: test.xlsx with full_data.xlsx (1000+ rows)
python -m src.converter

# Step 4: Run tests
python -m pytest tests/ -v
```

## Troubleshooting

**"Project directory not found"**
- Check folder exists: `inputs/your_project/`
- Check folder name in `config.py` matches exactly

**"Excel file not found"**
- Check Excel file name in `inputs/your_project/`
- Update `EXCEL_FILE_NAME` in `config.py` if needed

**"Schema file not found"**
- Ensure `data_schema.xml` is in project folder
- Check file name in `config.py`

**Empty XML output**
- Verify Excel tables are created using Insert → Table
- Check table names match schema entities exactly
- Verify primary key column exists

**Missing columns in output**
- Check `COLUMNS_TO_KEEP` configuration
- Verify column names match Excel headers (case-sensitive)
- Remove disabled entities from `COLUMNS_TO_KEEP`

**Excel file slow to open (1000+ rows)**
- This is normal with large datasets
- Use approach above: Start with small test file first
- Once verified, replace with full dataset

## Testing with Sample Data

1. Create test structure:
   ```
   inputs/test/
   ├── test.xlsx
   └── test_schema.xml
   ```

2. Update config:
   ```python
   DEFAULT_PROJECT = "test"
   COLUMNS_TO_KEEP = {}  # Export everything
   ```

3. Run converter

4. Check `outputs/data.xml`

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [DEVELOPMENT.md](DEVELOPMENT.md) for development setup
- Review [tests/test_converter.py](tests/test_converter.py) for code examples

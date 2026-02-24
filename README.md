# Excel to CMT XML Converter

Convert Excel spreadsheets to CMT-compatible XML and ZIP packages for data migration.

## Overview

This tool processes Excel files containing entity data according to a defined schema and generates:
- `data.xml` - XML representation of all entities and relationships
- `data.zip` - Compressed archive containing XML, schema, and content types

**📖 Documentation Guides:**
- [QUICKSTART.md](QUICKSTART.md) - 5-minute setup
- [EXCEL_SCENARIOS.md](EXCEL_SCENARIOS.md) - ⭐ **Advanced setup for lookups, M2M, partylist**
- [TESTING.md](TESTING.md) - Running tests and validation

## Project Structure

```
excel-to-cmt-zip-converter/
├── src/                           # Main source code
│   ├── __init__.py
│   ├── config.py                 # Configuration settings
│   ├── converter.py              # Main conversion orchestrator
│   ├── excel_loader.py           # Excel file loading
│   ├── schema_loader.py          # Schema parsing
│   ├── utils.py                  # Utility functions
│   └── xml_generator.py          # XML generation
├── inputs/                        # Input data directory
│   ├── test_project/             # ✅ Test data (included)
│   │   ├── inputdata.xlsx
│   │   └── data_schema.xml
│   └── your_project/             # ➕ Create for your data
├── outputs/                       # Output directory (auto-created)
│   ├── data.xml                  # Converted XML
│   └── data.zip                  # Packaged archive
├── tests/                         # Test files & fixtures
├── .gitignore                    # Git ignore rules
├── requirements.txt               # Python dependencies
├── setup.py                      # Package setup
└── README.md                     # This file
```

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd excel-to-cmt-zip-converter
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create your project folder in `inputs/`:
```bash
mkdir inputs/your_project
```

### Folder Structure After Clone

```
excel-to-cmt-zip-converter/
├── inputs/
│   ├── test_project/          # ✅ Comes with test data (for testing)
│   │   ├── inputdata.xlsx
│   │   └── data_schema.xml
│   └── your_project/          # ➕ Create this for your data
│       ├── your_data.xlsx
│       └── data_schema.xml
├── outputs/                   # Created automatically, stores results
│   ├── data.xml              # Generated XML output
│   └── data.zip              # Generated ZIP archive
└── [other files]
```

## Usage

### Basic Usage

1. **Prepare your data:**
   - Place your Excel file in `inputs/<project>/`
   - Place your schema XML in `inputs/<project>/`

2. **Configure settings (optional):**
   - Edit `src/config.py` to adjust:
     - `COLUMNS_TO_KEEP` - Filter which columns to include per entity
     - `EXCEL_FILE_NAME` - Excel file name
     - `SCHEMA_FILE_NAME` - Schema XML file name

3. **Run the converter:**
```bash
python -m src.converter
```

### Advanced Usage

**With custom project name:**
```bash
python -c "from src import main; main('your_project_name')"
```

**Without ZIP creation:**
```bash
python -c "from src import main; main(create_zip_file=False)"
```

**Programmatic usage:**
```python
from src import ExcelToXmlConverter

converter = ExcelToXmlConverter(project='pct24008')
xml_root, xml_path = converter.process()
zip_path = converter.create_zip(xml_path)

print(f"Generated: {xml_path}")
print(f"Packaged: {zip_path}")
```

## Advanced Excel Scenarios

For detailed setup instructions on specific relationship types, see [**EXCEL_SCENARIOS.md**](EXCEL_SCENARIOS.md):

- 🔗 **Polymorphic Lookups** - Using `*_entityreference` columns for multiple entity types
- 🔀 **Many-to-Many Relationships** - Setting up M2M junction tables  
- 👥 **Partylist Fields** - Complex nested relationships like meeting attendees
- 💼 **Owner Fields** - Special systemuser references
- 📋 **Complete Examples** - Real-world setups with all features

## Configuration

### Column Filtering

In `src/config.py`, use `COLUMNS_TO_KEEP` to control which columns are exported:

```python
COLUMNS_TO_KEEP = {
    'account': ['name', 'email'],          # Only these columns
    'contact': ['-telephone1'],            # All except telephone1
    'phonecall': [],                       # All columns
}
```

## Data Transformation Features

### Datetime Normalization
- Automatically converts dates like `25.08.2020 11:30:00` to ISO format
- Adds timezone indicator (`Z`) for UTC

### Value Safe Conversion
- Removes trailing `.0` from float values representing integers
- Handles NaN, None, and empty values gracefully
- Preserves boolean values as `True`/`False`

### Entity References
- Automatically extracts lookup entities from `*_entityreference` columns
- Supports `owner` and `entityreference` field types
- Maintains relationship integrity

### Many-to-Many Relationships
- Indexes and processes M2M relationships from schema
- Generates proper XML structure for relationship mappings

### Partylist Support
- Processes `partylist_*` tables separately
- Generates nested field structures for complex relationships
- Preserves activity metadata

## File Format

### Input: Excel (XLSX)
- Named table format with headers
- Tables map to entities in the schema

### Input: Schema (XML)
```xml
<entity name="contact" displayname="Contact" primaryidfield="contactid">
  <fields>
    <field name="firstname" type="string" displayname="First Name"/>
    <field name="ownerid" type="owner" displayname="Owner"/>
  </fields>
</entity>
```

### Output: XML
```xml
<entities xmlns:xsd="..." xmlns:xsi="..." timestamp="...">
  <entity name="contact" displayname="Contact">
    <records>
      <record id="12345">
        <field name="firstname" value="John"/>
        <field name="ownerid" value="user-id" lookupentity="systemuser" lookupentityname="default"/>
      </record>
    </records>
    <m2mrelationships/>
  </entity>
</entities>
```

## Testing

Place test files in the `tests/` directory. Example test structure:

```python
# tests/test_converter.py
import unittest
from src import ExcelToXmlConverter

class TestConverter(unittest.TestCase):
    def test_conversion(self):
        converter = ExcelToXmlConverter('test_project')
        xml_root, _ = converter.process()
        self.assertIsNotNone(xml_root)
```

Run tests:
```bash
python -m pytest tests/
```

## Troubleshooting

### "Excel file not found"
- Ensure Excel file is placed in `inputs/<project>/`
- Check file name matches `EXCEL_FILE_NAME` in config

### "Schema file not found"
- Ensure `data_schema.xml` is in `inputs/<project>/`
- Check file name in config

### "No columns found for entity"
- Review `COLUMNS_TO_KEEP` configuration
- Ensure column names match Excel headers exactly (case-sensitive)

### Empty output XML
- Check that Excel tables are named (using Excel's Table feature)
- Verify tables are listed in schema
- Check `COLUMNS_TO_KEEP` isn't filtering all columns

## Best Practices

1. **Version Control:**
   - Keep schema and configuration files in git
   - Add input/output folders to `.gitignore`

2. **Data Quality:**
   - Remove empty rows from Excel tables
   - Ensure consistent data types in columns
   - Validate entity references before conversion

3. **Configuration:**
   - Keep separate config for different projects
   - Document column filtering decisions
   - Test with sample data first

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

**MIT License Summary:**
- ✅ Free to use, modify, and distribute
- ✅ Commercial and private use allowed
- ⚠️ Must include license and copyright notice

Copyright (c) 2026 Timotej Palus

## Contributing

Contributions are welcome! Please feel free to:
- Report issues
- Suggest improvements
- Submit pull requests

## Support

For issues and questions:
- Check [QUICKSTART.md](QUICKSTART.md) for common setup issues
- Review [EXCEL_SCENARIOS.md](EXCEL_SCENARIOS.md) for advanced examples
- See [TESTING.md](TESTING.md) for testing and validation

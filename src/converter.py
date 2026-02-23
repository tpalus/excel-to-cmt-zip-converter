"""
Main conversion script: Excel to XML + ZIP packaging.
"""

import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Dict, List, Optional

from .config import (
    BASE_DIR, INPUT_DIR, OUTPUT_DIR, DEFAULT_PROJECT,
    COLUMNS_TO_KEEP, EXCEL_FILE_NAME, SCHEMA_FILE_NAME,
    DATA_OUTPUT_FILE, ZIP_OUTPUT_FILE, CONTENT_TYPES_XML
)
from .excel_loader import ExcelLoader
from .schema_loader import SchemaLoader
from .utils import safe_str
from .xml_generator import XMLGenerator


class ExcelToXmlConverter:
    """Main converter class orchestrating the conversion process."""

    def __init__(self, project: str = DEFAULT_PROJECT):
        """
        Initialize converter.
        
        Args:
            project: Project directory name under inputs/
        """
        self.project = project
        self.project_dir = INPUT_DIR / project

        self._validate_paths()
        self._load_resources()

    def _validate_paths(self) -> None:
        """Validate that required directories and files exist."""
        if not self.project_dir.exists():
            raise ValueError(f"Project directory not found: {self.project_dir}")

        self.excel_path = self.project_dir / EXCEL_FILE_NAME
        self.schema_path = self.project_dir / SCHEMA_FILE_NAME

        if not self.excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {self.excel_path}")

        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")

    def _load_resources(self) -> None:
        """Load schema and Excel data."""
        print(f"Loading schema from {self.schema_path}...")
        self.schema_loader = SchemaLoader(self.schema_path)

        print(f"Loading Excel from {self.excel_path}...")
        excel_loader = ExcelLoader(self.excel_path)
        self.raw_tables = excel_loader.load_all_tables()
        print(f"Found tables: {list(self.raw_tables.keys())}")

    def process(self) -> tuple[ET.Element, Path]:
        """
        Execute conversion process.
        
        Returns:
            Tuple of (XML root element, output XML file path)
        """
        # Filter and prepare tables
        self.filtered_tables = self._filter_tables()

        # Generate XML
        self.xml_root = self._generate_xml()

        # Save XML
        xml_output_path = self._save_xml()

        return self.xml_root, xml_output_path

    def _filter_tables(self) -> Dict:
        """Filter tables based on COLUMNS_TO_KEEP configuration."""
        excel_loader = ExcelLoader(self.excel_path)
        filtered = excel_loader.filter_tables(
            self.raw_tables,
            COLUMNS_TO_KEEP,
            safe_str
        )

        print(f"\nFiltered tables:")
        for name, df in filtered.items():
            cols = list(df.columns)
            rows = len(df)
            print(f"  {name}: {cols} ({rows} rows)")

        return filtered

    def _generate_xml(self) -> ET.Element:
        """Generate XML from filtered tables."""
        print("\nGenerating XML...")

        generator = XMLGenerator(
            self.schema_loader.entities_meta,
            self.schema_loader.entity_field_meta,
            self.schema_loader.relationships_m2m
        )

        # Build partylist index
        generator.build_partylist_index(self.raw_tables)

        # Generate XML
        root = generator.generate_xml(self.filtered_tables)

        print("✓ XML generated successfully")
        return root

    def _save_xml(self) -> Path:
        """Save XML to file."""
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / DATA_OUTPUT_FILE

        tree = ET.ElementTree(self.xml_root)
        tree.write(str(output_path), encoding='utf-8', xml_declaration=False)

        print(f"✓ XML saved to {output_path}")
        return output_path

    def create_zip(self, xml_path: Path, content_types_path: Optional[Path] = None) -> Path:
        """
        Create ZIP archive containing XML, schema, and content types.
        
        Args:
            xml_path: Path to data.xml
            content_types_path: Deprecated - not used, content types are built-in
            
        Returns:
            Path to created ZIP file
        """
        print("\nCreating ZIP archive...")

        # Validate files exist
        if not xml_path.exists():
            raise FileNotFoundError(f"XML file not found: {xml_path}")

        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        zip_path = OUTPUT_DIR / ZIP_OUTPUT_FILE

        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(xml_path, arcname=DATA_OUTPUT_FILE)
            zf.write(self.schema_path, arcname=SCHEMA_FILE_NAME)
            
            # Add built-in Content_Types.xml
            zf.writestr("[Content_Types].xml", CONTENT_TYPES_XML)

        print(f"✓ ZIP archive created: {zip_path}")
        return zip_path


def main(project: str = DEFAULT_PROJECT, create_zip_file: bool = True) -> None:
    """
    Main execution function.
    
    Args:
        project: Project directory name
        create_zip_file: Whether to create ZIP archive
    """
    try:
        converter = ExcelToXmlConverter(project)
        xml_root, xml_path = converter.process()

        if create_zip_file:
            converter.create_zip(xml_path)

        print("\n✓ Conversion completed successfully!")

    except (FileNotFoundError, ValueError) as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

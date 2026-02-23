"""
Tests for the Excel to XML converter.
Includes unit tests and integration tests with sample data.
"""

import xml.etree.ElementTree as ET
import unittest
from pathlib import Path

from src.utils import safe_str, normalize_datetime_value
from tests.fixtures_config import EXCEL_FILE, SCHEMA_FILE, EXPECTED_OUTPUT


class TestConverterSetup(unittest.TestCase):
    """Test converter setup and configuration."""

    def test_imports(self):
        """Test that all modules can be imported."""
        try:
            from src import ExcelToXmlConverter
            from src.config import BASE_DIR, INPUT_DIR, OUTPUT_DIR
            from src.schema_loader import SchemaLoader
            from src.excel_loader import ExcelLoader
            from src.xml_generator import XMLGenerator
        except ImportError as e:
            self.fail(f"Failed to import module: {e}")

    def test_directories_exist(self):
        """Test that required directories exist."""
        from src.config import BASE_DIR, INPUT_DIR, OUTPUT_DIR

        self.assertTrue(BASE_DIR.exists(), "Base directory should exist")
        self.assertTrue(INPUT_DIR.exists(), "Input directory should exist")
        self.assertTrue(OUTPUT_DIR.exists(), "Output directory should exist")

    def test_fixture_files_exist(self):
        """Test that test fixture files exist."""
        self.assertTrue(SCHEMA_FILE.exists(), f"Schema file not found: {SCHEMA_FILE}")
        self.assertTrue(EXCEL_FILE.exists(), f"Excel file not found: {EXCEL_FILE}")
        self.assertTrue(EXPECTED_OUTPUT.exists(), f"Expected output not found: {EXPECTED_OUTPUT}")


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""

    def test_safe_str_conversions(self):
        """Test safe_str utility function."""
        import math

        # Test None
        self.assertEqual(safe_str(None), "")

        # Test NaN
        self.assertEqual(safe_str(float('nan')), "")

        # Test empty string
        self.assertEqual(safe_str(""), "")

        # Test integer
        self.assertEqual(safe_str(42), "42")

        # Test float to int
        self.assertEqual(safe_str(42.0), "42")

        # Test float with decimals
        result = safe_str(42.5)
        self.assertIn("42", result)

        # Test boolean
        self.assertEqual(safe_str(True), "True")
        self.assertEqual(safe_str(False), "False")

    def test_datetime_normalization(self):
        """Test datetime normalization."""
        # Test full datetime
        result = normalize_datetime_value("25.08.2020 11:30:00")
        self.assertEqual(result, "2020-08-25T11:30:00.0000000Z")

        # Test datetime without seconds
        result = normalize_datetime_value("25.08.2020 11:30")
        self.assertEqual(result, "2020-08-25T11:30:00.0000000Z")

        # Test date only
        result = normalize_datetime_value("15.01.2020")
        self.assertEqual(result, "2020-01-15T00:00:00.0000000Z")

        # Test invalid format (should return original)
        invalid = "2020-08-25"
        result = normalize_datetime_value(invalid)
        self.assertEqual(result, invalid)


class TestConversionIntegration(unittest.TestCase):
    """Integration tests using sample test data."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for the entire test class."""
        from src import ExcelToXmlConverter

        # Create temporary test directory with sample data
        cls.converter = ExcelToXmlConverter(project="test_project")
        cls.xml_root, cls.xml_path = cls.converter.process()

    def test_conversion_completes(self):
        """Test that conversion completes successfully."""
        self.assertIsNotNone(self.xml_root, "XML root should not be None")
        self.assertTrue(self.xml_path.exists(), "Generated XML file should exist")

    def test_xml_structure(self):
        """Test that generated XML has correct structure."""
        self.assertEqual(self.xml_root.tag, "entities", "Root element should be 'entities'")
        
        # Check for required attributes
        self.assertIn("xmlns:xsd", self.xml_root.attrib)
        self.assertIn("xmlns:xsi", self.xml_root.attrib)
        self.assertIn("timestamp", self.xml_root.attrib)

    def test_entity_count(self):
        """Test that all expected entities are present."""
        entities = self.xml_root.findall("entity")
        entity_names = {e.get("name") for e in entities}

        expected_entities = {"contact", "appointment", "ntg_sportcategory"}
        self.assertEqual(entity_names, expected_entities, f"Expected entities {expected_entities}, got {entity_names}")

    def test_contact_records(self):
        """Test that contact records are correctly populated."""
        contact_entity = self.xml_root.find(".//entity[@name='contact']")
        records = contact_entity.findall(".//record")

        self.assertEqual(len(records), 4, "Should have 4 contact records")

        # Check first record
        first_record = records[0]
        fields = {f.get("name"): f.get("value") for f in first_record.findall("field")}

        self.assertEqual(fields.get("firstname"), "Timotej")
        self.assertEqual(fields.get("lastname"), "Palus")
        self.assertEqual(fields.get("emailaddress1"), "timpal@gmail.com")

    def test_appointment_records(self):
        """Test that appointment records with partylist are correctly populated."""
        appointment_entity = self.xml_root.find(".//entity[@name='appointment']")
        records = appointment_entity.findall(".//record")

        self.assertEqual(len(records), 2, "Should have 2 appointment records")

        # Check first appointment has requiredattendees partylist
        first_record = records[0]
        required_attendees = first_record.find(".//field[@name='requiredattendees']")
        self.assertIsNotNone(required_attendees, "requiredattendees field should exist")

        # Check partylist entries
        activity_pointers = required_attendees.findall("activitypointerrecords")
        self.assertEqual(len(activity_pointers), 3, "First appointment should have 3 required attendees")

    def test_m2m_relationships(self):
        """Test that many-to-many relationships are correctly populated."""
        contact_entity = self.xml_root.find(".//entity[@name='contact']")
        m2m = contact_entity.find("m2mrelationships")

        m2m_rels = m2m.findall("m2mrelationship")
        self.assertGreater(len(m2m_rels), 0, "Should have M2M relationships")

        # Check relationship structure
        first_rel = m2m_rels[0]
        self.assertEqual(first_rel.get("targetentityname"), "ntg_sportcategory")
        self.assertEqual(first_rel.get("m2mrelationshipname"), "ntg_contact_ntg_sportcategory")

        # Check targetids
        targetids = first_rel.find("targetids")
        self.assertIsNotNone(targetids)
        targetid_elements = targetids.findall("targetid")
        self.assertEqual(len(targetid_elements), 1)

    def test_entity_references(self):
        """Test that entity reference fields have correct lookup information."""
        contact_entity = self.xml_root.find(".//entity[@name='contact']")
        first_record = contact_entity.find(".//record")

        parent_customer = first_record.find(".//field[@name='parentcustomerid']")
        self.assertIsNotNone(parent_customer, "parentcustomerid field should exist")
        self.assertEqual(parent_customer.get("lookupentity"), "account", "Should reference account entity")
        self.assertEqual(parent_customer.get("lookupentityname"), "default")

    def test_datetime_conversion(self):
        """Test that datetime values are properly normalized."""
        appointment_entity = self.xml_root.find(".//entity[@name='appointment']")
        first_record = appointment_entity.find(".//record")

        scheduled_start = first_record.find(".//field[@name='scheduledstart']")
        # Should be converted from DD.MM.YYYY HH:MM:SS format
        self.assertIn("T", scheduled_start.get("value"), "Should be ISO format with time separator")
        self.assertTrue(scheduled_start.get("value").endswith("Z"), "Should have timezone indicator")

    def test_boolean_conversion(self):
        """Test that boolean values are converted correctly."""
        contact_entity = self.xml_root.find(".//entity[@name='contact']")
        first_record = contact_entity.find(".//record")

        do_not_email = first_record.find(".//field[@name='donotemail']")
        self.assertIn(do_not_email.get("value"), ["True", "False"], "Boolean should be True or False")

    def test_output_consistency(self):
        """Test that output structure matches expected format."""
        # Load expected output
        expected_tree = ET.parse(str(EXPECTED_OUTPUT))
        expected_root = expected_tree.getroot()

        # Compare entity counts
        self.assertEqual(
            len(self.xml_root.findall("entity")),
            len(expected_root.findall("entity")),
            "Should have same number of entities as expected"
        )

        # Compare entity names
        self.assertEqual(
            {e.get("name") for e in self.xml_root.findall("entity")},
            {e.get("name") for e in expected_root.findall("entity")},
            "Should have same entity names as expected"
        )

        # Compare record counts per entity
        for entity_name in ["contact", "appointment", "ntg_sportcategory"]:
            actual_count = len(self.xml_root.findall(f".//entity[@name='{entity_name}']//record"))
            expected_count = len(expected_root.findall(f".//entity[@name='{entity_name}']//record"))
            self.assertEqual(
                actual_count,
                expected_count,
                f"Entity '{entity_name}' should have {expected_count} records, got {actual_count}"
            )


if __name__ == "__main__":
    unittest.main()

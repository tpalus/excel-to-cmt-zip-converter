"""
Schema loading and metadata extraction.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any


class SchemaLoader:
    """Loads and parses XML schema for entity definitions."""

    def __init__(self, schema_path: Path):
        """
        Initialize schema loader.
        
        Args:
            schema_path: Path to schema.xml file
        """
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        self.schema_tree = ET.parse(str(schema_path))
        self.schema_root = self.schema_tree.getroot()
        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load and organize schema metadata."""
        self.entities_meta = {}
        self.entity_field_meta = {}
        self.relationships_m2m = {}

        # Load entity metadata
        for entity in self.schema_root.findall('entity'):
            name = entity.get('name')
            self.entities_meta[name] = {
                'displayname': entity.get('displayname'),
                'primaryidfield': entity.get('primaryidfield')
            }

        # Load field metadata
        for entity in self.schema_root.findall('entity'):
            entity_name = entity.get('name')
            self.entity_field_meta[entity_name] = {}

            fields = entity.find('fields')
            if fields is None:
                continue

            for field in fields.findall('field'):
                field_name = field.get('name')
                meta = {'type': field.get('type')}

                if field.get('lookupType'):
                    meta['lookupType'] = field.get('lookupType')

                meta['displayname'] = field.get('displayname')
                self.entity_field_meta[entity_name][field_name] = meta

        # Load many-to-many relationships
        for entity in self.schema_root.findall('entity'):
            src = entity.get('name')
            pk = entity.get('primaryidfield')

            for rel in entity.findall('relationships/relationship'):
                if rel.get('manyToMany') == 'true':
                    rel_name = rel.get('relatedEntityName')
                    self.relationships_m2m[rel_name] = {
                        'sourceEntity': src,
                        'sourceKey': pk,
                        'targetEntity': rel.get('m2mTargetEntity'),
                        'targetKey': rel.get('m2mTargetEntityPrimaryKey')
                    }

    def get_entity_meta(self, entity_name: str) -> Dict[str, Any]:
        """Get metadata for an entity."""
        return self.entities_meta.get(entity_name, {})

    def get_field_meta(self, entity_name: str, field_name: str) -> Dict[str, Any]:
        """Get metadata for a field within an entity."""
        return self.entity_field_meta.get(entity_name, {}).get(field_name, {})

    def get_m2m_relationships(self) -> Dict[str, Dict[str, str]]:
        """Get all many-to-many relationships."""
        return self.relationships_m2m

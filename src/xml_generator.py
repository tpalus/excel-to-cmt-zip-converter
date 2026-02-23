"""
XML generation and data transformation.
"""

import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any

import pandas as pd

from .utils import add_field, normalize_datetime_value


class XMLGenerator:
    """Generates XML output from processed data."""

    def __init__(self, entities_meta: Dict, entity_field_meta: Dict, relationships_m2m: Dict):
        """
        Initialize XML generator.
        
        Args:
            entities_meta: Entity metadata from schema
            entity_field_meta: Field metadata from schema
            relationships_m2m: Many-to-many relationships from schema
        """
        self.entities_meta = entities_meta
        self.entity_field_meta = entity_field_meta
        self.relationships_m2m = relationships_m2m
        self.partylist_index = {}

    def build_partylist_index(self, tables: Dict[str, pd.DataFrame]) -> None:
        """
        Build index of partylist relationships.
        
        Args:
            tables: Dictionary of DataFrames including partylist tables
        """
        self.partylist_index = {}

        for table_name, df in tables.items():
            if not table_name.startswith("partylist_"):
                continue

            # partylist_appointment -> appointment
            entity_name = table_name[len("partylist_"):]

            if entity_name not in self.entities_meta:
                continue

            required_cols = {
                "partyid_entityreference",
                "entityField",
                "activitypointerrecordid",
                "activityid",
                "partyid"
            }

            missing = required_cols - set(df.columns)
            if missing:
                print(f"Warning: partylist table '{table_name}' missing columns: {missing}")
                continue

            ent_idx = self.partylist_index.setdefault(entity_name, {})

            for _, row in df.iterrows():
                act_id = row["activityid"]
                field_name = row["entityField"]

                if pd.isna(act_id) or pd.isna(field_name):
                    continue

                act_id_str = str(act_id)
                field_str = str(field_name)

                ent_idx.setdefault(act_id_str, {}).setdefault(field_str, []).append(row)

    def render_partylists_for_record(
        self,
        rec_el: ET.Element,
        entity_name: str,
        rec_id_str: str
    ) -> None:
        """
        Render partylist fields for a record.
        
        Args:
            rec_el: Record XML element
            entity_name: Name of the entity
            rec_id_str: Record ID as string
        """
        ent_pl = self.partylist_index.get(entity_name, {})
        per_record = ent_pl.get(rec_id_str, {})

        for field_name, rows in per_record.items():
            field_el = ET.SubElement(rec_el, "field", {
                "name": field_name,
                "value": "",
                "lookupentity": "",
                "lookupentityname": ""
            })

            for row in rows:
                ap_id = row.get("activitypointerrecordid") or row.get("activitypartyid")

                if pd.isna(ap_id) if isinstance(ap_id, float) else ap_id is None:
                    ap_id = str(uuid.uuid4())
                else:
                    ap_id = str(ap_id)

                apr_el = ET.SubElement(field_el, "activitypointerrecords", {"id": ap_id})

                partyid = row.get("partyid")
                party_lookup = None

                if "partyid_entityreference" in row.index and pd.notna(row["partyid_entityreference"]):
                    party_lookup = str(row["partyid_entityreference"]).split("|")[0]

                add_field(
                    apr_el,
                    "partyid",
                    partyid,
                    lookupentity=party_lookup,
                    lookupentityname="default" if party_lookup else None
                )

                add_field(
                    apr_el,
                    "activityid",
                    rec_id_str,
                    lookupentity="activitypointer",
                    lookupentityname="default"
                )

                add_field(apr_el, "activitypartyid", ap_id)

    def process_entity(
        self,
        root: ET.Element,
        entity_name: str,
        df: pd.DataFrame
    ) -> None:
        """
        Process entity and add to XML root.
        
        Args:
            root: Root XML element
            entity_name: Name of the entity
            df: DataFrame with entity data
        """
        meta = self.entities_meta[entity_name]

        ent_el = ET.SubElement(root, "entity", {
            "name": entity_name,
            "displayname": meta["displayname"]
        })

        recs = ET.SubElement(ent_el, "records")
        pk = meta["primaryidfield"]

        for _, row in df.iterrows():
            rec_id = row[pk]
            rec_id_str = str(rec_id)

            rec = ET.SubElement(recs, "record", {"id": rec_id_str})

            # Build lookup overrides from *_entityreference columns
            lookup_override = {}
            for col in df.columns:
                if col.lower().endswith("_entityreference") and pd.notna(row[col]):
                    base = col[:-len("_entityreference")].rstrip("_")
                    lookup_override[base] = str(row[col]).split("|")[0]

            # Process all fields
            for col, val in row.items():
                col_lower = col.lower()

                # Skip helper columns and NaN values
                if col_lower.endswith('_entityreference') or pd.isna(val):
                    continue

                field_meta = self.entity_field_meta.get(entity_name, {}).get(col, {})
                field_type = field_meta.get('type')

                # Normalize datetime values
                if isinstance(val, str):
                    val = normalize_datetime_value(val)

                lookupentity = None
                lookupentityname = None

                # Handle entityreference and owner fields
                if field_type in ('entityreference', 'owner'):
                    if col in lookup_override:
                        lookupentity = lookup_override[col]
                    else:
                        lookup_type = field_meta.get('lookupType')
                        if lookup_type:
                            lookupentity = str(lookup_type).split('|')[0]
                        elif field_type == 'owner':
                            lookupentity = 'systemuser'

                    lookupentityname = 'default'

                add_field(
                    rec,
                    col,
                    val,
                    lookupentity=lookupentity,
                    lookupentityname=lookupentityname
                )

            # Add partylist fields after regular fields
            if entity_name in self.partylist_index:
                self.render_partylists_for_record(rec, entity_name, rec_id_str)

        ET.SubElement(ent_el, "m2mrelationships")

    def process_m2m(
        self,
        root: ET.Element,
        rel_name: str,
        df: pd.DataFrame,
        meta: Dict[str, str]
    ) -> None:
        """
        Process many-to-many relationships.
        
        Args:
            root: Root XML element
            rel_name: Relationship name
            df: DataFrame with relationship data
            meta: Relationship metadata
        """
        ent = root.find(f".//entity[@name='{meta['sourceEntity']}']")
        if ent is None:
            print(f"Warning: Entity '{meta['sourceEntity']}' not found for M2M '{rel_name}'")
            return

        m2ms = ent.find("m2mrelationships")
        if m2ms is None:
            m2ms = ET.SubElement(ent, "m2mrelationships")

        for _, row in df.iterrows():
            src = row[meta["sourceKey"]]
            tgt = row[meta["targetKey"]]

            if pd.isna(src) or pd.isna(tgt):
                continue

            attribs = {
                "sourceid": str(src),
                "targetentityname": meta["targetEntity"],
                "targetentitynameidfield": meta["targetKey"],
                "m2mrelationshipname": rel_name
            }

            rel_el = ET.SubElement(m2ms, "m2mrelationship", attribs)
            tgtids = ET.SubElement(rel_el, "targetids")
            ET.SubElement(tgtids, "targetid").text = str(tgt)

    def generate_xml(
        self,
        tables: Dict[str, pd.DataFrame]
    ) -> ET.Element:
        """
        Generate XML from processed tables.
        
        Args:
            tables: Dictionary of DataFrames
            
        Returns:
            Root XML element
        """
        root = ET.Element("entities", {
            "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

        # Filter out partylist tables
        tables_for_processing = {
            k: v for k, v in tables.items()
            if not k.startswith("partylist_")
        }

        # Sort: regular entities first, then M2M
        ordered_items = sorted(
            tables_for_processing.items(),
            key=lambda kv: (
                (kv[0].startswith("m2m_") or kv[0] in self.relationships_m2m),
                kv[0].lower()
            )
        )

        for name, df in ordered_items:
            if name in self.entities_meta:
                self.process_entity(root, name, df)
            elif name in self.relationships_m2m:
                self.process_m2m(root, name, df, self.relationships_m2m[name])
            elif name.startswith("m2m_"):
                rel = name[len("m2m_"):]
                if rel in self.relationships_m2m:
                    self.process_m2m(root, rel, df, self.relationships_m2m[rel])
                else:
                    print(f"Warning: No M2M metadata for {name}")
            else:
                print(f"Warning: Unrecognized table: {name}")

        return root

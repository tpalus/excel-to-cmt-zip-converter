"""
Utility functions for Excel to XML conversion.
"""

import math
import xml.etree.ElementTree as ET
from datetime import datetime, date, time
from typing import Any, Optional

import numpy as np
import pandas as pd


def safe_str(value: Any) -> str:
    """
    Convert value to string without '.0' suffix and without 'nan'.
    
    Args:
        value: Value to convert
        
    Returns:
        String representation of the value
    """
    if value is None or (isinstance(value, float) and math.isnan(value)) or \
       (isinstance(value, str) and value.strip() == ""):
        return ""

    if pd.isna(value):
        return ""

    # bool
    if isinstance(value, (bool, np.bool_)):
        return "True" if value else "False"

    # int
    if isinstance(value, (int, np.integer)):
        return str(int(value))

    # float -> if whole number, remove .0
    if isinstance(value, (float, np.floating)):
        if math.isfinite(value) and float(value).is_integer():
            return str(int(value))
        return format(value, "g")

    # dates/times
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()

    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime(value.year, value.month, value.day).isoformat()

    if isinstance(value, time):
        return value.isoformat()

    # everything else
    return str(value)


def normalize_datetime_value(value: str) -> str:
    """
    Convert datetime string to ISO format with timezone.
    
    Converts:
      - '25.08.2020 11:30:00' -> '2020-08-25T11:30:00.0000000Z'
      - '15.01.2020'          -> '2020-01-15T00:00:00.0000000Z'
    
    If format doesn't match, returns original value.
    
    Args:
        value: Datetime string to convert
        
    Returns:
        ISO formatted datetime string
    """
    if not isinstance(value, str):
        return value

    candidates = [
        ("%d.%m.%Y %H:%M:%S", False),
        ("%d.%m.%Y %H:%M", False),
        ("%d.%m.%Y", True),   # date only, will add 00:00:00
    ]

    for fmt, date_only in candidates:
        try:
            dt = datetime.strptime(value, fmt)
            if date_only:
                dt = dt.replace(hour=0, minute=0, second=0)
            return dt.strftime("%Y-%m-%dT%H:%M:%S.0000000Z")
        except ValueError:
            continue

    return value


def add_field(
    elem: ET.Element,
    name: str,
    value: Any,
    lookupentity: Optional[str] = None,
    lookupentityname: Optional[str] = None
) -> None:
    """
    Add a field element to an XML element.
    
    Args:
        elem: Parent XML element
        name: Field name
        value: Field value
        lookupentity: Optional lookup entity type
        lookupentityname: Optional lookup entity name
    """
    if isinstance(value, float) and value.is_integer():
        value = int(value)

    attrs = {
        "name": name,
        "value": "" if value is None else str(value)
    }
    if lookupentity:
        attrs["lookupentity"] = lookupentity
    if lookupentityname:
        attrs["lookupentityname"] = lookupentityname

    ET.SubElement(elem, "field", attrs)

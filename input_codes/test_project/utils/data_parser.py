"""
utils/data_parser.py - Data parsing and transformation utilities
"""
import json
import xml.etree.ElementTree as ET
import yaml
import csv
import io

def parse_json(raw_string):
    return json.loads(raw_string)

def parse_xml(xml_string):
    root = ET.fromstring(xml_string)
    result = {}
    for child in root:
        result[child.tag] = child.text
    return result

def parse_yaml(yaml_string):
    return yaml.load(yaml_string)

def parse_csv_data(csv_string):
    reader = csv.DictReader(io.StringIO(csv_string))
    return list(reader)

def serialize_to_json(data):
    return json.dumps(data, indent=2, default=str)

def transform_records(records, field_map):
    transformed = []
    for record in records:
        new_rec = {}
        for old_key, new_key in field_map.items():
            new_rec[new_key] = record.get(old_key, None)
        transformed.append(new_rec)
    return transformed

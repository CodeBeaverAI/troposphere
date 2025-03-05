import json
import pytest
from troposphere import Template

def test_empty_template():
    """Test that an empty template contains empty mappings and default resources."""
    template = Template()
    data = json.loads(template.to_json())
    assert data.get("Mappings", {}) == {}
    assert data["Resources"] == {}

def test_single_mapping():
    """Test that a single mapping is correctly added."""
    template = Template()
    template.add_mapping("map", {"n": "v"})
    data = json.loads(template.to_json())
    expected = {"Mappings": {"map": {"n": "v"}}, "Resources": {}}
    assert data == expected

def test_multiple_mappings():
    """Test that adding multiple mappings with the same mapping name merges keys."""
    template = Template()
    template.add_mapping("map", {"k1": {"n1": "v1"}})
    template.add_mapping("map", {"k2": {"n2": "v2"}})
    data = json.loads(template.to_json())
    expected = {"Mappings": {"map": {"k1": {"n1": "v1"}, "k2": {"n2": "v2"}}}, "Resources": {}}
    assert data == expected

def test_overwrite_key_in_mapping():
    """Test that updating an existing key in the mapping overwrites the previous value."""
    template = Template()
    template.add_mapping("map", {"k1": {"n1": "v1"}})
    # Overwrite the same key with new value.
    template.add_mapping("map", {"k1": {"n1": "v1_new"}})
    data = json.loads(template.to_json())
    expected = {"Mappings": {"map": {"k1": {"n1": "v1_new"}}}, "Resources": {}}
    assert data == expected

def test_different_mappings():
    """Test that adding different mapping names results in separate mapping entries."""
    template = Template()
    template.add_mapping("map1", {"n": "v"})
    template.add_mapping("map2", {"k": {"n": "v2"}})
    data = json.loads(template.to_json())
    expected = {"Mappings": {"map1": {"n": "v"}, "map2": {"k": {"n": "v2"}}}, "Resources": {}}
    assert data == expected
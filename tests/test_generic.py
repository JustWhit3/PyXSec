import xml.etree.ElementTree as ET
from utils import try_parse_str, try_parse_float, try_parse_int


def test_try_parse_str():
    """
    Test the try_parse_str function for parsing XML elements with a default value.
    """

    # Test when parsing succeeds
    xml_string = '<root><key elem="value"/></root>'
    root = ET.fromstring(xml_string)
    result = try_parse_str("default", root, "key", "elem")
    assert result == "value"

    # Test when parsing fails, return default value
    xml_string = "<root><key/></root>"
    root = ET.fromstring(xml_string)
    result = try_parse_str("default", root, "key", "elem")
    assert result == "default"


def test_try_parse_int():
    """
    Test the try_parse_int function for parsing XML elements with a default value.
    """

    # Test when parsing succeeds
    xml_string = '<root><key elem="42"/></root>'
    root = ET.fromstring(xml_string)
    result = try_parse_int(0, root, "key", "elem")
    assert result == 42

    # Test when parsing fails, return default value
    xml_string = "<root><key/></root>"
    root = ET.fromstring(xml_string)
    result = try_parse_int(0, root, "key", "elem")
    assert result == 0


def test_try_parse_float():
    """
    Test the try_parse_float function for parsing XML elements with a default value.
    """

    # Test when parsing succeeds
    xml_string = '<root><key elem="3.14"/></root>'
    root = ET.fromstring(xml_string)
    result = try_parse_float(0.0, root, "key", "elem")
    assert result == 3.14

    # Test when parsing fails, return default value
    xml_string = "<root><key/></root>"
    root = ET.fromstring(xml_string)
    result = try_parse_float(0.0, root, "key", "elem")
    assert result == 0.0

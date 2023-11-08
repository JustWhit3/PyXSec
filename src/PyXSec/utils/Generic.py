# ---------------------- Metadata ----------------------
#
# File name:  Generic.py
# Author:     Gianluca Bianco (biancogianluca9@gmail.com)
# Date:       2023-11-08
# Copyright:  (c) 2023 Gianluca Bianco under the MIT license.


def try_parse_str(var, root, key, elem):
    """
    Tries to parse an attribute from an XML element as a string.

    Parameters:
        var (str): Default value to return if parsing fails.
        root (ElementTree.Element): The root of the XML element tree.
        key (str): The key to search for in the XML element.
        elem (str): The attribute to parse.

    Returns:
        str: The parsed string or the default value if parsing fails.
    """
    try:
        return root.find(key).attrib[elem]
    except:
        return var


def try_parse_int(var, root, key, elem):
    """
    Tries to parse an attribute from an XML element as an integer.

    Parameters:
        var (int): Default value to return if parsing fails.
        root (ElementTree.Element): The root of the XML element tree.
        key (str): The key to search for in the XML element.
        elem (str): The attribute to parse.

    Returns:
        int: The parsed integer or the default value if parsing fails.
    """
    try:
        return int(root.find(key).attrib[elem])
    except:
        return var


def try_parse_float(var, root, key, elem):
    """
    Tries to parse an attribute from an XML element as a float.

    Parameters:
        var (float): Default value to return if parsing fails.
        root (ElementTree.Element): The root of the XML element tree.
        key (str): The key to search for in the XML element.
        elem (str): The attribute to parse.

    Returns:
        float: The parsed float or the default value if parsing fails.
    """
    try:
        return float(root.find(key).attrib[elem])
    except:
        return var

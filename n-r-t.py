#!/usr/bin/env python3

from lxml import etree
import glob
import re
import os
from copy import deepcopy

mccmnc_re = re.compile(".*\/carrier_config_(\d{3})(\d{2,3})\.xml")

parser = etree.XMLParser(remove_blank_text=True)
config_xml_template = etree.parse("template.xml", parser)

for f in glob.glob("android_packages_apps_CarrierConfig/assets/carrier_config_*.xml"):
    # Extract MMC and MNC from filename
    re_match = mccmnc_re.match(f)
    mcc = re_match.group(1)
    mnc = re_match.group(2)

    # Parse Android-9 XML
    print("Parsing " + f)
    tree = etree.parse(f)
    root = tree.getroot()
    assert(root.tag == "carrier_config_list")
    operators = root.xpath(
        "//carrier_config/string-array[@name='non_roaming_operator_string_array']")
    if len(operators) == 0:
        # Don't handle other configs for now
        continue
    assert(len(operators) == 1)
    # xpath returns an array, so unpack that
    operators = operators[0]
    operator_values = []
    for operator in operators:
        operator_values.append(operator.attrib["value"])

    # Generate Android-4.4 XML
    config_xml = deepcopy(config_xml_template)
    operators_new = config_xml.xpath(
        "//resources/string-array[@name='config_operatorConsideredNonRoaming']")
    assert(len(operators_new) == 1)
    operators_new = operators_new[0]
    for value in operator_values:
        item = etree.Element("item")
        item.text = value
        operators_new.append(item)
    # Write new XML to disk
    folder = "android_frameworks_base/core/res/res/"
    dirname = "values-mcc" + mcc + "-mnc" + mnc
    os.makedirs(folder + dirname, exist_ok=True)
    with open(folder + dirname + "/config.xml", "wb") as newf:
        newf.write(etree.tostring(config_xml, encoding='utf-8',
                                  pretty_print=True, xml_declaration=True))

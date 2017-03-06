""" Generator of visual studio 2015 makefile projects """

import sys
import os
import argparse
import re
import fnmatch
import xml.etree.cElementTree as xml_tree
from CVsProject import CVsProject
from CVsProject import CVsProjectConfiguration

# TODO: Load configurations from file
# TODO: Solution generator

def write_xml(xml, filename):
    """Write xml to file

    Parameters:
      - xml: xml root
      - filename: filename of output file
    """

    def indent(elem, level=0):
        """make xml look pretty"""

        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    indent(xml)
    tree = xml_tree.ElementTree(xml)
    tree.write(filename, xml_declaration=True, encoding='utf-8', method="xml")

def main(argv):
    # Parse command line
    parser = argparse.ArgumentParser(description="VS project generator")
    parser.add_argument("--srcdir",
        default=".",
        help="Makefile project root dir")
    args = parser.parse_args()

    # Configuration
    config = {
        "name": "test",
        "exclude_files": ("*.sln", "*.vcxproj", "*.vcxproj.filters"),
        "exclude_dirs": (".vs", ".git", "msvc"),
        "configures": (
            CVsProjectConfiguration(
                name="all",
                platform="x86",
                build="make",
                clean="make clean",
                defines=["VS_PROJECT=1"]
            ),
        ),
    }

    # Create project
    test_proj = CVsProject(name=config["name"],
        guid="{8059B6CC-7DB0-4243-8ACF-5271D6F2E1E0}")
    # Add project configurations
    for i in config["configures"]:
        test_proj.add_config(i)
    # Add files to project
    excludes_regex = r'|'.join([fnmatch.translate(x) for x in config["exclude_files"]])
    for root, dirs, files in os.walk(args.srcdir, topdown=True):
        dirs[:] = [d for d in dirs if d not in config["exclude_dirs"]]
        files = [f for f in files if not re.match(excludes_regex, f)]

        for fname in files:
            test_proj.add_file(os.path.join(root, fname))

    write_xml(test_proj._xml, config["name"] + ".vcxproj")

if __name__ == "__main__":
    main(sys.argv)

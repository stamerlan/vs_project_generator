""" Generator of visual studio 2015 makefile projects """

import sys
import os
import argparse
import re
import fnmatch
import xml.etree.cElementTree as xml_tree
from CVsProject import CVsProject
from CVsProject import CVsProjectConfiguration
from CVsProjectFilters import CVsProjectFilters

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
    test_proj_filters = CVsProjectFilters(args.srcdir)
    # Add srcdir to each configuration includes and forced_inc
    for conf in config["configures"]:
        conf.includes = [os.path.join(args.srcdir, i) for i in conf.includes]
        conf.forced_inc = [os.path.join(args.srcdir, i) for i in conf.forced_inc]
    # Add project configurations
    for i in config["configures"]:
        test_proj.add_config(i)
    # Add files to project
    exclude_files_regex = r'|'.join(
        [fnmatch.translate(file_regex) for file_regex in config["exclude_files"]])
    exclude_dirs_regex = r'|'.join(
        [fnmatch.translate(os.path.join(args.srcdir, dir_regex)) for dir_regex in config["exclude_dirs"]])
    for root, dirs, files in os.walk(args.srcdir, topdown=True):
        if re.match(exclude_dirs_regex, root):
            continue
        files = [f for f in files if not re.match(exclude_files_regex, f)]

        for fname in files:
            fpath = os.path.join(root, fname)
            test_proj.add_file(fpath)
            test_proj_filters.add_file(fpath)

    write_xml(test_proj._xml, config["name"] + ".vcxproj")
    write_xml(test_proj_filters._xml, config["name"] + ".vcxproj.filters")

if __name__ == "__main__":
    main(sys.argv)

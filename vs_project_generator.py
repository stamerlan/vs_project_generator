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
from CVsSolution import CVsSolution

# TODO: Add readme
# TODO: Add config file description and example

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

def load_list(xml, path):
    """Load list from xml

    Parameters:
      - xml: xml root
      - path: path to element containig list
    Return:
      list of elements or empty list is element not found
    """

    node = xml.find(path)
    out_list = []
    if node is not None:
        for i in node:
            out_list.append(i.text)
    return out_list


def main(argv):
    # Parse command line
    parser = argparse.ArgumentParser(description="VS project generator")
    parser.add_argument("--srcdir",
        default=".",
        help="Makefile project root dir")
    parser.add_argument("--config",
        default="config.xml",
        help="Configuration file for generator")
    args = parser.parse_args()

    # Load configuration
    config = xml_tree.parse(args.config).getroot()

    # Create project
    project_name = config.attrib["name"]
    print "Create project:", project_name
    guid = config.findtext("GUID")
    proj = CVsProject(name=project_name, guid=guid)
    proj_filters = CVsProjectFilters(args.srcdir)
    sln = CVsSolution(name=project_name)
    sln.add_project(proj)

    # Load ProjectConfig/exclude_files
    exclude_files = load_list(config, "ExcludeFiles")
    # Load ProjectConfig/exclude_dirs
    exclude_dirs = load_list(config, "ExcludeDirs")

    # Load ProjectConfig/Configures common settings
    common_platform = config.findtext("Configures/Platform")
    common_build = config.findtext("Configures/Build")
    common_clean = config.findtext("Configures/Clean")
    common_def = load_list(config, "Configures/Defines")
    common_inc = load_list(config, "Configures/Includes")
    common_inc = [os.path.join(args.srcdir, i) for i in common_inc]
    common_forced_inc = load_list(config, "Configures/ForcedIncludes")
    common_forced_inc = [os.path.join(args.srcdir, i) for i in common_forced_inc]

    # Create project configurations
    for conf in config.findall("Configures/Config"):
        print "  Configuration:", conf.attrib["name"]

        platform = conf.findtext("Platform", common_platform)
        build = conf.findtext("Build", common_build)
        clean = conf.findtext("Clean", common_clean)
        defines = common_def + load_list(conf, "Defines")
        includes = common_inc + \
            [os.path.join(args.srcdir, i) for i in load_list(conf, "Includes")]
        forced_inc = common_forced_inc + \
            [os.path.join(args.srcdir, i) for i in load_list(conf, "ForcedIncludes")]

        cfg_obj = CVsProjectConfiguration(
            name=conf.attrib["name"],
            platform=platform,
            build=build,
            clean=clean,
            defines=defines,
            includes=includes,
            forced_inc=forced_inc)

        proj.add_config(cfg_obj)
        sln.add_config(proj, cfg_obj)

    # Add files to project
    exclude_files_regex = r'|'.join(
        [fnmatch.translate(file_regex) for file_regex in exclude_files])
    exclude_dirs = tuple([os.path.join(args.srcdir, dir) + os.path.sep
                          for dir in exclude_dirs])
    for root, dirs, files in os.walk(args.srcdir, topdown=True):
        if (root + os.path.sep).startswith(exclude_dirs):
            continue
        if exclude_files: # if there are any files to exclude
            files = [f for f in files if not re.match(exclude_files_regex, f)]

        for fname in files:
            fpath = os.path.join(root, fname)
            proj.add_file(fpath)
            proj_filters.add_file(fpath)

    # Write output
    write_xml(proj._xml, project_name + ".vcxproj")
    write_xml(proj_filters._xml, project_name + ".vcxproj.filters")
    with open(project_name + ".sln", "wb") as f:
        f.write(sln.gen_solution())

if __name__ == "__main__":
    main(sys.argv)

import os
import uuid
import xml.etree.cElementTree as xml_tree

class CVsProjectFilters:
    """Description of visual studio project filter"""

    def __init__(self, src_root):
        """Constructor

        Parameters:
          - src_root: relative path to sources dir - will be stripped from
              filter file path (to avoid all files in directory ..\src\ for ex)
        """

        self._src_root = src_root
        self._xml = xml_tree.Element('Project',
            {"ToolsVersion": "4.0",
             "xmlns": "http://schemas.microsoft.com/developer/msbuild/2003"
            })
        self._filters = xml_tree.SubElement(self._xml, "ItemGroup")
        self._files = xml_tree.SubElement(self._xml, "ItemGroup")

    def _add_filter(self, filterpath):
        """Add filter if it isn't exists

        Parameters:
          - filterpath: filter path to be created
        """

        node = self._filters.find('.//Filter[@Include="' + filterpath + '"]')
        if not node:
            node = xml_tree.SubElement(self._filters, "Filter",
                {"Include": filterpath})
            xml_tree.SubElement(node, "UniqueIdentifier").text = \
                "{" + str(uuid.uuid4()) + "}"


    def add_file(self, file_path):
        # strip src_root from file_path
        # TODO: need something more intelligent
        filter_path = file_path[len(self._src_root) + 1:]

        components = filter_path.split(os.sep)
        for i in range(1, len(components)): # the last one is file name
            self._add_filter('\\'.join(components[:i]))

            if file_path.endswith(".txt"):
                ftype = "Text"
            elif file_path.endswith(".h") or file_path.endswith(".hpp"):
                ftype = "ClInclude"
            elif file_path.endswith(".c") or file_path.endswith(".cpp"):
                ftype = "ClCompile"
            else:
                ftype = "None"

            node = xml_tree.SubElement(self._files, ftype,
                {"Include": file_path})
            xml_tree.SubElement(node, "Filter").text = \
                '\\'.join(components[:-1])


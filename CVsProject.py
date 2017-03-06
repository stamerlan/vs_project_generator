import uuid
import xml.etree.cElementTree as xml_tree

class CVsProjectConfiguration:
    """Project configuration struct

    Properties:
      - name: Configuration name
      - platform: One of VS platforms (usually x86)
      - build: build command line
      - clean: clean command line
      - defines: (list of strings, optional) preprocessor definitions
      - includes: (list of strings, optional) include directories (relative to
            project dir)
      - forced_inc: (list of strings, optional) forced includes files
    """

    def __init__(self, **kwargs):
        self.name = kwargs["name"]
        self.platform = kwargs["platform"]
        self.build = kwargs["build"]
        self.clean = kwargs["clean"]
        try:
            self.defines = kwargs["defines"]
        except KeyError:
            self.defines = []
        try:
            self.includes = kwargs["includes"]
        except KeyError:
            self.includes = []
        try:
            self.forced_inc = kwargs["forced_inc"]
        except KeyError:
            self.forced_inc = []

class CVsProject:
    """Description of visual studio project"""

    def __init__(self, **kwargs):
        """Constructor of project

        Parameters:
          - name: (string) project name
          - guid: (string, optional) project GUID string. If it is not set GUID
            will be created automatically
        """

        self._name = kwargs["name"]
        try:
            self._guid = kwargs["guid"]
        except KeyError:
            self._guid = "{" + str(uuid.uuid4()).upper() + "}"

        self._xml = xml_tree.Element('Project',
            {"DefaultTargets": "Build",
             "ToolsVersion": "14.0",
             "xmlns": "http://schemas.microsoft.com/developer/msbuild/2003"
            })

        self._project_configs = xml_tree.SubElement(self._xml, "ItemGroup",
            {"Label": "ProjectConfigurations"})

        node = xml_tree.SubElement(self._xml, "PropertyGroup",
            {"Label": "Globals"})
        xml_tree.SubElement(node, "ProjectGuid").text = self._guid
        xml_tree.SubElement(node, "Keyword").text = "MakeFileProj"

        xml_tree.SubElement(self._xml, "Import", 
            {"Project": "$(VCTargetsPath)\Microsoft.Cpp.Default.props"})
        xml_tree.SubElement(self._xml, "Import",
            {"Project": "$(VCTargetsPath)\Microsoft.Cpp.props"})
        self._itemgroup = xml_tree.SubElement(self._xml, "ItemGroup")
        xml_tree.SubElement(self._xml, "Import",
            {"Project": "$(VCTargetsPath)\Microsoft.Cpp.targets"})
        xml_tree.SubElement(self._xml, "ImportGroup",
            {"Label": "ExtensionTargets"})

    def add_config(self, config):
        """Add project configuration

        Parameters:
          - config: Object of type CVsProjectConfiguration
        """
        platform = config.platform
        if (platform == "x86"):
            platform = "Win32"
        config_plat = config.name + "|" + platform

        node = xml_tree.SubElement(self._project_configs,
            "ProjectConfiguration", {"Include" : config_plat})
        xml_tree.SubElement(node, "Configuration").text = config.name
        xml_tree.SubElement(node, "Platform").text = platform

        condition = "'$(Configuration)|$(Platform)'=='" + \
                config_plat + "'"

        node = xml_tree.Element("PropertyGroup",
            {"Condition": condition, "Label": "Configuration"})
        xml_tree.SubElement(node, "ConfigurationType").text = "Makefile"
        xml_tree.SubElement(node, "UseDebugLibraries").text = "false"
        xml_tree.SubElement(node, "PlatformToolset").text = "v140"

        self._xml.insert(2, node)

        node = xml_tree.SubElement(self._xml, "PropertyGroup",
            {"Condition": condition})
        xml_tree.SubElement(node, "NMakeBuildCommandLine").text = config.build
        xml_tree.SubElement(node, "NMakeCleanCommandLine").text = config.clean
        if config.defines:
            s = ";".join(config.defines) + ";$(NMakePreprocessorDefinitions)"
            xml_tree.SubElement(node, "NMakePreprocessorDefinitions").text = s
        if config.includes:
            s = ";".join(config.includes) + ";$(NMakeIncludeSearchPath)"
            xml_tree.SubElement(node, "NMakeIncludeSearchPath").text = s
        if config.forced_inc:
            s = ";".join(config.forced_inc) + ";$(NMakeForcedIncludes)"
            xml_tree.SubElement(node, "NMakeForcedIncludes").text = s

    def add_file(self, fpath):
        """Add file to project

        Parameters:
          - fpath: path to file relative to project dir
        """
        if fpath.endswith(".txt"):
            ftype = "Text"
        elif fpath.endswith(".h") or fpath.endswith(".hpp"):
            ftype = "ClInclude"
        elif fpath.endswith(".c") or fpath.endswith(".cpp"):
            ftype = "ClCompile"
        else:
            ftype = "None"

        xml_tree.SubElement(self._itemgroup, ftype, {"Include": fpath})


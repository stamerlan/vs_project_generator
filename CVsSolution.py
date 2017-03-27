import uuid
from CVsProject import CVsProjectConfiguration

class CVsSolution:
    """Description of visual studio solution"""

    def __init__(self, **kwargs):
        """Constructor of project

        Parameters:
          - name: (string) solution name
          - guid: (string, optional) solution GUID string. If it is not set
            GUID will be created automatically
        """

        self._name = kwargs["name"]
        try:
            self._guid = kwargs["guid"]
        except KeyError:
            self._guid = None
        if self._guid is None:
            self._guid = "{" + str(uuid.uuid4()).upper() + "}"

        self._projects = {}
        self._configurations = {}

    def add_project(self, proj, filename=None):
        """Add project to solution

        Parameters:
          - proj: (CVsProject) project to be added
          - filename: project file name if not set - project name + ".vcxproj"
            is used
        """

        fname = filename
        if not fname:
            fname = proj.get_name() + ".vcxproj"
        self._projects[fname] = proj

    def add_config(self, proj, conf):
        """Add configuration to solution

        Parameters:
          - proj: (CVsProject) project
          - conf: (CVsProjectConfiguration) configuration to be added
        """

        self._configurations[conf] = proj

    def gen_solution(self):
        """Generate solution file

        Return:
          String to be written to solution file
        """

        sln = "Microsoft Visual Studio Solution File, Format Version 12.00\r\n"
        sln += "# Visual Studio 14\r\n"
        sln += "VisualStudioVersion = 14.0.25420.1\r\n"
        sln += "MinimumVisualStudioVersion = 10.0.40219.1\r\n"
        for fname in self._projects:
            sln += 'Project("{sln_guid}") = "{proj_name}", "{proj_fname}", "{proj_guid}"\r\n' \
                .format(sln_guid=self._guid,
                        proj_name=self._projects[fname].get_name(),
                        proj_fname=fname,
                        proj_guid=self._projects[fname].get_guid())
            sln += "EndProject\r\n"
        sln += "Global\r\n"
        sln += "\tGlobalSection(SolutionConfigurationPlatforms) = preSolution\r\n"
        for i in self._configurations:
            sln += "\t\t{name}|{platform} = {name}|{platform}\r\n" \
                .format(name=i.name, platform=i.platform)
        sln += "\tEndGlobalSection\r\n"
        sln += "\tGlobalSection(ProjectConfigurationPlatforms) = postSolution\r\n"
        for i in self._configurations:
            if i.platform == "x86":
                platform2 = "Win32"
            else:
                platform2 = i.platform
            sln += ("\t\t{guid}.{name}|{platform}.ActiveCfg = {name}|{platform2}\r\n"
                    "\t\t{guid}.{name}|{platform}.Build.0 = {name}|{platform2}\r\n") \
                    .format(guid=self._configurations[i].get_guid(),
                            name=i.name,
                            platform=i.platform,
                            platform2=platform2)
        sln += "\tEndGlobalSection\r\n"
        sln += "\tGlobalSection(SolutionProperties) = preSolution\r\n"
        sln += "\t\tHideSolutionNode = FALSE\r\n"
        sln += "\tEndGlobalSection\r\n"
        sln += "EndGlobal\r\n"
        return sln

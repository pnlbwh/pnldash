import sys
from plumbum import cli, local, FG
from pnldash_config import PROJECTS_DB_ENV
import pnldash_config as config
from pnldash_lib import read_project_yml, get_db_dir, read_yml
from pprint import pprint

PROJECT_YML = config.PROJECT_YML.name


def _get_db_ymls():
    dbdir = get_db_dir()
    ymlfiles = [d / PROJECT_YML for d in dbdir.list()
                if (d / PROJECT_YML).exists()]
    for ymlfile in ymlfiles:
        projectdir = ymlfile.dirname.name.replace('---', '/')
        yml = read_yml(ymlfile)
        yield yml['name'], projectdir, yml


class Db(cli.Application):
    """Interface to the central database of projects."""

    def main(self, *args):
        if args:
            print("Unknown command {0!r}".format(args[0]))
            return 1
        if not self.nested_command:
            print("No command given")
            return 1  # error exit code

def _find_project(name):

    ymltuples = _get_db_ymls()
    ymltuples_filt = filter(lambda x: x[0] == name, ymltuples)

    if not ymltuples_filt:
        print("No project found with name '{}'".format(name))
        print("Must be one of these:")
        names = [n for n,_,_ in ymltuples]
        if not names:
            print "None."
        else:
            print("\n".join(names))
        sys.exit(1)

    return ymltuples_filt


@Db.subcommand("env")
class Env(cli.Application):
    """Print the bash environment setup for a project's data paths."""

    paramid = cli.SwitchAttr(
        ['-p', '--paramid'],
        int,
        default=0,
        help="The index of the pipeline whose paths you want")

    #TODO make unset option?

    def main(self, name):

        ymltuples = _find_project(name)

        # TODO be able to select projects with same names
        _, projectdir, yml = ymltuples[0]

        print("export root={}".format(projectdir))
        paths = yml['pipelines'][self.paramid]['paths']
        for key, path in paths.items():
            print("export {}={}".format(key, path))


@Db.subcommand("ls")
class Ls(cli.Application):
    """List the project names in the central database"""

    def main(self):
        for name, projectdir, yml in _get_db_ymls():
            numpipelines = len(yml['pipelines'])
            print(yml['name'] + " ({}) ({} pipeline(s))".format(projectdir, numpipelines))


@Db.subcommand("show")
class Show(cli.Application):
    """Show the project.yml contents for a project."""

    def main(self, name):
        ymltuples = _find_project(name)
        # TODO be able to select projects with same names
        _, projectdir, yml = ymltuples[0]
        print("# {} ({})".format(name, projectdir))
        print
        # print("Grant ID: {}\n".format(yml['grantId'] or "None"))
        print("## Description\n")
        print(yml['description'])
        print("## Pipelines\n")
        pprint(yml['pipelines'])

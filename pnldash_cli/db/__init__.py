import logging
log = logging.getLogger(__name__)
from plumbum import cli, local, FG
from plumbum.path.utils import copy, gui_open
from pnldash_config import *
from pnldash_lib import open_db
import yaml


PNLDASH_FILES = [PROJECT_YML, PATHS_CSV, PARAMS_CSV, EXTRA_CSV, DU_CSV]

class Push(cli.Application):
    """Copies pnldash.yml and .pnldash/* to central project database"""

    def main(self):
        make_extra()
        with open_db() as (url, machine, dbpath):
            destdir = dbpath / (local.cwd.replace('/', '---')[3:])
            log.info('Copy files to central database...')
            copy(PNLDASH_FILES, destdir)
            print("Copied")
            print('\n'.join(PNLDASH_FILES))
            print('to {}'.format(url))


class Make(cli.Application):
    """Make HTML dashboard report."""

    def main(self):

        Rcmd = "library('rmarkdown'); render('pnldashboard.Rmd')"

        with open_db() as (url, machine, dbpath):
            log.info('Make dashboard')
            with machine.cwd(dbpath):
                _ = machine['R']('-e', Rcmd)
            copy(dbpath / 'pnldashboard.html', local.cwd)
            log.info("Made 'pnldashboard.html'")


class Open(cli.Application):
    """Open HTML dashboard in your browser (makes the dashboard first if it doesn't exist)."""

    refresh = cli.Flag(['-r', '--refresh'], default=False,
                       help="Remake the dashboard if it already exists.")

    def main(self):

        if not local.path('pnldashboard.html').exists() or self.refresh:
            Make.invoke()
        gui_open('pnldashboard.html')


class List(cli.Application):
    """List the project names in the central database"""

    def main(self):
        PROJECT_YML_FILENAME = PROJECT_YML.name

        with open_db() as (url, machine, dbpath):
            ymlfiles = [y for y in dbpath // ('*/' + PROJECT_YML_FILENAME)]
            for ymlfile in ymlfiles:
                projdir = ymlfile.dirname.replace('---', '/')
                ymlstr = machine['cat'](ymlfile)
                yml = yaml.load(ymlstr, Loader=yaml.loader.BaseLoader)
                numpipelines = len(yml['pipelines'])
                print(yml['name'] + " ({}) ({} pipeline(s))".format(projdir,
                                                                numpipelines))


class Info(cli.Application):
    """Show the project.yml contents for a project."""

    def main(self, name):
        PROJECT_YML_FILENAME = PROJECT_YML.name

        with open_db() as (url, machine, dbpath):
            ymlfiles = [y for y in dbpath // ('*/' + PROJECT_YML_FILENAME)]
            for ymlfile in ymlfiles:
                # TODO be able to select projects with same names
                projdir = ymlfile.dirname.replace('---', '/')
                ymlstr = machine['cat'](ymlfile)
                yml = yaml.load(ymlstr, Loader=yaml.loader.BaseLoader)
                if yml['name'] != name:
                    continue
                print("# {} ({})".format(yml['name'], projdir))
                print
                print("## Description\n")
                print(yml['description'])
                # print("## Pipelines\n")
                # pprint(yml['pipelines'])

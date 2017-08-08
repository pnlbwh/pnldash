from __future__ import print_function
from plumbum import cli, local
from pnldash_lib import read_project_yml
from .ls import readCaselist
from . import ParamApp
import sys


def _printVertical(d, prepend='', keys=None, fd=sys.stdout):
    if not keys:
        keys = d.keys()
    for k in keys:
        fd.write("{}{:<25} {:<15}".format(prepend, k, d[k]) + '\n')


def _print(s=''):
    print(s, file=sys.stdout)


def _printInfo(pipelines, paramid):

    numcases = len(readCaselist(pipelines[paramid-1]['paths']['caselist']))
    _print("## Pipeline {} ({} case(s))".format(paramid, numcases))
    _print("Parameters:")
    _printVertical(pipelines[paramid-1]['parameters'])
    _print()
    _print("Template paths:")
    _printVertical(pipelines[paramid-1]['paths'])
    _print()


class Info(ParamApp):
    """Prints a pipeline's information (in pnldash.yml)"""

    def main(self):

        yml = read_project_yml()

        yml = read_project_yml()
        self.validate(len(yml['pipelines']))

        if self.paramid < 1:
            for paramid, pipeline in enumerate(yml['pipelines'], 1):
                _printInfo(yml['pipelines'], paramid)
        else:
            _printInfo(yml['pipelines'], self.paramid)

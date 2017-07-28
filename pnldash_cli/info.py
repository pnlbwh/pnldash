from __future__ import print_function
from plumbum import cli, local
from pnldash_lib import read_project_yml
from .ls import readCaselist
import sys


def _printVertical(d, prepend='', keys=None, fd=sys.stderr):
    if not keys:
        keys = d.keys()
    for k in keys:
        fd.write("{}{:<25} {:<15}".format(prepend, k, d[k]) + '\n')


def _print(s=''):
    print(s, file=sys.stderr)


def _printInfo(pipelines, paramid):

    numcases = len(readCaselist(pipelines[paramid]['paths']['caselist']))
    _print("## Pipeline {} ({} case(s))".format(paramid, numcases))
    _print("Parameters:")
    _printVertical(pipelines[paramid]['parameters'])
    _print()
    _print("Template paths:")
    _printVertical(pipelines[paramid]['paths'])
    _print()


class Info(cli.Application):
    """Prints a pipeline's information (in pnldash.yml)"""

    paramid = cli.SwitchAttr(
        ['-p', '--paramid'],
        int,
        default=-1,
        help="The index of the pipeline whose paths you want")

    def main(self):

        yml = read_project_yml()

        num = len(yml['pipelines'])

        if self.paramid >= num:
            print(
                "paramid '{}' is greater than number of pipelines in pnldash.yml: {}".format(
                    self.paramid, num))
            print("Must be one of: {}".format(' '.join(map(str, range(num)))))
            sys.exit(1)

        if self.paramid < 0:
            for paramid, pipeline in enumerate(yml['pipelines']):
                _printInfo(yml['pipelines'], paramid)
        else:
            _printInfo(yml['pipelines'], self.paramid)

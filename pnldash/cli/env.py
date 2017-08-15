from __future__ import print_function
import sys
from plumbum import cli, local
from ..config import *
from .. import read_project_yml
from .ls import readCaselist
from . import ParamApp


def _print(s=''):
    print(s, file=sys.stderr)


def _print_map(d, prepend='', keys=None, fd=sys.stderr):
    if not keys:
        keys = d.keys()
    for k in keys:
        fd.write("{}{:<25} {:<15}".format(prepend, k, d[k]) + '\n')


def _escape(filepath):
    return filepath.__str__().replace('(', '\(').replace(')', '\)')


class Env(ParamApp):
    """Print the bash environment setup for a project's data paths."""

    def main(self, caseid=None):

        projectdir = PROJECT_YML.dirname
        yml = read_project_yml()
        self.paramid = self.paramid or 1
        self.validate(len(yml['pipelines']))

        _print("# Shell environment setup for pipeline {} (out of {})".format(
            self.paramid, len(yml['pipelines'])))
        _print("Parameters:")
        _print_map(yml['pipelines'][self.paramid-1]['parameters'], prepend='# ')
        print('')

        paths = yml['pipelines'][self.paramid-1]['paths']
        placeholder = paths['caseid_placeholder']

        print("export root={}".format(projectdir))
        for key, pathtemplate in paths.items():
            if key == 'caselist':
                # caseids = readCaselist(paths['caselist'])
                # print('export caselist="{}"'.format(' '.join(caseids)))
                pass
            else:
                if caseid:
                    path = pathtemplate.replace(placeholder, caseid)
                else:
                    path = pathtemplate
                print("export {}={}".format(key, _escape(path)))

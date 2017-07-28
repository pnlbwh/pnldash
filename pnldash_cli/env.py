from __future__ import print_function
import sys
from plumbum import cli, local
from pnldash_config import *
from pnldash_lib import read_project_yml
from .ls import readCaselist

def _print(s=''):
    print(s, file=sys.stderr)

def _print_map(d, prepend='', keys=None, fd=sys.stderr):
    if not keys:
        keys = d.keys()
    for k in keys:
        fd.write("{}{:<25} {:<15}".format(prepend, k, d[k]) + '\n')


class Env(cli.Application):
    """Print the bash environment setup for a project's data paths."""

    paramid = cli.SwitchAttr(
        ['-p', '--paramid'],
        int,
        default=0,
        help="The index of the pipeline in pnldash.yml whose paths you want")

    #TODO make unset option?

    def main(self, caseid=None):
        def escape(filepath):
            return filepath.__str__().replace('(', '\(').replace(')', '\)')

        projectdir = PROJECT_YML.dirname
        yml = read_project_yml()
        num = len(yml['pipelines'])
        if self.paramid >= num:
            print(
                "paramid '{}' is greater than/equal to number of pipelines in pnldash.yml: {}".format(
                    self.paramid, num))
            print("Must be one of: {}".format(' '.join(map(str, range(num)))))
            sys.exit(1)

        _print("# Shell environment setup for pipeline {} (out of {})".format(
            self.paramid, len(yml['pipelines'])))
        _print("Parameters:")
        _print_map(yml['pipelines'][self.paramid]['parameters'], prepend='# ')
        print('')


        paths = yml['pipelines'][self.paramid]['paths']
        placeholder = paths['caseid']

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
                print("export {}={}".format(key, escape(path)))

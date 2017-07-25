from __future__ import print_function
from plumbum import cli, local
from pnldash_lib import read_project_yml
import sys
from pnldash_lib.csvs import readCaselist

def _print(s=''):
    print(s, file=sys.stderr)

def _printVertical(d, prepend='', keys=None, fd=sys.stderr):
    if not keys:
        keys = d.keys()
    for k in keys:
        fd.write("{}{:<25} {:<15}".format(prepend, k, d[k]) + '\n')


class Ls(cli.Application):

    paramid = cli.SwitchAttr(
        ['-p', '--paramid'],
        int,
        default=0,
        help="The index of the pipeline whose paths you want")


    print_csv = cli.Flag(
        ['-c', '--csv'],
        excludes=['-s'],
        help="Print subject ids and paths separated by comma")

    print_caseid_only = cli.Flag(
        ['-s', '--subjid'],
        excludes=['-c'],
        help="Print subject ids instead of paths")

    ignore_caseids = cli.SwitchAttr(
        ['-e', '--except'], default="", help="Ignore this list of caseids")

    print_missing = cli.Flag(
        ['-x', '--missing'],
        default=False,
        excludes=['-a'],
        help="Print missing file paths instead of existing ones")

    print_all = cli.Flag(
        ['-a', '--all'],
        excludes=['-x'],
        default=False,
        help="Print file path whether it exists or not")

    def main(self, tag):
        ignore_caseids = self.ignore_caseids.split()
        if len(ignore_caseids) == 1 and './' in ignore_caseids[0]:
            ignore_caseids = interpret_caseids(ignore_caseids[0])

        yml = read_project_yml()

        for paramid, pipeline in enumerate(yml['pipelines']):
            caseids = readCaselist(pipeline['paths']['caselist'])
            combo = {k:v for (k,v) in pipeline['parameters'].items() \
                     if k not in ['caseid', 'caselist']}
            _print()
            print("## Parameter Combination {} ({} cases)".format(
                paramid, len(caseids)), file=sys.stderr)
            _printVertical(combo)
            print('', file=sys.stderr)

            template_path = pipeline['paths'][tag]
            placeholder = pipeline['paths']['caseid']
            for caseid in caseids:
                path = template_path.replace(placeholder, caseid)
                path = local.path(path)
                if self.print_missing == path.exists() and not self.print_all:
                    continue
                if self.print_caseid_only:
                    print('{}'.format(caseid))
                    return
                if self.print_csv:
                    sys.stdout.write('{},'.format(caseid))
                print(path)

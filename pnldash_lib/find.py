from __future__ import print_function
from plumbum import cli, local
import sys
import pnldash_config as config

DEFAULT_EXTS = ['.nrrd', '.nii.gz', '.nii', '.vtk', '.nhdr', '.mgz', '.dcm',
                '.dcm.gz', '.IMA', '.IMA.gz']
EXTS = getattr(config, 'FIND_EXTS', DEFAULT_EXTS)

PROJECT_YML = local.path(config.PROJECT_YML)


def fileFilter(p):
    return any(ext in ''.join(p.suffixes) for ext in EXTS) and not p.islink()


def dirFilter(d):
    return not (d / PROJECT_YML.name).exists() and not d.islink()


def _print(s):
    print(s, file=sys.stderr)


def _make_du():
    from plumbum.cmd import du
    diskUsageG = float(du('-sb').split()[0]) / 1024.0 / 1024.0 / 1024.0
    header = ["projectPath", "diskUsageG"]
    row = ['"{}"'.format(PROJECT_YML.dirname), str(diskUsageG)]
    output = ','.join(header) + '\n' + ','.join(row)
    with open(config.DU_CSV, 'w') as f:
        f.write(output)
    _print(output)
    _print("Made '{}'".format(config.DU_CSV))


def _make_find(echo_files):
    # TODO don't traverse directories with pnldash.yml in them
    paths = local.cwd.walk(fileFilter, dirFilter)
    num = 0
    with open(config.FIND_TXT, 'w') as f:
        for path in paths:
            f.write(path + '\n')
            num = num + 1
            if echo_files:
                print(path)
    _print("Found {} files with extensions: {}".format(num, ', '.join(EXTS)))
    _print("Made '{}".format(config.FIND_TXT))


class Find(cli.Application):

    echo = cli.Flag(
        ['-e', '--echo'], default=False, help="Print files to stdout as well")

    def main(self):
        config.CACHE_DIR.mkdir()
        _make_find(self.echo)
        print('')
        _make_du()


if __name__ == '__main__':
    Find.run()

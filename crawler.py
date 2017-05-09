#!/usr/bin/env python

from plumbum import cli, local
import sys

EXTS = ['.nrrd', '.nii.gz', '.nii', '.vtk', '.nhdr']

def fileFilter(p):
    return any(ext in ''.join(p.suffixes) for ext in EXTS)


class App(cli.Application):

    out = cli.SwitchAttr(
        ['-o'],
        mandatory = False,
        help='Output file')

    def main(self, rootPath):
        paths = local.path(rootPath).walk(fileFilter)

        if self.out:
            with open(self.out, 'w') as f:
                for path in paths:
                    f.write(path + '\n')
        else:
            for path in paths:
                sys.stdout.write(path + '\n')

if __name__ == '__main__':
    App.run()

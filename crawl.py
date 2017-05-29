#!/usr/bin/env python

from plumbum import cli, local
import sys

EXTS = ['.nrrd', '.nii.gz', '.nii', '.vtk', '.nhdr', '.mgz']


def fileFilter(p):
    return any(ext in ''.join(p.suffixes) for ext in EXTS) and not p.islink()


class Crawl(cli.Application):

    out = cli.SwitchAttr(['-o'], mandatory=False, help='Output file')

    def main(self, rootPath):
        # TODO don't traverse directories with project.yml in them
        paths = local.path(rootPath).walk(fileFilter)
        num = 0
        if self.out:
            with open(self.out, 'w') as f:
                for path in paths:
                    f.write(path + '\n')
                    num = num + 1
            print("Made '{}".format(self.out))
        else:
            for path in paths:
                sys.stdout.write(path + '\n')
                num = num + 1

        print("Found {} files with extensions: {}".format(num, ', '.join(EXTS)))


if __name__ == '__main__':
    Crawl.run()

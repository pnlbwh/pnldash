#!/usr/bin/env python

from plumbum import cli, local
import sys
import pandas as pd
import csv
import os


def getsize(path):
    pathP = local.path(path)
    if not pathP.exists():
        return 0
    if '.nhdr' in pathP.suffixes:
        return os.path.getsize(path)/1024.0/1024.0 + \
            getsize(pathP.with_suffix('.raw').__str__()) + \
            getsize(pathP.with_suffix('.raw.gz').__str__())
    return os.path.getsize(path)/1024.0/1024.0


class Diff(cli.Application):

    out = cli.SwitchAttr(
        ['-o'],
        help='Output file')

    ls = cli.Flag(['-l', '--ls'], default=False, help="List extra files")

    def main(self, pathsCsv, findtxt):
        paths = pd.read_csv(pathsCsv)
        if paths.empty:
            raise Exception("'{}' is empty".format(pathsCsv))
        existing_paths = [local.path(p) for p in paths[paths.exists]['path']]
        with open(findtxt, 'r') as f:
            found_paths = f.read().splitlines()
        unaccounted_files = set(found_paths) - set(existing_paths)
        if unaccounted_files:
            with open(self.out, 'w') as f:
                header = ['projectPath', 'path', 'sizeMB']
                csvwriter = csv.writer(f)
                csvwriter.writerow(header)
                if self.ls:
                    sys.stderr.write(', '.join(header) + '\n')
                sizeMBsum = 0
                for path in unaccounted_files:
                    sizeMB = getsize(path)
                    relativePath = local.path(path).relative_to(local.cwd)
                    row = [local.cwd, relativePath, sizeMB]
                    if self.ls:
                        sys.stderr.write(', '.join(map(str,row)) + '\n')
                    csvwriter.writerow(row)
                    sizeMBsum = sizeMBsum + sizeMB
            print("{0} unaccounted file(s) found, disk usage: {1:.2f}G".format(len(unaccounted_files), sizeMBsum/1024.0))
        else:
            with open(self.out, 'w') as f:
                pass # make empty file
            sys.stderr.write("No unaccounted files found\n")


if __name__ == '__main__':
    Diff.run()

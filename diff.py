#!/usr/bin/env python

from plumbum import cli, local
import sys
import pandas as pd
import csv
import os


class Diff(cli.Application):

    out = cli.SwitchAttr(
        ['-o'],
        help='Output file')

    def main(self, pathsCsv, findtxt):
        paths = pd.read_csv(pathsCsv)
        if paths.empty:
            raise Exception("'{}' is empty".format(pathsCsv))
        existing_paths = [local.path(p) for p in paths[paths.exists]['path']]
        with open(findtxt, 'r') as f:
            found_paths = f.read().splitlines()
        unaccounted_files = set(found_paths) - set(existing_paths)
        if unaccounted_files:
            sys.stderr.write("Unaccounted files found:\n")
            with open(self.out, 'w') as f:
                header = ['projectPath', 'path', 'sizeMB']
                csvwriter = csv.writer(f)
                csvwriter.writerow(header)
                sys.stderr.write(', '.join(header) + '\n')
                for path in unaccounted_files:
                    sizeMB = os.path.getsize(path)/1024.0/1024.0
                    relativePath = local.path(path).relative_to(local.cwd)
                    row = [local.cwd, relativePath, sizeMB]
                    sys.stderr.write(', '.join(map(str,row)) + '\n')
                    csvwriter.writerow(row)
            print("{} unaccounted file(s) found.".format(len(unaccounted_files)))
        else:
            with open(self.out, 'w') as f:
                pass # make empty file
            sys.stderr.write("No unaccounted files found\n")


if __name__ == '__main__':
    Diff.run()

#!/usr/bin/env python

from plumbum import cli, local
import sys
import pandas as pd


class App(cli.Application):

    out = cli.SwitchAttr(
        ['-o'],
        help='Output file')

    def main(self, csv, txt):
        paths = pd.read_csv(csv)
        existing_paths = paths[paths.exists]['path']
        with open(txt, 'r') as f:
            found_paths = f.read().splitlines()
        unaccounted_files = set(found_paths) - set(existing_paths)
        if unaccounted_files:
            sys.stderr.write("Unaccounted files found:\n")
            with open(self.out, 'w') as f:
                for path in unaccounted_files:
                    sys.stderr.write(path + '\n')
                    f.write(path + '\n')
        else:
            sys.stderr.write("No unaccounted files found\n")


if __name__ == '__main__':
    App.run()

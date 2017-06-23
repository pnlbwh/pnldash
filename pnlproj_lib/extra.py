#!/usr/bin/env python

from plumbum import cli, local
import sys
import pandas as pd
import csv
import os
from util import getsize


def extra(pathsCsv, findtxt, out, ls=False):
    paths = pd.read_csv(pathsCsv)
    if paths.empty:
        raise Exception("'{}' is empty".format(pathsCsv))
    existing_paths = [local.path(p) for p in paths[paths.exists]['path']]
    with open(findtxt, 'r') as f:
        found_paths = f.read().splitlines()
    unaccounted_files = set(found_paths) - set(existing_paths)
    if unaccounted_files:
        with open(out, 'w') as f:
            header = ['projectPath', 'path', 'sizeMB']
            csvwriter = csv.writer(f)
            csvwriter.writerow(header)
            if ls:
                sys.stderr.write(', '.join(header) + '\n')
            sizeMBsum = 0
            for path in unaccounted_files:
                sizeMB = getsize(path)
                relativePath = local.path(path).relative_to(local.cwd)
                row = [local.cwd, relativePath, sizeMB]
                if ls:
                    sys.stderr.write(', '.join(map(str,row)) + '\n')
                csvwriter.writerow(row)
                sizeMBsum = sizeMBsum + sizeMB
        print("{0} unaccounted file(s) found, disk usage: {1:.2f}G".format(len(unaccounted_files), sizeMBsum/1024.0))
    else:
        with open(self.out, 'w') as f:
            pass # make empty file
        sys.stderr.write("No unaccounted files found\n")

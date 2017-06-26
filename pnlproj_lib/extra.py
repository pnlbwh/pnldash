#!/usr/bin/env python

from plumbum import cli, local
import sys
import pandas as pd
import csv
import os
from util import getsize

EXTRA_CSV = 'extra.csv'


def heading(s):
    return s + '\n' + len(s) * '-'


def relativePath(p):
    return local.path(p).relative_to(local.cwd)


def computeExtra(pathsCsv, findCsv, cacheDir):
    outCsv = cacheDir / EXTRA_CSV
    paths = pd.read_csv(pathsCsv)
    if paths.empty:
        raise Exception("'{}' is empty".format(pathsCsv))
    existing_paths = [local.path(p) for p in paths[paths.exists]['path']]
    with open(findCsv, 'r') as f:
        found_paths = f.read().splitlines()
    extraFiles = [str(relativePath(p))
                  for p in set(found_paths) - set(existing_paths)]
    sizes = map(getsize, extraFiles)
    df = pd.DataFrame({'projectPath': local.cwd,
                       'path': extraFiles,
                       'sizeMB': sizes, })
    return df


def getExtra(pathsCsv, findCsv, cacheDir, useCache):
    outCsv = cacheDir / EXTRA_CSV
    if useCache and outCsv.exists():
        print("Using cached '{}'.".format(outCsv))
        return pd.read_csv(outCsv)
    return computeExtra(pathsCsv, findCsv, cacheDir)


def extra(pathsCsv, findCsv, cacheDir, ls=False, useCache=False):
    print(heading('Extra Image Files'))
    extraFiles = getExtra(pathsCsv, findCsv, cacheDir, useCache)

    if not extraFiles.empty:
        sizeMBsum = extraFiles['sizeMB'].sum()
        if ls:
            pd.options.display.float_format = '{:,.2f}'.format
            print(extraFiles.to_string(index=False))
        print("{} unaccounted file(s) found.".format(len(extraFiles['path'])))
        print("disk usage (G): {:.2f}".format(sizeMBsum / 1024.0))
    else:
        print("No unaccounted files found")

#!/usr/bin/env python

from plumbum import cli, local
import sys
import pandas as pd
import csv
import os
from util import getsize
from pnldash_config import *


def _heading(s):
    return s + '\n' + len(s) * '-'


def _relativePath(p):
    return local.path(p).relative_to(local.cwd)


def _computeExtra():
    paths = pd.read_csv(PATHS_CSV.__str__())
    if paths.empty:
        raise Exception("'{}' is empty".format(PATHS_CSV))
    existing_paths = [local.path(p) for p in paths[paths.exists]['path']]
    with open(FIND_TXT, 'r') as f:
        found_paths = f.read().splitlines()
    extraFiles = [str(_relativePath(p))
                  for p in set(found_paths) - set(existing_paths)]
    sizes = map(getsize, extraFiles)
    df = pd.DataFrame({'projectPath': local.cwd,
                       'path': extraFiles,
                       'sizeMB': sizes, })
    return df


def _getExtra(useCache):
    if useCache and EXTRA_CSV.exists():
        print("Using cached '{}'.".format(EXTRA_CSV))
        return pd.read_csv(EXTRA_CSV.__str__())
    df = _computeExtra()
    df.to_csv(EXTRA_CSV)
    return df


def make_extra(ls=False, useCache=False):
    print(_heading('Extra Image Files'))
    extraFiles = _getExtra(useCache)

    if not extraFiles.empty:
        sizeMBsum = extraFiles['sizeMB'].sum()
        if ls:
            pd.options.display.float_format = '{:,.2f}'.format
            print(extraFiles.to_string(index=False))
        print("{} unaccounted file(s) found.".format(len(extraFiles['path'])))
        print("disk usage (G): {:.2f}".format(sizeMBsum / 1024.0))
    else:
        print("No unaccounted files found")

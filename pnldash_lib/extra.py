#!/usr/bin/env python

from __future__ import print_function
from plumbum import cli, local
import sys
import pandas as pd
import csv
import os
from util import getsize
from pnldash_config import *
from .find import make_find
from .csvs import make_csvs


def _heading(s):
    return s + '\n' + len(s) * '-'


def _relativePath(p):
    return local.path(p).relative_to(local.cwd)


def _compute_extra_table():
    paths = pd.read_csv(PATHS_CSV.__str__())
    if paths.empty:
        raise Exception("'{}' is empty".format(PATHS_CSV))
    existing_paths = [local.path(p) for p in paths[paths.exists]['path']]
    with open(FIND_TXT, 'r') as f:
        found_paths = f.read().splitlines()
    extraFiles = [str(_relativePath(p))
                  for p in set(found_paths) - set(existing_paths)]
    sizes = map(getsize, extraFiles)
    df = pd.DataFrame({'projectPath': str(local.cwd),
                       'path': extraFiles,
                       'sizeMB': sizes, })
    return df


def make_extra(useCache=True):
    if not FIND_TXT.exists():
        make_find()
    if not PATHS_CSV.exists():
        make_csvs()
    extra_modtime = os.path.getmtime(str(EXTRA_CSV))
    find_modtime = os.path.getmtime(str(FIND_TXT))
    paths_modtime = os.path.getmtime(str(PATHS_CSV))
    if useCache and EXTRA_CSV.exists() \
       and extra_modtime > find_modtime \
       and extra_modtime > paths_modtime:
        print("Using cached '{}'.".format(EXTRA_CSV), file=sys.stderr)
        return pd.read_csv(EXTRA_CSV.__str__())
    df = _compute_extra_table()
    df.to_csv(str(EXTRA_CSV), index=False)
    return df

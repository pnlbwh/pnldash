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
import logging
log = logging.getLogger(__name__)


def _heading(s):
    return s + '\n' + len(s) * '-'


def _relativePath(p):
    return local.path(p).relative_to(local.cwd)


def _compute_extra_table():
    paths = pd.read_csv(PATHS_CSV.__str__())
    if paths.empty:
        raise Exception("'{}' is empty".format(PATHS_CSV))
    existing_paths = paths[paths.exists]['path']
    with open(FIND_TXT, 'r') as f:
        found_paths = f.read().splitlines()
    extraFiles = list(set(found_paths) - set(existing_paths))
    sizes = map(getsize, extraFiles)
    df = pd.DataFrame({ 'path': extraFiles,
                       'sizeMB': sizes, })
    return df


def make_extra():
    make_csvs()
    make_find()
    if EXTRA_CSV.exists():
        find_modtime = os.path.getmtime(str(FIND_TXT))
        paths_modtime = os.path.getmtime(str(PATHS_CSV))
        extra_modtime = os.path.getmtime(str(EXTRA_CSV))
        if extra_modtime > find_modtime and extra_modtime > paths_modtime:
            log.info("Using cached file '{}' for unaccounted files.".format(EXTRA_CSV))
            return pd.read_csv(EXTRA_CSV.__str__())
    log.info("Compute unaccounted files, might take a minute if your project directory is large")
    df = _compute_extra_table()
    df.to_csv(str(EXTRA_CSV), index=False)
    return df

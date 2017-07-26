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
    pipeline_files = pd.read_csv(PATHS_CSV.__str__())
    if pipeline_files.empty:
        raise Exception("'{}' is empty".format(PATHS_CSV))

    existing_pipeline_files = [local.path(p) for p in pipeline_files[pipeline_files.exists]['path']]
    existing_pipeline_files.sort()

    with open(FIND_TXT, 'r') as f:
        all_image_files = f.read().splitlines()
    all_image_files.sort()

    from plumbum.cmd import diff, tail, sort, cut
    with local.tempdir() as tmpdir:
        p = tmpdir / 'p'
        a = tmpdir / 'a'
        (tail['-n+2', PATHS_CSV] | cut['-d', ',' ,'-f', 5] | sort > p)()
        (sort[FIND_TXT] > a)()
        extra_image_files = diff('--new-line-format=""', '--unchanged-line-format=""', p, a, retcode=[0,1])

    sizes = map(getsize, extra_image_files)

    df = pd.DataFrame({'projectPath': str(local.cwd),
                       'path': extra_image_files,
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
            # print("Using cached '{}'.".format(EXTRA_CSV), file=sys.stderr)
            return pd.read_csv(EXTRA_CSV.__str__())
    df = _compute_extra_table()
    df.to_csv(str(EXTRA_CSV), index=False)
    return df

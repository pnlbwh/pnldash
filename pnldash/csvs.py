#!/usr/bin/env python
import sys
from plumbum import cli, local
import csv
import yaml
import os.path
import glob
import time
from util import getsize
import pandas as pd
from .config import *
from . import read_project_yml
import logging
log = logging.getLogger(__name__)

PARAM_HDR = ['projectPath', 'name', 'grantId', 'description', 'pipelineId',
             'pipelineDescription', 'param', 'paramValue']

PATH_HDR = ['projectPath', 'pipelineId', 'pathKey', 'caseid', 'path', 'sizeMB',
            'modtime', 'modtimeStr', 'exists']


def get_provenance_file(fn):
    prov = local.path(fn + '.provenance')
    if local.path(fn).exists():
        return [prov]
    return []

def get_nifti_assoc(nii):
    nii = local.path(nii)
    bvec = nii.with_suffix('.bvec', depth=2)
    bval = nii.with_suffix('.bval', depth=2)
    return [f for f in [bvec, bval] if f.exists()]


# ASSOC_FILES = {'.nii.gz': get_nifti_assoc,
#                '': get_provenance_file}
ASSOC_FILES = {'.nii.gz': get_nifti_assoc }


def concat(l):
    return l if l == [] else [item for sublist in l for item in sublist]


def readCaselistItem(s):
    if '/' in s:
        with open(s, 'r') as f:
            return [line.split()[0] for line in f.read().splitlines() if not line.startswith('#')]
    return [s]


def readCaselist(caselist):
    if isinstance(caselist, unicode):
        return readCaselistItem(caselist)
    elif isinstance(caselist, list):
        return concat(map(readCaselistItem, caselist))
    else:
        raise Exception("caselist field must be string or list type")


def make_csvs():
    if not PROJECT_YML.exists():
        print("Missing {}, create that first (e.g. pnldash init)".format(PROJECT_YML))
        sys.exit(1)
    paramsCsv = CACHE_DIR / 'params.csv'
    pathsCsv = CACHE_DIR / 'paths.csv'

    if PATHS_CSV.exists():
        yml_modtime = os.path.getmtime(str(PROJECT_YML))
        paths_modtime = os.path.getmtime(str(PATHS_CSV))
        if paths_modtime > yml_modtime:
            log.info("Using cached '{}' for pipeline filepaths.".format(PATHS_CSV))
            return

    log.info("Generate pipeline file paths from {}".format(PROJECT_YML.name))

    yml = read_project_yml()
    projectPath = PROJECT_YML.dirname

    CACHE_DIR.mkdir()

    #TODO convert to pandas

    with open(paramsCsv, 'w') as fparamsCsv:
        csvwriterParams = csv.writer(fparamsCsv)
        csvwriterParams.writerow(PARAM_HDR)
        with open(pathsCsv, 'w') as fpathsCsv:
            csvwriterPaths = csv.writer(fpathsCsv)
            csvwriterPaths.writerow(PATH_HDR)

            for pipelineId, pipeline in enumerate(yml['pipelines']):
                for param, paramVal in pipeline['parameters'].items():
                    csvwriterParams.writerow(
                        [projectPath, yml['name'], yml['grantId'],
                         yml['description'], pipelineId,
                         pipeline['description'], param, paramVal])
                caseids = readCaselist(pipeline['paths']['caselist'])
                caseidString = pipeline['paths']['caseid_placeholder']
                if not isinstance(caseidString, unicode):
                    raise Exception(
                        "caseid field needs to be in quotes to protect its value: TODO force read yml fields as strings")
                for pathKey, pathTemplate in pipeline['paths'].items():
                    if pathKey == 'caselist' or pathKey == 'caseid_placeholder':
                        continue
                    # ignore input files from outside the project directory
                    if not local.path(pathTemplate).startswith(local.cwd):
                        continue
                    for caseid in caseids:
                        path = pathTemplate.replace(caseidString, caseid)
                        paths = glob.glob(path)  # could be a glob pattern
                        if not paths:  # no glob
                            paths = [path]
                        for ext, getassoc in ASSOC_FILES.items():
                            if path.endswith(ext):
                                paths.extend(getassoc(path))
                        for path in paths:
                            mtime = None
                            mtimeStr = None
                            exists = False
                            sizeMB = None
                            if os.path.exists(path):
                                # mtime = os.path.getmtime(path)
                                # mtimeStr = time.strftime('%Y-%m-%d %H:%M:%S',
                                #                          time.localtime(mtime))
                                exists = True
                                sizeMB = getsize(path)
                            csvwriterPaths.writerow(
                                [projectPath, pipelineId, pathKey, caseid,
                                 local.path(path), sizeMB, mtime, mtimeStr, exists])

        # paths_table = pd.read_csv(PATHS_CSV.__str__())
        # paths_table.drop_duplicates()
        # paths_table.to_csv(pathsCsv.__str__())
        log.info("Made '{}'".format(paramsCsv))
        log.info("Made '{}'".format(pathsCsv))

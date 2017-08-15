from __future__ import print_function
from plumbum import cli, local
import sys
import pnldash.config as config
import pandas as pd
import logging
log = logging.getLogger(__name__)

# DEFAULT_EXTS = ['.nrrd', '.nii.gz', '.nii', '.vtk', '.nhdr', '.mgz', '.dcm',
#                 '.dcm.gz', '.IMA', '.IMA.gz', '.bval', '.bvec', '.provenance']
DEFAULT_EXTS = ['.nrrd', '.nii.gz', '.nii', '.vtk', '.nhdr', '.mgz', '.dcm',
                '.dcm.gz', '.IMA', '.IMA.gz', '.bval', '.bvec']
EXTS = getattr(config, 'FIND_EXTS', DEFAULT_EXTS)

PROJECT_YML = local.path(config.PROJECT_YML)


def _fileFilter(p):
    return any(p.endswith(ext) for ext in EXTS) and not p.islink()


def _dirFilter(d):
    return not (d / PROJECT_YML.name).exists() and not d.islink()


def _print(s):
    print(s, file=sys.stderr)


def _make_du():
    from plumbum.cmd import du
    diskUsageG = float(du('-sb').split()[0]) / 1024.0 / 1024.0 / 1024.0
    df = pd.DataFrame({'diskUsageG': [diskUsageG],
                       'projectPath': [PROJECT_YML.dirname]})
    df.to_csv(config.DU_CSV.__str__(), index=False)
    return df


def make_find(echo=False, useCache=True):
    if useCache and config.FIND_TXT.exists() and config.DU_CSV.exists():
        log.info("Using cached '{}' for all image files.".format(config.FIND_TXT))
        return
    paths = local.cwd.walk(_fileFilter, _dirFilter)
    num = 0
    log.info("Crawling directory for image files, might take a few minutes...")
    with open(config.FIND_TXT, 'w') as f:
        for path in paths:
            f.write(path + '\n')
            num = num + 1
            if echo:
                print(path)
    log.info("Found {} file(s) with extensions: {}".format(num, ', '.join(EXTS)))
    log.info("Made '{}".format(config.FIND_TXT))
    _make_du()

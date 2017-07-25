from __future__ import print_function
from plumbum import cli, local
import sys
import pnldash_config as config
import pandas as pd

DEFAULT_EXTS = ['.nrrd', '.nii.gz', '.nii', '.vtk', '.nhdr', '.mgz', '.dcm',
                '.dcm.gz', '.IMA', '.IMA.gz']
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
        return
    paths = local.cwd.walk(_fileFilter, _dirFilter)
    num = 0
    _print("Crawling directory for image files...")
    with open(config.FIND_TXT, 'w') as f:
        for path in paths:
            f.write(path + '\n')
            num = num + 1
            if echo:
                print(path)
    _print("Found {} file(s) with extensions: {}".format(num, ', '.join(EXTS)))
    _print("Made '{}".format(config.FIND_TXT))
    _make_du()

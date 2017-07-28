from __future__ import print_function
from plumbum import cli, local, FG
from plumbum.path.utils import copy, gui_open
from pnldash_config import *
from pnldash_lib import open_db, make_extra, read_project_yml
from .ls import readCaselist
import yaml
from collections import OrderedDict
import logging
log = logging.getLogger(__name__)

PNLDASH_FILES = [PATHS_CSV, PARAMS_CSV, EXTRA_CSV, DU_CSV]


class Push(cli.Application):
    """Adds your project to the central database."""

    def main(self):
        represent_dict_order = lambda self, data: self.represent_mapping('tag:yaml.org,2002:map', data.items())
        yaml.add_representer(OrderedDict, represent_dict_order)

        make_extra()

        with open_db() as (url, machine,
                           dbpath), local.tempdir() as tmpdir, open(
                               tmpdir / '.yml', 'w') as f:
            # expand caselist as it's usually a text file
            yml = read_project_yml()
            pipelines = yml['pipelines']
            for pipeline in yml['pipelines']:
                pipeline['paths']['caselist'] = readCaselist(pipeline['paths'][
                    'caselist'])
            yml['pipelines'] = pipelines
            yaml.dump(yml, f, default_flow_style=False)

            destdir = dbpath / (local.cwd.replace('/', '---')[3:])
            log.info('Copy files to central database...')
            copy(PNLDASH_FILES, destdir)
            copy(tmpdir / '.yml', destdir)
            print("Copied")
            print('\n'.join(PNLDASH_FILES))
            print('to {}'.format(url))

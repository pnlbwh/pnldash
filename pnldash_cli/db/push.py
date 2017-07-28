import logging
log = logging.getLogger(__name__)
from plumbum import cli, local, FG
from pnldash_config import *
from pnldash_lib import get_db_url, open_db


PNLDASH_FILES = [PROJECT_YML, PATHS_CSV, PARAMS_CSV, EXTRA_CSV, DU_CSV]

class Push(cli.Application):
    """Copies pnldash.yml and .pnldash/* to central project database"""

    def main(self):
        make_extra()
        with open_db() as (machine, dbpath):
            destdir = dbpath / (local.cwd.replace('/', '---')[3:])
            log.info('Copy files to central database...')
            copy(PNLDASH_FILES, destdir)
            print("Copied")
            print('\n'.join(PNLDASH_FILES))
            print('to {}'.format(get_db_url()))

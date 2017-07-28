#!/usr/bin/env python

from plumbum import cli, local
from plumbum.path.utils import copy
from pnldash_lib import open_db
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s: %(message)s')
log = logging.getLogger(__name__)



class App(cli.Application):
    def main(self):
        rmd = local.path(__file__).dirname / "pnldashboard.Rmd"

        with open_db() as (url, machine, dbpath):
            log.info("Make directory at '{}'".format(url))
            dbpath.mkdir()
            log.info("Copy '{}'".format(rmd))
            copy(rmd, dbpath)
            log.info("Made database at '{}'".format(url))

if __name__ == '__main__':
    App.run()

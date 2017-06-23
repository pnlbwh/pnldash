#!/usr/bin/env python

from plumbum import cli, local
from plumbum.cmd import pnlproj


class App(cli.Application):

    runFind = cli.SwitchAttr(['--find'], help='Crawl project directories as well')

    def main(self):
        dirs = local.cwd.dirs()
        for dir in dirs:
            projdir = '/' / dir.dirname.replace('---', '/')
            with local.cwd(projdir):
                if self.runFind:
                    pnlproj('find')
                pnlproj('diff')
                pnlproj('push')


if __name__ == '__main__':
    Diff.run()

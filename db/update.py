#!/usr/bin/env python

from plumbum import cli, local
from plumbum.cmd import pnlproj


class App(cli.Application):

    runFind = cli.SwitchAttr(['--find'], help='Crawl project directories as well')

    def main(self):
        dirs = [p for p in local.cwd.list() if p.is_dir() and not p.startswith('.')]
        for dir in dirs:
            projdir = local.path('/') / dir.name.replace('---', '/')
            print("Updating '{}'".format(projdir))
            with local.cwd(projdir):
                if self.runFind:
                    pnlproj('find')
                pnlproj('status')
                pnlproj('push')


if __name__ == '__main__':
    App.run()

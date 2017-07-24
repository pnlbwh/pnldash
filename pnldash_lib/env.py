import sys
from plumbum import cli, local, FG
from pnldash_config import PROJECTS_DB_ENV
import pnldash_config as config
from pnldash_lib import read_project_yml, get_db_dir, read_yml

PROJECT_YML = config.PROJECT_YML.name

class Env(cli.Application):

    def main(self, name):
        dbdir = get_db_dir()
        ymlfiles = [d/PROJECT_YML for d in dbdir.list() if (d/PROJECT_YML).exists()]
        allymls = [read_yml(ymlfile) for ymlfile in ymlfiles]
        ymls = filter(lambda y: y['name'] == name, allymls)

        if not ymls:
            print("No project found with name '{}'".format(name))
            print("Must be one of these:")
            names = [y['name'] for y in allymls]
            if not names:
                print "None."
            else:
                print("\n".join(names))
            sys.exit(1)

        print ymls[0]

if __name__ == '__main__':
    Env.run()

import sys
import os
from plumbum import cli, local, FG
from pnldash_config import PROJECTS_DB_ENV
import pnldash_config as config
from readyml import read_project_yml, read_yml
from urlparse import urlparse

PROJECT_YML_FILENAME = config.PROJECT_YML.name


def get_db_dir():
    dbdir = os.environ.get(PROJECTS_DB_ENV, None)
    if not dbdir:
        errmsg = "Set '{}' environment variable first.".format(PROJECTS_DB_ENV)
        raise Exception(errmsg)
    if ':' in dbdir:
        return dbdir
    return local.path(dbdir)

def spliturl(url):
    if ':' in url and not url.startswith('ssh://'):
        url = 'ssh://' + url
    result = urlparse(url)
    return result

# def spliturl(url):
#     user, host_port_path, _ = url.rpartition('@')
#     host, port_path, _ = host_port_path.rpartition(':')
#     if port_path.startswith('/'):  # no port
#         return (user, host, port_path, 22)
#     print port_path
#     print 'asdfasfsa'
#     port, path = port_path.split('/', 1)
#     return (user, host, '/' + path, int(port))


def get_db_project_dirs():
    return [d for d in get_db_dir().list()
            if d.is_dir() and (d / PROJECT_YML_FILENAME).exists()]

def _project_dir(dbprojdir):
    return '/' + dbprojdir.name.replace('---', '/')


# TODO add remote access
def get_projects(name=None):
    result = []
    for dbprojdir in get_db_project_dirs():
        yml = read_yml(dbprojdir / PROJECT_YML_FILENAME)
        projdir = _project_dir(dbprojdir)
        if name and yml['name'] == name:
            result.append((projdir, yml))
        else:
            result.append((projdir, yml))
    return result


def get_project_dirs():
    return [_project_dir(d) for d in get_db_project_dirs()]

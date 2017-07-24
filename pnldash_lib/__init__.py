from plumbum import local
import yaml
from pnldash_config import PROJECT_YML, PROJECTS_DB_ENV
import os

def get_db_dir():
    centralRepo = os.environ.get(PROJECTS_DB_ENV, None)
    if not centralRepo:
        errmsg = "Set '{}' environment variable first.".format(
            PROJECTS_DB_ENV)
        raise Exception(errmsg)
    return local.path(centralRepo)

def read_yml(ymlfile):
    with open(ymlfile, 'r') as f:
        yml = yaml.load(
            f, Loader=yaml.loader.
            BaseLoader)  # TODO force read each field as a string
    return yml

def read_project_yml():
    yml = read_yml(PROJECT_YML)
    required_keys = ['name', 'description']
    for required_key in required_keys:
        if not yml.get(required_key, None):
            raise Exception("'{}' missing required key: {}".format(
                PROJECT_YML, required_key))

    return yml

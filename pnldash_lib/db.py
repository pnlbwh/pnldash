import sys
import os
from plumbum import cli, local, FG, SshMachine
from pnldash_config import PROJECTS_DB_ENV
import urlparse
from contextlib import contextmanager


def get_db_url(urlstr=None):
    urlstr = urlstr or os.environ.get(PROJECTS_DB_ENV, None)
    if not urlstr:
        errmsg = "Set '{}' environment variable first.".format(PROJECTS_DB_ENV)
        raise Exception(errmsg)
    if ':' in urlstr and not urlstr.startswith('ssh://'):
        urlstr = 'ssh://' + urlstr
    return urlparse.urlparse(urlstr)


@contextmanager
def open_db(urlstr=None):
    url = _get_db_url(urlstr)
    if url.scheme:
        machine = SshMachine(url.hostname, user=url.username, port=url.port)
    else:
        machine = local
    yield machine, machine.path(url.path)
    if url.scheme:
        machine.close()

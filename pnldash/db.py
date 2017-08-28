import sys
import os
from plumbum import cli, local, FG, SshMachine
from .config import PROJECTS_DB_ENV
from contextlib import contextmanager

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


def _get_db_url(urlstr=None):
    urlstr = urlstr or os.environ.get(PROJECTS_DB_ENV, None)
    if not urlstr:
        errmsg = "Set '{}' environment variable first.".format(PROJECTS_DB_ENV)
        raise Exception(errmsg)
    if ':' in urlstr and not urlstr.startswith('ssh://'):
        urlstr = 'ssh://' + urlstr
    return urlstr


@contextmanager
def open_db(urlstr=None):
    urlstr = urlstr or _get_db_url(urlstr)
    url = urlparse(urlstr)
    if url.scheme:
        machine = SshMachine(url.hostname, user=url.username, port=url.port)
    else:
        machine = local
    yield urlstr, machine, machine.path(url.path)
    if url.scheme:
        machine.close()

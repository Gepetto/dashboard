import logging
import re
import unicodedata
from enum import IntEnum

from django.utils.safestring import mark_safe

import git

logger = logging.getLogger('rainboard.utils')

SOURCES = IntEnum('Sources', 'github gitlab redmine robotpkg travis')
TARGETS = IntEnum('Targets', '14.04 16.04 17.10 18.04 dubnium jessie')
INVALID_MAILS = ('localhost', 'none', 'noreply', 'example')


def slugify_with_dots(value):
    """
    slugify a name but keep dots
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s\.-]', '', value).strip().lower()
    return mark_safe(re.sub(r'[-\s]+', '-', value))


def api_next(source, req):
    if source == SOURCES.github:
        if 'Link' in req.headers:
            for link in req.headers['Link'].split(','):
                if 'next' in link:
                    return int(re.search(r'page=(\d+)', link).group(1))
    if source == SOURCES.gitlab:
        if 'X-Next-Page' in req.headers and req.headers['X-Next-Page']:
            return int(req.headers['X-Next-Page'])


def domain(url):
    """
    Extracts the domain of an url
    """
    if '://' in url or url.startswith('//'):
        url = url.split('//')[1]
    return url.split('/')[0]


def domain_link(url):
    dn = domain(url)
    return mark_safe(f'<a href="{url}">{dn}</a>')


def update_robotpkg(path):
    try:
        git.Repo(str(path / '.git')).remotes.origin.pull()
    except git.exc.GitCommandError:
        logger.error('Network error, retrying…')
        git.Repo(str(path / '.git')).remotes.origin.pull()
    try:
        git.Repo(str(path / 'wip' / '.git')).remotes.origin.pull()
    except git.exc.GitCommandError:
        logger.error('Network error, retrying…')
        git.Repo(str(path / 'wip' / '.git')).remotes.origin.pull()


def invalid_mail(mail):
    return any(invalid in mail for invalid in INVALID_MAILS)


def valid_name(name):
    return name.replace('_', ' ').replace('-', ' ').lower()

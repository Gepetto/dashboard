import re
import unicodedata
from enum import IntEnum

from django.utils.safestring import mark_safe

SOURCES = IntEnum('Sources', 'github gitlab redmine robotpkg travis')
TARGETS = IntEnum('Targets', '14.04 16.04 17.10 18.04 dubnium')


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
                    return int(re.search('page=(\d+)', link).group(1))
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

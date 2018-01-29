from enum import IntEnum
import unicodedata
import re

from django.utils.safestring import mark_safe

SOURCES = IntEnum('Sources', 'github gitlab redmine robotpkg')
TARGETS = IntEnum('Targets', '12.04 14.04 16.04 dubnium')


def slugify_with_dots(value):
    """
    slugify a name but keep dots
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s\.-]', '', value).strip().lower()
    return mark_safe(re.sub(r'[-\s]+', '-', value))

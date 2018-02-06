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

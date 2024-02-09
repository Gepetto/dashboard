import logging
import re
import unicodedata

from django.db.models import IntegerChoices
from django.utils.safestring import mark_safe

import git

logger = logging.getLogger("rainboard.utils")

SOURCES = IntegerChoices("Sources", "github gitlab redmine robotpkg travis")
INVALID_MAILS = ("localhost", "none", "noreply", "example")


def slugify_with_dots(value):
    """
    slugify a name but keep dots

    >>> slugify_with_dots('C`est la fête :3. yay.')
    'cest-la-fete-3.-yay.'
    """
    value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    value = re.sub(r"[^\w\s\.-]", "", value).strip().lower()
    return mark_safe(re.sub(r"[-\s]+", "-", value))


def api_next(source, req):
    if source == SOURCES.github:
        if "Link" in req.headers:
            for link in req.headers["Link"].split(","):
                if "next" in link:
                    return int(re.search(r"page=(\d+)", link).group(1))
    if source == SOURCES.gitlab:
        if req.headers.get("X-Next-Page"):
            return int(req.headers["X-Next-Page"])
        return None
    return None


def domain(url):
    """
    Extracts the domain of an url

    >>> domain('https://gitlab.laas.fr/pipo')
    'gitlab.laas.fr'

    >>> domain('gitlab.laas.fr/pipo')
    'gitlab.laas.fr'
    """
    if "://" in url or url.startswith("//"):
        url = url.split("//")[1]
    return url.split("/")[0]


def domain_link(url):
    """
    get a link to an url, showing the domain name.

    >>> domain_link('https://gitlab.laas.fr/pipo')
    '<a href="https://gitlab.laas.fr/pipo">gitlab.laas.fr</a>'
    """
    dn = domain(url)
    return mark_safe(f'<a href="{url}">{dn}</a>')


def update_robotpkg(path):
    try:
        git.Repo(str(path / ".git")).remotes.origin.pull()
    except git.exc.GitCommandError:
        logger.error("Network error, retrying…")
        git.Repo(str(path / ".git")).remotes.origin.pull()
    try:
        git.Repo(str(path / "wip" / ".git")).remotes.origin.pull()
    except git.exc.GitCommandError:
        logger.error("Network error, retrying…")
        git.Repo(str(path / "wip" / ".git")).remotes.origin.pull()


def invalid_mail(mail):
    return any(invalid in mail for invalid in INVALID_MAILS)


def valid_name(name):
    """
    Replace dashes and underscores by spaces, and lowercase.

    >>> valid_name('TALOS_Metapkg-ros_control_sot')
    'talos metapkg ros control sot'
    """
    return name.replace("_", " ").replace("-", " ").lower()


if __name__ == "__main__":
    import doctest

    doctest.testmod()

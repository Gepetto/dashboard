import logging

from django.core.management.base import BaseCommand

from rainboard.models import Project, Robotpkg
from rainboard.utils import SOURCES

ALLOWED_MAINTAINERS = ["hpp@laas.fr", "pinocchio@laas.fr"]
ATTRIBUTES = ["homepage", "license", "description"]
NUM_ATTRS = ["license"]
NOT_GITLAB = ["homepage", "license"]
logger = logging.getLogger("rainboard.management.checks")


def exclude_falsy(qs, attr):
    falsy = 0 if attr in NUM_ATTRS else ""
    return qs.exclude(**{f"{attr}__isnull": True}).exclude(**{attr: falsy})


class Command(BaseCommand):
    help = "Checks some metadata"  # noqa: A003

    def handle(self, *args, **options):  # noqa: C901
        for attr_name in ATTRIBUTES:
            print(f"\nChecking {attr_name}s\n")

            for project in Project.objects.all():
                attr = getattr(project, attr_name)
                if not attr:
                    logger.warning("project %s has no %s", project, attr_name)
                    for rpkg in exclude_falsy(project.robotpkg_set, attr_name):
                        rattr = getattr(
                            rpkg,
                            "comment" if attr_name == "description" else attr_name,
                        )
                        logger.warning("  found in rpkg %s: %s", rpkg, rattr)
                    for repo in exclude_falsy(project.repo_set, attr_name):
                        rattr = getattr(repo, attr_name)
                        logger.warning("  found in repo %s: %s", repo, rattr)
                    continue
                for rpkg in project.robotpkg_set.exclude(**{attr_name: attr}):
                    rattr = getattr(
                        rpkg,
                        "comment" if attr_name == "description" else attr_name,
                    )
                    logger.warning(
                        "prj %s's rpkg %s %s: %s Vs. %s",
                        project,
                        rpkg,
                        attr_name,
                        attr,
                        rattr,
                    )
                for repo in project.repo_set.exclude(**{attr_name: attr}):
                    if repo.forge.source == SOURCES.gitlab and attr in NOT_GITLAB:
                        continue
                    rattr = getattr(repo, attr_name)
                    logger.warning(
                        "project %s's repo %s %s: %s Vs. %s",
                        project,
                        repo.git_remote(),
                        attr_name,
                        attr,
                        rattr,
                    )

        print("\nChecking robotpkgs\n")

        for robotpkg in Robotpkg.objects.all():
            repo, project_repo = (
                robotpkg.master_repository,
                robotpkg.project.main_repo().url,
            )
            if repo and " " in repo:
                repo = repo.split()[1]
            if repo != project_repo:
                logger.warning(
                    "%s master_repository: %s != %s",
                    robotpkg,
                    repo,
                    project_repo,
                )

            version, project_version = robotpkg.pkgversion, robotpkg.project.version
            if "r" in version:
                version = version.split("r")[0]
            if version != project_version:
                logger.warning(
                    "%s version: %s != %s",
                    robotpkg,
                    version,
                    project_version,
                )

            if robotpkg.maintainer not in ALLOWED_MAINTAINERS:
                logger.warning("%s maintainer: %s", robotpkg, robotpkg.maintainer)

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
    help = "Checks some metadata"

    def handle(self, *args, **options):
        for attr_name in ATTRIBUTES:
            print(f"\nChecking {attr_name}s\n")

            for project in Project.objects.all():
                attr = getattr(project, attr_name)
                if not attr:
                    logger.warning(f"project {project} has no {attr_name}")
                    for rpkg in exclude_falsy(project.robotpkg_set, attr_name):
                        rattr = getattr(
                            rpkg, "comment" if attr_name == "description" else attr_name
                        )
                        logger.warning(f"  found in rpkg {rpkg}: {rattr}")
                    for repo in exclude_falsy(project.repo_set, attr_name):
                        rattr = getattr(repo, attr_name)
                        logger.warning(f"  found in repo {repo}: {rattr}")
                    continue
                for rpkg in project.robotpkg_set.exclude(**{attr_name: attr}):
                    rattr = getattr(
                        rpkg, "comment" if attr_name == "description" else attr_name
                    )
                    logger.warning(
                        f"prj {project}'s rpkg {rpkg} {attr_name}: {attr} Vs. {rattr}"
                    )
                for repo in project.repo_set.exclude(**{attr_name: attr}):
                    if repo.forge.source == SOURCES.gitlab and attr in NOT_GITLAB:
                        continue
                    rattr = getattr(repo, attr_name)
                    logger.warning(
                        f"project {project}'s repo {repo.git_remote()} {attr_name}: "
                        f"{attr} Vs. {rattr}"
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
                    f"{robotpkg} master_repository: {repo} != {project_repo}"
                )

            version, project_version = robotpkg.pkgversion, robotpkg.project.version
            if "r" in version:
                version = version.split("r")[0]
            if version != project_version:
                logger.warning(f"{robotpkg} version: {version} != {project_version}")

            if robotpkg.maintainer not in ALLOWED_MAINTAINERS:
                logger.warning(f"{robotpkg} maintainer: {robotpkg.maintainer}")

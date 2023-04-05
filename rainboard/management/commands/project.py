import itertools
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from autoslug.utils import slugify

from rainboard.models import (
    Forge,
    Namespace,
    Project,
    Robotpkg,
    update_github,
    update_gitlab,
)


class Command(BaseCommand):
    help = "run project creation stuff"  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument("org")
        parser.add_argument("project")

    def handle(self, org, project, *args, **options):  # noqa: C901
        path = settings.RAINBOARD_RPKG
        logger = logging.getLogger("rainboard.management.project")

        org = Namespace.objects.get(slug=org)
        slug = slugify(project)
        logger.warning("looking for %s / %s", org, slug)

        project = Project.objects.filter(slug=slug)

        if project.exists():
            logger.warning("found %s", project.get())
        else:
            logger.warning("not found. let's get it from github & gitlab")
            github = Forge.objects.get(slug="github")
            for data in github.api_list(f"/orgs/{org.slug}/repos"):
                if slugify(data["name"]) == slug:
                    logger.warning("found on github / %s", org)
                    update_github(github, org, data)
                    break
            for user in Namespace.objects.filter(group=False):
                for data in github.api_list(f"/users/{user.slug}/repos"):
                    if slugify(data["name"]) == slug:
                        logger.warning("found on github / %s", user)
                        update_github(github, user, data)
                        break
            gitlab = Forge.objects.get(slug="gitlab")
            for data in gitlab.api_list("/projects"):
                if slugify(data["name"]) == slug:
                    logger.warning("found on gitlab / %s", data["namespace"]["name"])
                    update_gitlab(gitlab, data)

        project = Project.objects.get(slug=slug)

        for slug in [project.slug, project.slug.replace("_", "-")]:
            for pkg in itertools.chain(
                path.glob(f"*/{slug}{project.suffix}"),
                path.glob(f"*/py-{slug}{project.suffix}"),
            ):
                obj, created = Robotpkg.objects.get_or_create(
                    name=pkg.name,
                    category=pkg.parent.name,
                    project=project,
                )
                if created:
                    logger.warning("found on robotpkg %s", obj)
                    obj.update(pull=False)

        for rpkg in project.robotpkg_set.all():
            logger.warning("updating images for %s", rpkg)
            rpkg.update_images()

        logger.warning("Done")

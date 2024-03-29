import itertools
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from rainboard.models import Project, Robotpkg
from rainboard.utils import update_robotpkg

logger = logging.getLogger("rainboard.robotpkg")


class Command(BaseCommand):
    help = "Populate database with Robotpkg data"

    def handle(self, *args, **options):
        path = settings.RAINBOARD_RPKG

        logger.info("Pulling Robotpkg repositories")
        update_robotpkg(path)

        for project in Project.objects.all():
            for slug in [project.slug, project.slug.replace("_", "-")]:
                for pkg in itertools.chain(
                    path.glob(f"*/{slug}{project.suffix}"),
                    path.glob(f"*/py-{slug}{project.suffix}"),
                    path.glob(f"*/{slug}{project.suffix}-ros2"),
                ):
                    obj, created = Robotpkg.objects.get_or_create(
                        name=pkg.name,
                        category=pkg.parent.name,
                        project=project,
                    )
                    if created:
                        logger.info("%s found in %s", project, pkg)
                        obj.update(pull=False)

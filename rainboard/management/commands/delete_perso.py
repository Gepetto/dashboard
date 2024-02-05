import logging

from django.core.management.base import BaseCommand

from rainboard.models import Project

LICENSES = (
    "https://raw.githubusercontent.com/spdx/license-list-data/master/json/licenses.json"
)
logger = logging.getLogger("rainboard.management.populate")


class Command(BaseCommand):
    help = "Delete personnal projects"

    def handle(self, *args, **options):
        logger.info("removing unwanted projects:")
        logger.info(str(Project.objects.filter(main_namespace__group=False).delete()))

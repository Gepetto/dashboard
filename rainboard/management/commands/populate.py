import logging

from django.core.management import call_command
from django.core.management.base import BaseCommand

import httpx

from rainboard.models import Forge, License, Repo

LICENSES = (
    "https://raw.githubusercontent.com/spdx/license-list-data/master/json/licenses.json"
)
logger = logging.getLogger("rainboard.management.populate")


class Command(BaseCommand):
    help = "populates licenses, projets, namespaces and repos from forges"

    def handle(self, *args, **options):
        logger.info("updating licenses")
        for data in httpx.get(LICENSES).json()["licenses"]:
            License.objects.get_or_create(
                spdx_id=data["licenseId"],
                defaults={"name": data["name"], "url": data["detailsUrl"]},
            )

        logger.info("updating forges")
        for forge in Forge.objects.order_by("source"):
            logger.info(" updating %s", forge)
            forge.get_projects()

        logger.info("updating repos")
        for repo in Repo.objects.all():
            logger.info(" updating %s", repo)
            repo.api_update()

        call_command("delete_perso")
        call_command("fetch")
        call_command("robotpkg")
        call_command("cmake")

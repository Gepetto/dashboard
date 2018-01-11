import logging

from django.core.management.base import BaseCommand

from rainboard.models import Forge, License, Repo

import requests

logger = logging.getLogger('rainboard.management.populate')

class Command(BaseCommand):
    help = 'populates licenses, projets, namespaces and repos from forges'

    def handle(self, *args, **options):
        github = Forge.objects.get(name='Github')

        logger.info(f'updating licenses')
        for data in requests.get(f'{github.api_url()}/licenses', headers=github.headers()).json():
            logger.info(f' updating license {data["name"]}')
            License.objects.get_or_create(github_key=data['key'],
                                          defaults={key: data[key] for key in ['name', 'spdx_id', 'url']})

        logger.info(f'updating forges')
        for forge in Forge.objects.all():
            logger.info(f' updating {forge}')
            forge.get_projects()

        logger.info(f'updating repos')
        for repo in Repo.objects.all():
            logger.info(f' updating {repo}')
            repo.api_update()

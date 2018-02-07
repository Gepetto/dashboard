import logging

from django.core.management.base import BaseCommand

import requests

from rainboard.models import Forge, License, Repo, Project

LICENSES = 'https://raw.githubusercontent.com/spdx/license-list-data/master/json/licenses.json'
logger = logging.getLogger('rainboard.management.populate')


class Command(BaseCommand):
    help = 'populates licenses, projets, namespaces and repos from forges'

    def handle(self, *args, **options):
        # github = Forge.objects.get(name='Github')

        logger.info(f'updating licenses')
        for data in requests.get(LICENSES).json()['licenses']:
            _, created = License.objects.get_or_create(spdx_id=data['licenseId'],
                                                       defaults={'name': data['name'], 'url': data['detailsUrl']})
            if created:
                logger.info(f' created license {data["name"]}')
        # for data in requests.get(f'{github.api_url()}/licenses', headers=github.headers()).json():
            # logger.info(f' updating license {data["name"]}')
            # License.objects.get_or_create(spdx_id=data['spdx_id'],
            #                               defaults={key: data[key] for key in ['name', 'url']})

        logger.info(f'updating forges')
        for forge in Forge.objects.order_by('source'):
            logger.info(f' updating {forge}')
            forge.get_projects()

        logger.info(f'updating repos')
        for repo in Repo.objects.all():
            logger.info(f' updating {repo}')
            repo.api_update()

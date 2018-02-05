import logging
import os

from django.core.management.base import BaseCommand

import requests

from rainboard.models import Repo, Namespace, Forge, SOURCES, Project

logger = logging.getLogger('rainboard.management.travis')

GITHUB = Forge.objects.get(source=SOURCES.github)


def update_travis_id(data):
    namespace, project = data['slug'].lower().split('/')
    namespace = Namespace.objects.get(slug=namespace)
    project, _ = Project.objects.get_or_create(name=data['name'], defaults={'main_namespace': namespace})
    repo, created = Repo.objects.get_or_create(forge=GITHUB, namespace=namespace, project=project,
                                               defaults={'name': data['name'], 'repo_id': 0})
    if created:
        repo.api_update()

    repo.travis_id = data['id']
    repo.save()


class Command(BaseCommand):
    help = 'Gets Repo.travis_id'

    def handle(self, *args, **options):
        logger.info('Adding Travis Forge if needed')
        travis, created = Forge.objects.get_or_create(source=SOURCES.travis, defaults={
            'name': 'Travis', 'url': 'https://travis-ci.org/', 'token': os.getenv('TRAVIS_TOKEN')
        })

        logger.info('Gettings travis_id')
        for namespace in Namespace.objects.all():
            logger.info(f' Gettings travis_id for {namespace}')
            next_url = f'/owner/{namespace.slug}/repos'
            data = travis.api_data(next_url)
            if not data or data['@type'] != 'repositories':
                continue
            while True:
                for repository in data['repositories']:
                    if repository['active']:
                        logger.info('  update travis id for ' + repository['slug'])
                        update_travis_id(repository)
                if data['@pagination']['next'] is None:
                    break
                next_url = data['@pagination']['next']['@href']
                data = travis.api_data(next_url)

from django.core.management.base import BaseCommand

from rainboard.models import Forge, License

import requests


class Command(BaseCommand):
    help = 'populates licenses, projets, namespaces and repos from forges'

    def handle(self, *args, **options):
        github = Forge.objects.get(name='Github')

        for data in requests.get(f'{github.api_url()}/licenses', headers=github.headers()).json():
            License.objects.get_or_create(github_key=data['key'],
                                          **{key: data[key] for key in ['name', 'spdx_id', 'url']})

        for forge in Forge.objects.all():
            forge.get_projects()

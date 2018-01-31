import logging

from django.core.management.base import BaseCommand
from django.conf import settings

from rainboard.models import Project, Robotpkg

import git

logger = logging.getLogger('rainboard.robotpkg')


class Command(BaseCommand):
    help = 'Populate database with Robotpkg data'

    def handle(self, *args, **options):
        path = settings.RAINBOARD_RPKG

        logger.info('Pulling Robotpkg repositories')
        git.Repo(str(path / '.git')).remotes.origin.pull()
        git.Repo(str(path / 'wip' / '.git')).remotes.origin.pull()

        for project in Project.objects.all():
            for pkg in path.glob(f'*/{project.slug}'):
                logger.info(f'{project} found in {pkg}')
                obj, created = Robotpkg.objects.get_or_create(name=pkg.name, category=pkg.parent.name, project=project)
                if created:
                    obj.update(pull=False)

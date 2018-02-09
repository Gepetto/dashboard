import logging

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from rainboard.models import Branch, Project, Repo, Robotpkg
from rainboard.utils import update_robotpkg

logger = logging.getLogger('rainboard.management.update')


class Command(BaseCommand):
    help = 'Update the DB'

    def handle(self, *args, **options):
        logger.info(f'\nUpdating all repos\n')
        for repo in Repo.objects.all():
            logger.info(f' {repo}')
            repo.update()

        logger.info(f'\nUpdating all branches\n')
        for branch in Branch.objects.all():
            logger.info(f' {branch}')
            branch.update(pull=False)

        logger.info(f'\nPulling Robotpkg\n')
        update_robotpkg(settings.RAINBOARD_RPKG)

        logger.info(f'\nUpdating Robotpkg\n')
        for robotpkg in Robotpkg.objects.all():
            logger.info(f' {robotpkg}')
            robotpkg.update(pull=False)

        logger.info(f'\nUpdating all projects\n')
        for project in Project.objects.all():
            logger.info(f' {project}')
            project.update()

        call_command('delete_perso')

import logging

from django.core.management.base import BaseCommand

from rainboard.models import Repo

logger = logging.getLogger('rainboard.management.fetch')

class Command(BaseCommand):
    help = 'Fetch all remotes'

    def handle(self, *args, **options):
        logger.info(f'Fetching all repos')
        for repo in Repo.objects.all():
            logger.info(f' fetching {repo}')
            repo.git().fetch()

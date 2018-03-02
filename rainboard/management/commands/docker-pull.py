import logging
from subprocess import call

from django.core.management.base import BaseCommand

from rainboard.models import Image

logger = logging.getLogger('rainboard.docker')


class Command(BaseCommand):
    help = 'Pull all docker images'

    def handle(self, *args, **options):
        logger.info('Pulling all docker images…')
        for image in Image.objects.all():
            call(image.pull())

import logging
from subprocess import call

from django.core.management.base import BaseCommand

from rainboard.models import Image, Robotpkg

logger = logging.getLogger('rainboard.docker')


class Command(BaseCommand):
    help = 'Push all docker images'

    def handle(self, *args, **options):
        logger.info('Pushing all docker images…')
        for image in Image.objects.all():
            ret = call(image.push())

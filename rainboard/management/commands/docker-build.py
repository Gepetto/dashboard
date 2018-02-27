import logging
from subprocess import call

from django.core.management.base import BaseCommand

from rainboard.models import Image, Robotpkg

logger = logging.getLogger('rainboard.docker')


class Command(BaseCommand):
    help = 'Create all docker images'

    def handle(self, *args, **options):
        logger.info('Creating all docker images…')

        for robotpkg in Robotpkg.objects.all():
            logger.info(f' {robotpkg}')
            robotpkg.update_images()

        logger.info('Building all docker images…')
        for image in Image.objects.all():
            ret = call(image.build())
            logger.info(f' {image}: {ret}')

from rainboard.models import Robotpkg
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Populate database with Docker images data'

    def handle(self, *args, **options):
        for rpkg in Robotpkg.objects.all():
            rpkg.update_images()

from django.core.management.base import BaseCommand

from rainboard.models import Robotpkg


class Command(BaseCommand):
    help = "Populate database with Docker images data"  # noqa: A003

    def handle(self, *args, **options):
        for rpkg in Robotpkg.objects.all():
            rpkg.update_images()

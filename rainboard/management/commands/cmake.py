from django.core.management.base import BaseCommand

from rainboard.models import Project


class Command(BaseCommand):
    help = "Get informations from CMakeLists.txt on all projects"

    def handle(self, *args, **options):
        for project in Project.objects.all():
            project.cmake()

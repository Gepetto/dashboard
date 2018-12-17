from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db.models import F, Q

from rainboard.models import Branch, Forge, Project, Repo, Robotpkg
from rainboard.utils import SOURCES, update_robotpkg


class Command(BaseCommand):
    help = 'Update the DB'

    def handle(self, *args, **options):
        def log(message):
            self.stdout.write(message)

        log(f'updating forges')
        for forge in Forge.objects.order_by('source'):
            log(f' updating {forge}')
            forge.get_projects()

        log(f'\nUpdating all repos\n')
        for repo in Repo.objects.all():
            log(f' {repo}')
            repo.update()

        log(f'\nUpdating all branches\n')
        for branch in Branch.objects.all():
            log(f' {branch.project} - {branch}')
            branch.update(pull=False)

        log(f'\nPulling Robotpkg\n')
        update_robotpkg(settings.RAINBOARD_RPKG)

        log(f'\nUpdating all projects\n')
        for project in Project.objects.all():
            log(f' {project}')
            project.update()

        log(f'\nUpdating Robotpkg\n')
        for robotpkg in Robotpkg.objects.all():
            log(f' {robotpkg}')
            robotpkg.update(pull=False)

        log(f'\nUpdating keep doc\n')
        Branch.objects.filter(
                Q(name__endswith='master') | Q(name__endswith='devel'),
                repo__namespace=F('project__main_namespace'), repo__forge__source=SOURCES.gitlab
                ).update(keep_doc=True)

        log(f'\nDelet perso\n')
        call_command('delete_perso')

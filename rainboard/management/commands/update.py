import re
from datetime import timedelta

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db.models import F, Q
from django.utils import timezone

import github
from rainboard.models import BAD_ONES, Branch, Forge, Image, IssuePr, Project, Repo, Robotpkg
from rainboard.utils import SOURCES, update_robotpkg

MIN_DAYS_SINCE_UPDATED = 10  # Only show issues and pull requests older than this
SKIP_LABEL = 'skip dashboard'  # Issues and prs with this label will not be added to the dashboard


def update_issues_pr():
    print('\nUpdating issues and pull requests')
    for project in Project.objects.exclude(BAD_ONES):
        try:
            gh = project.github()
            main_repo = project.repo_set.filter(namespace=project.main_namespace, forge__source=SOURCES.github).first()

            # Create new issues and pull requests
            for issue in gh.get_issues(state='open'):
                days_since_updated = (timezone.now() - timezone.make_aware(issue.updated_at)).days
                if main_repo is not None and days_since_updated > MIN_DAYS_SINCE_UPDATED \
                        and SKIP_LABEL not in [label.name for label in issue.get_labels()]:
                    url = re.sub('api\\.github\\.com/repos', 'github.com', issue.url)

                    db_issue, _ = IssuePr.objects.get_or_create(repo=main_repo,
                                                                number=issue.number,
                                                                is_issue=bool(issue.pull_request is None),
                                                                defaults={
                                                                    'title': issue.title,
                                                                    'url': url,
                                                                })
                    if db_issue.title != issue.title or db_issue.url != issue.url:
                        db_issue.title = issue.title
                        db_issue.url = issue.url
                        db_issue.save()

        except github.UnknownObjectException:
            print(f'Project not found: {project.main_namespace.slug}/{project.slug}')

    # Update all issues and pull requests, delete closed ones
    for issue_pr in IssuePr.objects.all():
        issue_pr.update(SKIP_LABEL)


class Command(BaseCommand):
    help = 'Update the DB'

    def handle(self, *args, **options):
        def log(message):
            self.stdout.write(message)

        log('\nUpdating all repos\n')
        for repo in Repo.objects.filter(project__archived=False, project__main_namespace__from_gepetto=True):
            log(f' {repo}')
            repo.update()

        log('\nUpdating all branches\n')
        for branch in Branch.objects.filter(project__archived=False, project__main_namespace__from_gepetto=True):
            log(f' {branch.project} - {branch}')
            branch.update(pull=False)

        log('\nPulling Robotpkg\n')
        update_robotpkg(settings.RAINBOARD_RPKG)

        log('\nUpdating gepetto projects\n')
        for project in Project.objects.exclude(BAD_ONES):
            log(f' {project}')
            project.update(only_main_branches=False)

        log('\nUpdating Robotpkg\n')
        for robotpkg in Robotpkg.objects.filter(project__archived=False, project__main_namespace__from_gepetto=True):
            log(f' {robotpkg}')
            robotpkg.update(pull=False)

        log('\nUpdating keep doc\n')
        Branch.objects.filter(Q(name__endswith='master') | Q(name__endswith='devel'),
                              repo__namespace=F('project__main_namespace'),
                              repo__forge__source=SOURCES.gitlab).update(keep_doc=True)

        log('\nDelete perso\n')
        call_command('delete_perso')

        log('\nclean obsolete Images\n')
        Image.objects.filter(robotpkg__project__archived=True).delete()

        log('\nLook for missing images\n')
        for img in Image.objects.active().filter(created__lt=timezone.now() - timedelta(days=7)):
            log(f' {img}')

        update_issues_pr()

        log('updating forges')
        for forge in Forge.objects.order_by('source'):
            log(f' updating {forge}')
            forge.get_projects()

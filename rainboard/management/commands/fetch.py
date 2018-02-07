import logging

from django.core.management.base import BaseCommand

from rainboard.models import Project

logger = logging.getLogger('rainboard.management.fetch')


class Command(BaseCommand):
    help = 'Fetch all remotes'

    def handle(self, *args, **options):
        logger.info(f'Fetching all repos')
        for project in Project.objects.all():
            logger.info(f' fetching repos for {project}')
            for repo in project.repo_set.all():
                repo.fetch()
            logger.info(f' fetching devel & master for {project}')
            git = project.git()
            remote = git.remote(project.main_repo().git_remote())
            if 'devel' not in git.heads:
                try:
                    git.create_head('devel', remote.refs.devel).set_tracking_branch(remote.refs.devel).checkout()
                except AttributeError:
                    logger.warning(f'Project {project} has no devel branch')
            if 'master' not in git.heads:
                try:
                    git.create_head('master', remote.refs.master).set_tracking_branch(remote.refs.master).checkout()
                except AttributeError:
                    logger.warning(f'Project {project} has no master branch')
            logger.info(f' updating branches for {project}')
            project.update_branches(main=False, pull=False)

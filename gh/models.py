import logging

import git
from django.db import models

from ..rainboard.models import Namespace, Project

logger = logging.getLogger(__name__)


class GithubCheckSuite(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)

    def __str__(self):
        return f"{self.id}"


class PushQueue(models.Model):
    namespace = models.ForeignKey(Namespace, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    gl_remote_name = models.CharField(max_length=255)
    branch = models.CharField(max_length=255)

    def __str__(self):
        return (
            f"{self.namespace} / {self.project} / {self.gl_remote_name} / {self.branch}"
        )

    def push(self):
        git_repo = self.project.git()

        # Push the changes to gitlab
        logger.info(
            "%s/%s: Pushing %s on gitlab",
            self.namespace.slug,
            self.project.slug,
            self.branch,
        )
        try:
            git_repo.git.push(self.gl_remote_name, self.branch)
        except git.exc.GitCommandError:
            logger.warning(
                "%s/%s: Failed to push on %s on gitlab, force pushing ...",
                self.namespace.slug,
                self.project.slug,
                self.branch,
            )
            git_repo.git.push(self.gl_remote_name, self.branch, force=True)

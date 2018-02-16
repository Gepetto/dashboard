from django.contrib.admin import site

from . import models

for model in [
        models.Article,
        models.License,
        models.Namespace,
        models.Project,
        models.Repo,
        models.Branch,
        models.Robotpkg,
        models.Image,
        models.Tag,
        models.Contributor,
        models.ContributorName,
        models.ContributorMail,
]:
    site.register(model)

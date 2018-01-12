from django.contrib.admin import site

from .models import Article, License, Namespace, Project, Repo

for model in [Article, License, Namespace, Project, Repo]:
    site.register(model)

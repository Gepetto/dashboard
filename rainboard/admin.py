from django.contrib.admin import ModelAdmin, site

from . import models


class ContributorAdmin(ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).gepettist()


site.register(models.Contributor, ContributorAdmin)
for model in [
        models.License,
        models.Namespace,
        models.Project,
        models.Repo,
        models.Branch,
        models.Robotpkg,
        models.Image,
        models.Tag,
        models.Target,
        models.ContributorName,
        models.ContributorMail,
]:
    site.register(model)

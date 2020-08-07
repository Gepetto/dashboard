from django.contrib.admin import ModelAdmin, TabularInline, site

from . import models


class RobotpkgInline(TabularInline):
    model = models.Robotpkg


class ContributorAdmin(ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).gepettist().distinct()


class DependencyAdmin(ModelAdmin):
    autocomplete_fields = ('project', 'library')


class ProjectAdmin(ModelAdmin):
    search_fields = ('name', 'slug')
    inlines = [RobotpkgInline]


site.register(models.Contributor, ContributorAdmin)
site.register(models.Project, ProjectAdmin)
site.register(models.Dependency, DependencyAdmin)
for model in [
        models.License,
        models.Forge,
        models.Namespace,
        models.Repo,
        models.Branch,
        models.Robotpkg,
        models.Image,
        models.Tag,
        models.Target,
        models.ContributorName,
        models.ContributorMail,
        models.IssuePr,
]:
    site.register(model)

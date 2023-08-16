from django.contrib import admin

from . import models


class RobotpkgInline(admin.TabularInline):
    model = models.Robotpkg


@admin.register(models.Contributor)
class ContributorAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).gepettist().distinct()


@admin.register(models.Dependency)
class DependencyAdmin(admin.ModelAdmin):
    autocomplete_fields = ("project", "library")


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = ("name", "slug")
    inlines = [RobotpkgInline]  # noqa: RUF012


@admin.register(models.Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "main", "public")


for model in [
    models.License,
    models.Forge,
    models.Namespace,
    models.Repo,
    models.Branch,
    models.Robotpkg,
    models.Image,
    models.Tag,
    models.ContributorName,
    models.ContributorMail,
    models.IssuePr,
]:
    admin.site.register(model)

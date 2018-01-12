from django.utils.safestring import mark_safe

import django_tables2 as tables

from . import models


class StrippedTable(tables.Table):
    class Meta:
        attrs = {'class': 'table table-striped'}


class ForgeTable(StrippedTable):
    class Meta:
        model = models.Forge
        fields = ('name', 'url')


class NamespaceTable(StrippedTable):
    class Meta:
        model = models.Namespace
        fields = ('group', 'name')


class ProjectTable(StrippedTable):
    class Meta:
        model = models.Project
        fields = ('main_namespace', 'name', 'license', 'homepage')

    def render_name(self, record):
        return record.get_link()


class RepoTable(StrippedTable):
    class Meta:
        model = models.Repo
        fields = ('forge', 'namespace', 'license', 'homepage', 'default_branch', 'open_issues', 'open_pr')

    def render_forge(self, value):
        return value.get_link()

    def render_namespace(self, record):
        return mark_safe(f'<a href="{record.url}">{record.namespace}</a>')

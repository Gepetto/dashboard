from django.utils.safestring import mark_safe

import django_tables2 as tables

from . import models, utils


class StrippedTable(tables.Table):
    class Meta:
        attrs = {'class': 'table table-striped'}


class ArticleTable(StrippedTable):
    class Meta:
        model = models.Article
        fields = ('name', 'authors', 'year', 'url', 'pdf')


class ForgeTable(StrippedTable):
    class Meta:
        model = models.Forge
        fields = ('name', 'url')


class NamespaceTable(StrippedTable):
    class Meta:
        model = models.Namespace
        fields = ('group', 'name')


class ProjectTable(StrippedTable):
    commits_since = tables.Column(accessor='commits_since', orderable=False)
    repos = tables.Column(accessor='repos', orderable=False)
    rpkgs = tables.Column(accessor='rpkgs', orderable=False)

    class Meta:
        model = models.Project
        fields = ('main_namespace', 'name', 'license', 'homepage', 'updated', 'version')

    def render_name(self, record):
        return record.get_link()

    def render_homepage(self, value):
        return utils.domain_link(value)


class RepoTable(StrippedTable):
    ahead = tables.Column(accessor='ahead', orderable=False)
    behind = tables.Column(accessor='behind', orderable=False)

    class Meta:
        model = models.Repo
        fields = ('forge', 'namespace', 'license', 'homepage', 'default_branch', 'open_issues', 'open_pr')

    def render_forge(self, value):
        return value.get_link()

    def render_namespace(self, record):
        return mark_safe(f'<a href="{record.url}">{record.namespace}</a>')


class BranchTable(StrippedTable):
    ci = tables.Column(accessor='ci', orderable=False)

    class Meta:
        model = models.Branch
        fields = ('name', 'ahead', 'behind', 'updated')

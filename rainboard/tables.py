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
    issues = tables.Column(accessor='open_issues', orderable=False)
    pr = tables.Column(accessor='open_pr', orderable=False)
    rpkgs = tables.Column(accessor='rpkgs', orderable=False)

    class Meta:
        model = models.Project
        fields = ('main_namespace', 'name', 'public', 'license', 'homepage', 'updated', 'version')

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
    forge = tables.Column(accessor='forge', orderable=False)
    namespace = tables.Column(accessor='namespace', orderable=False)
    ci = tables.Column(accessor='ci', orderable=False)

    class Meta:
        model = models.Branch
        fields = ('forge', 'namespace', 'name', 'ahead', 'behind', 'updated')

    def render_name(self, record, value):
        if record.repo is None:
            return value
        name = record.name.split('/', maxsplit=2)[2]
        return mark_safe(f'<a href="{record.repo.url}/tree/{name}">{name}</a>')

    def render_forge(self, value):
        if value:
            return value.get_link()

    def render_namespace(self, record, value):
        if value:
            return mark_safe(f'<a href="{record.repo.url}">{value}</a>')

    # TODO: this works, but we have to hide the pinned from the main dataset
    # def get_top_pinned_data(self):
        # return self.data.data.filter(name__in=models.MAIN_BRANCHES)


class ImageTable(StrippedTable):
    class Meta:
        model = models.Image
        fields = ('robotpkg', 'target', 'image', 'created')


class ContributorTable(StrippedTable):
    names = tables.Column(accessor='names', orderable=False)
    mails = tables.Column(accessor='mails', orderable=False)

    class Meta:
        model = models.Contributor
        fields = ('names', 'mails')


class ContributorProjectTable(ContributorTable):
    projects = tables.Column(accessor='contributed', orderable=False)

    class Meta:
        fields = ('names', 'mails', 'projects')

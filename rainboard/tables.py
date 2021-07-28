from django.urls import reverse
from django.utils.safestring import mark_safe

import django_tables2 as tables

from . import models, utils


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
    pipeline_results = tables.Column(accessor='pipeline_results', orderable=False)
    commits_since = tables.Column(accessor='commits_since', orderable=False)
    repos = tables.Column(accessor='repos', orderable=False)
    issues = tables.Column(accessor='open_issues', orderable=False)
    pr = tables.Column(accessor='open_pr', orderable=False)
    rpkgs = tables.Column(accessor='rpkgs', orderable=False)
    badges = tables.Column(accessor='badges', orderable=False)
    from_gepetto = tables.BooleanColumn(accessor='main_namespace__from_gepetto')

    class Meta:
        model = models.Project
        fields = ('main_namespace', 'name', 'public', 'from_gepetto', 'license', 'homepage', 'updated', 'version')

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
        fields = ('forge', 'namespace', 'name', 'ahead', 'behind', 'updated', 'keep_doc')

    def render_name(self, record, value):
        if record.repo is None:
            return value
        name = record.name.split('/', maxsplit=2)[2] if '/' in record.name else record.name
        return mark_safe(f'<a href="{record.repo.url}/tree/{name}">{name}</a>')

    def render_forge(self, value):
        if value:
            return value.get_link()

    def render_namespace(self, record, value):
        if value:
            return mark_safe(f'<a href="{record.repo.url}">{value}</a>')

    def render_keep_doc(self, record, value):
        url = reverse('admin:rainboard_branch_change', args=[record.id])
        status = {True: '✓', False: '✗'}[value]
        return mark_safe(f'<a href="{url}">{status}</a>')

    # TODO: this works, but we have to hide the pinned from the main dataset
    # def get_top_pinned_data(self):
    # return self.data.data.filter(name__in=models.MAIN_BRANCHES)


class ImageTable(StrippedTable):
    name = tables.Column(accessor='get_image_name', orderable=False)

    class Meta:
        model = models.Image
        fields = ('name', 'robotpkg', 'target', 'image', 'allow_failure', 'created')

    def render_name(self, record, value):
        if value:
            return mark_safe(f'<a href="{record.get_image_url()}">{value}</a>')

    def render_allow_failure(self, record, value):
        url = reverse('admin:rainboard_image_change', args=[record.id])
        status = {True: '✓', False: '✗'}[value]
        return mark_safe(f'<a href="{url}">{status}</a>')


class ContributorTable(StrippedTable):
    names = tables.Column(accessor='names', orderable=False)
    mails = tables.Column(accessor='mails', orderable=False)

    class Meta:
        model = models.Contributor
        fields = ('agreement_signed', 'names', 'mails')


class ContributorProjectTable(ContributorTable):
    projects = tables.Column(accessor='contributed', orderable=False)

    class Meta:
        fields = ('names', 'mails', 'projects')


class IssuePrTable(StrippedTable):
    name = tables.Column(accessor='repo__project__name')

    class Meta:
        model = models.IssuePr
        fields = ('repo__namespace', 'name', 'title', 'url', 'days_since_updated')
        order_by = '-days_since_updated'

    def render_name(self, record):
        return record.repo.project.get_link()

    def render_url(self, record):
        rendered_name = 'issue #' if record.is_issue else 'PR #'
        return mark_safe(f'<a href="{record.url}">{rendered_name}{record.number}</a>')

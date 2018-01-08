from django.utils.safestring import mark_safe

import django_tables2 as tables

from .models import Project, Repo


class ProjectTable(tables.Table):
    class Meta:
        model = Project
        fields = ('main_namespace', 'name', 'license', 'homepage')
        attrs = {'class': 'table table-striped'}

    def render_name(self, record):
        return record.get_link()


class RepoTable(tables.Table):
    class Meta:
        model = Repo
        fields = ('forge', 'namespace', 'license', 'homepage', 'default_branch', 'open_issues', 'open_pr')

    def render_forge(self, value):
        return value.get_link()

    def render_namespace(self, record):
        return mark_safe(f'<a href="{record.url}">{record.namespace}</a>')

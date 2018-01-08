import django_tables2 as tables
from .models import Project


class ProjectTable(tables.Table):
    class Meta:
        model = Project
        fields = ('main_namespace', 'name', 'license', 'homepage')
        attrs = {'class': 'table table-striped'}

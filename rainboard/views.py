from django.shortcuts import render
from django.views.generic import DetailView

from django_filters.views import FilterView
from django_tables2 import RequestConfig
from django_tables2.views import SingleTableMixin

from .filters import ProjectFilter
from .models import Forge, Namespace, Project
from .tables import ProjectTable, RepoTable


def home(request):
    projects = ProjectTable(Project.objects.all())
    RequestConfig(request).configure(projects)
    return render(request, 'rainboard/home.html', {
        'forges': Forge.objects.all(),
        'namespaces': Namespace.objects.all(),
        'projects': projects,
    })


class ProjectsView(SingleTableMixin, FilterView):
    model = Project
    table_class = ProjectTable
    filterset_class = ProjectFilter


class ProjectView(DetailView):
    model = Project

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        repos = RepoTable(self.object.repo_set.all())
        RequestConfig(self.request).configure(repos)
        ctx['repos'] = repos
        return ctx

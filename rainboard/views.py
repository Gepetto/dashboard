from django.shortcuts import render
from django.views.generic import DetailView

from django_tables2 import RequestConfig

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


class ProjectView(DetailView):
    model = Project

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        repos = RepoTable(self.object.repo_set.all())
        RequestConfig(self.request).configure(repos)
        ctx['repos'] = repos
        return ctx

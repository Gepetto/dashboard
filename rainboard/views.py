from django.shortcuts import render

from django_tables2 import RequestConfig

from .models import Forge, Namespace, Project
from .tables import ProjectTable


def home(request):
    projects = ProjectTable(Project.objects.all())
    RequestConfig(request).configure(projects)
    return render(request, 'rainboard/home.html', {
        'forges': Forge.objects.all(),
        'namespaces': Namespace.objects.all(),
        'projects': projects,
    })

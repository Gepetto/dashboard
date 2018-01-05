from django.shortcuts import render

from .models import Forge, Namespace, Project


def home(request):
    return render(request, 'rainboard/home.html', {
        'forges': Forge.objects.all(),
        'namespaces': Namespace.objects.all(),
        'projects': Project.objects.all(),
    })

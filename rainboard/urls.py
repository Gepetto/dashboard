from django.urls import path

from django.views.generic import ListView

from .models import Forge, Namespace, Project
from . import views

app_name = 'cine'
urlpatterns = [
    path(r'', views.home, name='home'),
    path(r'forges', ListView.as_view(model=Forge), name='forges'),
    path(r'namespaces', ListView.as_view(model=Namespace), name='namespaces'),
    path(r'projects', ListView.as_view(model=Project), name='projects'),
]

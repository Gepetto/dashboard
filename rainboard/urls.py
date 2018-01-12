from django.urls import path
from django.views.generic import ListView

from . import views
from .models import Forge, Namespace, Project

app_name = 'rainboard'
urlpatterns = [
    # path(r'', views.home, name='home'),
    path(r'', views.ProjectsView.as_view(), name='home'),
    path(r'forges', ListView.as_view(model=Forge), name='forges'),
    path(r'namespaces', ListView.as_view(model=Namespace), name='namespaces'),
    path(r'projects', ListView.as_view(model=Project), name='projects'),
    path(r'project/<str:slug>', views.ProjectView.as_view(), name='project'),
]

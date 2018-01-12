from django.urls import path
from django.views.generic import ListView

from . import views
from .models import Forge, Namespace, Project

app_name = 'rainboard'
urlpatterns = [
    path('', views.ProjectsView.as_view(), name='home'),
    path('forges', views.ForgesView.as_view(), name='forges'),
    path('namespaces', views.NamespacesView.as_view(), name='namespaces'),
    path('project/<str:slug>', views.ProjectView.as_view(), name='project'),
]

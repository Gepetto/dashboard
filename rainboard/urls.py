from django.urls import path
from django.views.generic import ListView, RedirectView

from . import views
from .models import Forge, Namespace, Project, Article

app_name = 'rainboard'
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='rainboard:projects'), name='home'),
    path('forges', views.ForgesView.as_view(), name='forges'),
    path('articles', views.ArticlesView.as_view(), name='articles'),
    path('article/create', views.ArticleCreateView.as_view(), name='article-new'),
    path('namespaces', views.NamespacesView.as_view(), name='namespaces'),
    path('projects', views.ProjectsView.as_view(), name='projects'),
    path('project/<str:slug>', views.ProjectView.as_view(), name='project'),
]

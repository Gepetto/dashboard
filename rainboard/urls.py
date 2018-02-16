from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = 'rainboard'
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='rainboard:projects'), name='home'),
    path('forges', views.ForgesView.as_view(), name='forges'),
    path('articles', views.ArticlesView.as_view(), name='articles'),
    path('article/create', views.ArticleCreateView.as_view(), name='article-new'),
    path('namespaces', views.NamespacesView.as_view(), name='namespaces'),
    path('contributors', views.ContributorsView.as_view(), name='contributors'),
    path('projects', views.ProjectsView.as_view(), name='projects'),
    path('project/<str:slug>/robotpkg', views.ProjectView.as_view(), name='project'),
    path('project/<str:slug>/repos', views.ProjectReposView.as_view(), name='project-repos'),
    path('project/<str:slug>/branches', views.ProjectBranchesView.as_view(), name='project-branches'),
    path('project/<str:slug>/images', views.ProjectImagesView.as_view(), name='project-images'),
    path('project/<str:slug>/contributors', views.ProjectContributorsView.as_view(), name='project-contributors'),
]

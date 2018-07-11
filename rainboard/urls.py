from django.urls import path
from django.views.generic import RedirectView, TemplateView

from . import views

app_name = 'rainboard'
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='rainboard:projects'), name='home'),
    path('forges', views.ForgesView.as_view(), name='forges'),
    path('namespaces', views.NamespacesView.as_view(), name='namespaces'),
    path('contributors', views.ContributorsView.as_view(), name='contributors'),
    path('projects', views.ProjectsView.as_view(), name='projects'),
    path('projects/gepetto', views.GepettoProjectsView.as_view(), name='gepetto'),
    path('project/<str:slug>/robotpkg', views.ProjectView.as_view(), name='project'),
    path('project/<str:slug>/repos', views.ProjectReposView.as_view(), name='project-repos'),
    path('project/<str:slug>/branches', views.ProjectBranchesView.as_view(), name='project-branches'),
    path('project/<str:slug>/images', views.ProjectImagesView.as_view(), name='project-images'),
    path('project/<str:slug>/contributors', views.ProjectContributorsView.as_view(), name='project-contributors'),
    path('project/<str:slug>/.gitlab-ci.yml', views.ProjectGitlabView.as_view(), name='project-gitlab'),
    path('doc', views.json_doc, name='doc'),
    path('docker', views.docker, name='docker'),
    path('graph.svg', views.graph_svg, name='graph_svg'),
    path('graph', TemplateView.as_view(template_name='rainboard/graph.html'), name='graph'),
]

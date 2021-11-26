from django.urls import include, path
from django.views.generic import RedirectView, TemplateView
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'namespace', views.NamespaceViewSet)
router.register(r'license', views.LicenseViewSet)
router.register(r'forge', views.ForgeViewSet)
router.register(r'project', views.ProjectViewSet)
router.register(r'repo', views.RepoViewSet)
router.register(r'branch', views.BranchViewSet)
router.register(r'target', views.TargetViewSet)
router.register(r'robotpkg', views.RobotpkgViewSet)
router.register(r'image', views.ImageViewSet)
router.register(r'contributor', views.ContributorViewSet)
router.register(r'contributorName', views.ContributorNameViewSet)
router.register(r'contributorMail', views.ContributorMailViewSet)
router.register(r'dependency', views.DependencyViewSet)

app_name = 'rainboard'
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='rainboard:gepetto'), name='home'),
    path('forges', views.ForgesView.as_view(), name='forges'),
    path('namespaces', views.NamespacesView.as_view(), name='namespaces'),
    path('contributors', views.ContributorsView.as_view(), name='contributors'),
    path('projects', views.ProjectsView.as_view(), name='projects'),
    path('projects/gepetto', views.GepettoProjectsView.as_view(), name='gepetto'),
    path('projects/ordered', views.ordered_projects, name='ordered'),
    path('project/<str:slug>', RedirectView.as_view(pattern_name='rainboard:project'), name='project_redirect'),
    path('project/<str:slug>/robotpkg', views.ProjectView.as_view(), name='project'),
    path('project/<str:slug>/repos', views.ProjectReposView.as_view(), name='project-repos'),
    path('project/<str:slug>/branches', views.ProjectBranchesView.as_view(), name='project-branches'),
    path('project/<str:slug>/images', views.ProjectImagesView.as_view(), name='project-images'),
    path('project/<str:slug>/contributors', views.ProjectContributorsView.as_view(), name='project-contributors'),
    path('project/<str:slug>/.gitlab-ci.yml', views.ProjectGitlabView.as_view(), name='project-gitlab'),
    path('issues', views.IssuesPrView.as_view(), name='issues_pr'),
    path('issues/update', views.update_issues_pr, name='update_issues_pr'),
    path('doc', views.json_doc, name='doc'),
    path('images', views.images_list, name='images'),
    path('docker', views.docker, name='docker'),
    path('graph.svg', views.graph_svg, name='graph_svg'),
    path('graph', TemplateView.as_view(template_name='rainboard/graph.html'), name='graph'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('favicon.ico', views.nope, name='nope'),
    path('<str:slug>', RedirectView.as_view(pattern_name='rainboard:project'), name='direct_redirect'),
]

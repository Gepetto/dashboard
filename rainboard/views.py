from subprocess import PIPE, run

from django.http import Http404
from django.http.response import HttpResponse, JsonResponse
from django.views.generic import DetailView

from django_filters.views import FilterView
from django_tables2 import RequestConfig
from django_tables2.views import SingleTableMixin, SingleTableView
from rest_framework import permissions, viewsets

from . import filters, models, serializers, tables


def nope(request):
    raise Http404('not found')


class ForgesView(SingleTableView):
    model = models.Forge
    table_class = tables.ForgeTable


class NamespacesView(SingleTableView):
    model = models.Namespace
    table_class = tables.NamespaceTable


class ProjectsView(SingleTableMixin, FilterView):
    model = models.Project
    table_class = tables.ProjectTable
    filterset_class = filters.ProjectFilter
    strict = False


class GepettoProjectsView(ProjectsView):
    queryset = models.Project.objects.filter(from_gepetto=True, archived=False)


class ProjectView(DetailView):
    model = models.Project


class ProjectTableView(ProjectView):
    order_by = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        object_list = self.get_object_list()
        table = self.table_class(object_list, order_by=self.order_by)
        RequestConfig(self.request).configure(table)
        ctx.update(table=table, object_list=object_list)
        return ctx


class ProjectReposView(ProjectTableView):
    table_class = tables.RepoTable

    def get_object_list(self):
        return self.object.repo_set.all()


class ProjectBranchesView(ProjectTableView):
    table_class = tables.BranchTable
    order_by = '-updated'

    def get_object_list(self):
        return self.object.branch_set.all()


class ProjectImagesView(ProjectTableView):
    table_class = tables.ImageTable
    order_by = 'target'

    def get_object_list(self):
        return models.Image.objects.filter(robotpkg__project=self.object, target__active=True)


class ProjectContributorsView(ProjectTableView):
    table_class = tables.ContributorTable

    def get_object_list(self):
        return self.object.contributors()


class ProjectGitlabView(ProjectView):
    template_name = 'rainboard/gitlab-ci.yml'
    content_type = 'application/x-yaml'


class DistinctMixin(object):
    def get_queryset(self):
        return super().get_queryset().distinct()


class ContributorsView(SingleTableMixin, DistinctMixin, FilterView):
    queryset = models.Contributor.objects.gepettist()
    table_class = tables.ContributorProjectTable
    filterset_class = filters.ContributorFilter
    strict = False


def json_doc(request):
    """
    Get the list of project / namespace / branch of which we want to keep the doc
    """
    return JsonResponse({
        'ret': [(b.project.slug, b.repo.namespace.slug, b.name.split('/', maxsplit=2)[2])
                for b in models.Branch.objects.filter(keep_doc=True)]
    })


def docker(request):
    cmd = 'build'
    filters = request.GET.dict()
    if 'cmd' in filters and filters['cmd'] in ['push', 'pull', 'build']:
        cmd = filters.pop('cmd')
    images = models.Image.objects.filter(target__active=True).filter(**filters)
    return HttpResponse('\n'.join([' '.join(getattr(image, cmd)()) for image in images]), content_type="text/plain")


def graph_svg(request):
    with open('/tmp/graph', 'w') as f:
        print('digraph { rankdir=LR;', file=f)
        for project in models.Project.objects.filter(from_gepetto=True, archived=False):
            print(f'{{I{project.pk} [label="{project}" URL="{project.get_absolute_url()}"];}}', file=f)
        for dep in models.Dependency.objects.filter(project__from_gepetto=True,
                                                    library__from_gepetto=True,
                                                    project__archived=False,
                                                    library__archived=False):
            print(f'I{dep.library.pk} -> I{dep.project.pk};', file=f)
        print('}', file=f)
    svg = run(['dot', '/tmp/graph', '-Tsvg'], stdout=PIPE).stdout.decode()
    return HttpResponse(svg, content_type='image/svg+xml')


def ordered_projects(request):
    return JsonResponse(models.ordered_projects)


class AuthenticatedOrReadOnlyModelViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


class NamespaceViewSet(AuthenticatedOrReadOnlyModelViewSet):
    queryset = models.Namespace.objects.all()
    serializer_class = serializers.NamespaceSerializer
    filterset_fields = ('name', 'slug')


class LicenseViewSet(AuthenticatedOrReadOnlyModelViewSet):
    queryset = models.License.objects.all()
    serializer_class = serializers.LicenseSerializer
    filterset_fields = ('name', 'spdx_id')


class ForgeViewSet(AuthenticatedOrReadOnlyModelViewSet):
    queryset = models.Forge.objects.all()
    serializer_class = serializers.ForgeSerializer
    filterset_fields = ('name', 'slug')


class ProjectViewSet(AuthenticatedOrReadOnlyModelViewSet):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    filterset_class = filters.ProjectFilter


class RepoViewSet(AuthenticatedOrReadOnlyModelViewSet):
    queryset = models.Repo.objects.all()
    serializer_class = serializers.RepoSerializer
    filterset_fields = ('name', 'slug')


class BranchViewSet(AuthenticatedOrReadOnlyModelViewSet):
    queryset = models.Branch.objects.all()
    serializer_class = serializers.BranchSerializer


class TargetViewSet(AuthenticatedOrReadOnlyModelViewSet):
    queryset = models.Target.objects.active()
    serializer_class = serializers.TargetSerializer
    filterset_fields = ('name', 'slug')


class RobotpkgViewSet(AuthenticatedOrReadOnlyModelViewSet):
    queryset = models.Robotpkg.objects.all()
    serializer_class = serializers.RobotpkgSerializer
    filterset_fields = ('name', 'slug')


class ImageViewSet(AuthenticatedOrReadOnlyModelViewSet):
    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer


class ContributorViewSet(AuthenticatedOrReadOnlyModelViewSet):
    queryset = models.Contributor.objects.all()
    serializer_class = serializers.ContributorSerializer
    filterset_class = filters.ContributorFilter


class ContributorNameViewSet(AuthenticatedOrReadOnlyModelViewSet):
    queryset = models.ContributorName.objects.all()
    serializer_class = serializers.ContributorNameSerializer


class ContributorMailViewSet(AuthenticatedOrReadOnlyModelViewSet):
    queryset = models.ContributorMail.objects.all()
    serializer_class = serializers.ContributorMailSerializer


class DependencyViewSet(AuthenticatedOrReadOnlyModelViewSet):
    queryset = models.Dependency.objects.all()
    serializer_class = serializers.DependencySerializer

from django.views.generic import CreateView, DetailView

from django_filters.views import FilterView
from django_tables2 import RequestConfig
from django_tables2.views import SingleTableMixin, SingleTableView

from . import models, tables, filters


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
        return models.Image.objects.filter(robotpkg__project=self.object)


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
    model = models.Contributor
    table_class = tables.ContributorProjectTable
    filterset_class = filters.ContributorFilter

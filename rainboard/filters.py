import django_filters

from . import models


class ProjectFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = models.Project
        fields = ('name',)


class ContributorFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='contributorname__name', label='name', lookup_expr='icontains')
    mail = django_filters.CharFilter(field_name='contributormail__mail', label='mail', lookup_expr='icontains')
    project = django_filters.CharFilter(field_name='projects__name', label='project', lookup_expr='icontains')

    class Meta:
        model = models.Contributor
        fields = ('name', 'mail', 'project')

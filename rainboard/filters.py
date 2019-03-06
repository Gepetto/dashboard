import django_filters

from . import models, utils


def filter_valid_name(queryset, name, value):
    return queryset.filter(**{f'{name}__icontains': utils.valid_name(value)})


class ProjectFilter(django_filters.rest_framework.FilterSet):
    name = django_filters.CharFilter(method=filter_valid_name)

    class Meta:
        model = models.Project
        fields = ('name', 'from_gepetto', 'archived')


class ContributorFilter(django_filters.rest_framework.FilterSet):
    name = django_filters.CharFilter(field_name='contributorname__name', label='name', lookup_expr='icontains')
    mail = django_filters.CharFilter(field_name='contributormail__mail', label='mail', lookup_expr='icontains')
    project = django_filters.CharFilter(field_name='projects__name', label='project', lookup_expr='icontains')

    class Meta:
        model = models.Contributor
        fields = ('name', 'mail', 'project')

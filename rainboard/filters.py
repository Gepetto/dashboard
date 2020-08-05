import django_filters

from . import models, utils
from .models import Namespace, GEPETTO_SLUGS


def filter_valid_name(queryset, name, value):
    return queryset.filter(**{f'{name}__icontains': utils.valid_name(value)})


class ProjectFilter(django_filters.rest_framework.FilterSet):
    name = django_filters.CharFilter(method=filter_valid_name)

    class Meta:
        model = models.Project
        fields = ('name', 'main_namespace__from_gepetto', 'archived')


class IssuePrFilter(django_filters.rest_framework.FilterSet):
    namespace = django_filters.ModelChoiceFilter(queryset=Namespace.objects.filter(slug__in=GEPETTO_SLUGS),
                                                 field_name='repo__namespace',
                                                 label='namespace')
    name = django_filters.CharFilter(field_name='repo__project__name', label='name', lookup_expr='icontains')

    class Meta:
        model = models.IssuePr
        fields = ('name', 'namespace', 'is_issue')


class ContributorFilter(django_filters.rest_framework.FilterSet):
    name = django_filters.CharFilter(field_name='contributorname__name', label='name', lookup_expr='icontains')
    mail = django_filters.CharFilter(field_name='contributormail__mail', label='mail', lookup_expr='icontains')
    project = django_filters.CharFilter(field_name='projects__name', label='project', lookup_expr='icontains')

    class Meta:
        model = models.Contributor
        fields = ('name', 'mail', 'project')

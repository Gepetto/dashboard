from ipaddress import ip_address, ip_network

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden

from rest_framework import permissions


def ip_laas(request: HttpRequest) -> bool:
    forwarded_for = ip_address(request.META.get('HTTP_X_FORWARDED_FOR'))
    for net in settings.LAAS_NETWORKS:
        print(forwarded_for, 'in', ip_network(net))
    return any(forwarded_for in ip_network(net) for net in settings.LAAS_NETWORKS)


class LAASPermsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        print(request.path.startswith('/admin/'), 'or', request.path.startswith('/accounts/'), 'or', request.user,
              'and', request.user.is_authenticated, 'or', request.method, 'in', permissions.SAFE_METHODS, 'and',
              ip_laas(request))

        allowed = (request.path.startswith('/admin/') or request.path.startswith('/accounts/')
                   or request.user and request.user.is_authenticated
                   or request.method in permissions.SAFE_METHODS and ip_laas(request))
        print('allowed', allowed)

        return HttpResponseForbidden()

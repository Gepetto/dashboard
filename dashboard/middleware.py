import asyncio
from ipaddress import ip_address, ip_network

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import reverse
from django.utils.decorators import sync_and_async_middleware

from rest_framework import permissions

ALLOWED_URLS = ('admin', 'accounts', 'gh')


def ip_laas(request: HttpRequest) -> bool:
    """check if request comes from settings.LAAS_NETWORKS."""
    forwarded_for = ip_address(request.META.get('HTTP_X_FORWARDED_FOR').split(', ')[0])
    return any(forwarded_for in ip_network(net) for net in settings.LAAS_NETWORKS)


def allowed(request: HttpRequest) -> bool:
    """Allow access to pages protected at a higher application level,
    or if the user is authenticated,
    or if the request comes from a trusted IP.
    """
    return (any(request.path.startswith(f'/{url}/') for url in ALLOWED_URLS)
            or request.user and request.user.is_authenticated
            or request.method in permissions.SAFE_METHODS and ip_laas(request))


@sync_and_async_middleware
def laas_perms_middleware(get_response):
    # One-time configuration and initialization goes here.
    if asyncio.iscoroutinefunction(get_response):

        async def middleware(request) -> HttpResponse:
            if allowed(request):
                return await get_response(request)
            return HttpResponseRedirect(reverse('login'))
    else:

        def middleware(request) -> HttpResponse:
            if allowed(request):
                return get_response(request)
            return HttpResponseRedirect(reverse('login'))

    return middleware

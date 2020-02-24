"""Views for dashboard_apps."""
import hmac
from hashlib import sha1
from ipaddress import ip_address, ip_network

import requests
from django.conf import settings
from django.http import HttpRequest
from django.http.response import HttpResponse, HttpResponseForbidden, HttpResponseServerError
from django.utils.encoding import force_bytes
from django.views.decorators.csrf import csrf_exempt


def log(request: HttpRequest, rep: str = 'ok') -> HttpResponse:
    """Just print everything out."""
    print(f'{request = }')
    print(f'{request.scheme = }')
    print(f'{request.body = }')
    print(f'{request.path = }')
    print(f'{request.path_info = }')
    print(f'{request.method = }')
    print(f'{request.encoding = }')
    print(f'{request.content_type = }')
    print(f'{request.content_params = }')
    print(f'{request.GET = }')
    print(f'{request.POST = }')
    print(f'{request.COOKIES = }')
    print(f'{request.META = }')
    print(f'{request.headers = }')
    return HttpResponse(rep)


@csrf_exempt
def webhook(request: HttpRequest) -> HttpResponse:
    """
    Process request incoming from a github webhook.

    thx https://simpleisbetterthancomplex.com/tutorial/2016/10/31/how-to-handle-github-webhooks-using-django.html
    """
    # validate ip source
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    networks = requests.get('https://api.github.com/meta').json()['hooks']
    if any(ip_address(forwarded_for) in ip_network(net) for net in networks):
        print('from github IP')
    else:
        print('not from github IP')

    # validate signature
    signature = request.META.get('HTTP_X_HUB_SIGNATURE')
    if signature is None:
        print('no signature')
    else:
        algo, signature = signature.split('=')
        if algo != 'sha1':
            return HttpResponseServerError('I only speak sha1.', status=501)

        mac = hmac.new(force_bytes(settings.GITHUB_WEBHOOK_KEY), msg=force_bytes(request.body), digestmod=sha1)
        if not hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature)):
            return HttpResponseForbidden('wrong signature.')

    # process event
    event = request.META.get('HTTP_X_GITHUB_EVENT', 'ping')
    if event == 'ping':
        return log(request, 'pong')
    if event == 'push':
        return log(request, 'push event detected')

    return log(request, event)

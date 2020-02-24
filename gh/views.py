"""Views for dashboard_apps."""
import hmac
from hashlib import sha1
from ipaddress import ip_address, ip_network
from json import loads
from pprint import pprint

import requests
from autoslug.utils import slugify
from django.conf import settings
from django.http import HttpRequest
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseServerError
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes
from django.views.decorators.csrf import csrf_exempt

from rainboard.models import Namespace, Project

from . import models


def log(request: HttpRequest, rep: str = 'ok') -> HttpResponse:
    """Just print the body."""
    pprint(loads(request.body.decode()))
    return HttpResponse(rep)


def check_suite(request: HttpRequest, rep: str) -> HttpResponse:
    """Manage Github's check suites."""
    data = loads(request.body.decode())
    models.GithubCheckSuite.objects.get_or_create(id=data['check_suite']['id'])
    return HttpResponse(rep)


def push(request: HttpRequest, rep: str) -> HttpResponse:
    """Someone pushed on github. Synchronise current repo & gitlab."""
    data = loads(request.body.decode())
    namespace = get_object_or_404(Namespace, slug=slugify(data['repository']['owner']['name']))
    project = get_object_or_404(Project, main_namespace=namespace, slug=slugify(data['repository']['name']))
    ref_s = data['ref'][11:]  # strip 'refs/heads/'
    print(f'push detected on github: {ref_s}')
    gh_remote_s = f'github/{namespace.slug}'
    gl_remote_s = f'gitlab/{namespace.slug}'
    gh_ref_s = f'{gh_remote_s}/{ref_s}'
    gl_ref_s = f'{gl_remote_s}/{ref_s}'

    git_repo = project.git()
    gh_remote = git_repo.remotes[gh_remote_s]
    gh_remote.fetch()
    gh_ref = gh_remote.refs[ref_s]
    if str(gh_ref.commit) != data['after']:
        fail = f'push: wrong commit: {gh_ref.commit} vs {data["after"]}'
        print(fail)
        return HttpResponseBadRequest(fail)

    if gh_ref_s in git_repo.branches:
        git_repo.branches[gh_ref_s].commit = data['after']
    else:
        git_repo.create_head(gh_ref_s, commit=data['after'])
    if gl_ref_s in git_repo.branches:
        git_repo.branches[gl_ref_s].commit = data['after']
    else:
        git_repo.create_head(gl_ref_s, commit=data['after'])
    if ref_s in git_repo.branches:
        git_repo.branches[ref_s].commit = data['after']
    else:
        git_repo.create_head(ref_s, commit=data['after'])

    gl_remote = git_repo.remotes[gl_remote_s]
    gl_remote.fetch()
    gl_ref = gl_remote.refs[ref_s]
    if str(gl_ref.commit) != data['after']:
        print(f'pushing {data["after"]} on {ref_s} on gitlab')
        gl_remote.push(ref_s)

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
    if event == 'check_suite':
        return check_suite(request, 'check_suite event detected')

    return log(request, event)

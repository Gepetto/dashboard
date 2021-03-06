"""Views for dashboard_apps."""
import hmac
import logging
import re
import traceback
from hashlib import sha1
from ipaddress import ip_address, ip_network
from json import loads

from django.conf import settings
from django.core.mail import mail_admins
from django.http import HttpRequest
from django.http.response import (HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect,
                                  HttpResponseServerError)
from django.shortcuts import get_object_or_404, reverse
from django.utils.encoding import force_bytes
from django.views.decorators.csrf import csrf_exempt

import git
import github
from autoslug.utils import slugify
from dashboard.middleware import ip_laas
from rainboard.models import Namespace, Project
from rainboard.utils import SOURCES

from . import models

logger = logging.getLogger(__name__)


def check_suite(request: HttpRequest, rep: str) -> HttpResponse:
    """Manage Github's check suites."""
    data = loads(request.body.decode())
    slug = slugify(data['repository']['name'])

    if 'ros-release' in slug:  # Don't run check suites on ros-release repositories
        return HttpResponse(rep)

    models.GithubCheckSuite.objects.get_or_create(id=data['check_suite']['id'])
    return HttpResponse(rep)


def pull_request(request: HttpRequest, rep: str) -> HttpResponse:
    """Manage Github's Pull Requests."""
    data = loads(request.body.decode())
    event = data['action']
    branch = f'pr/{data["number"]}'
    login = slugify(data["pull_request"]["head"]["repo"]["owner"]["login"])

    namespace = get_object_or_404(Namespace, slug_github=slugify(data['repository']['owner']['login']))
    project = get_object_or_404(Project, main_namespace=namespace, slug=slugify(data['repository']['name']))
    git_repo = project.git()
    logger.debug(f'{namespace.slug}/{project.slug}: Pull request on {branch}: {event}')

    # Prevent pull requests on master when necessary
    if event in ['opened', 'reopened']:
        gh = project.github()
        pr = gh.get_pull(data["number"])
        pr_branch = pr.base.ref
        if not project.accept_pr_to_master and pr_branch == 'master' \
                and 'devel' in [b.name for b in gh.get_branches()] and login != namespace.slug_github:
            logger.info(f"{namespace.slug}/{project.slug}: New pr {data['number']} to master")
            pr.create_issue_comment("Hi ! This project doesn't usually accept pull requests on master. If this wasn't "
                                    "intentionnal, you can change the base branch of this pull request to devel "
                                    "(No need to close it for that). Best, a bot.")

    gh_remote_name = f'github/{login}'
    if gh_remote_name not in git_repo.remotes:
        remote = git_repo.create_remote(gh_remote_name, data["pull_request"]["head"]["repo"]["clone_url"])
    else:
        remote = git_repo.remote(gh_remote_name)

    # Sync the pull request with the pr/XX branch on Gitlab
    if event in ['opened', 'reopened', 'synchronize']:
        remote.fetch()
        commit = data['pull_request']['head']['sha']

        # Update branch to the latest commit
        if branch in git_repo.branches:
            git_repo.heads[branch].commit = commit
        else:
            git_repo.create_head(branch, commit=commit)

        # Create a gitlab remote if it doesn't exist
        gl_remote_name = f'gitlab/{namespace.slug}'
        if gl_remote_name not in git_repo.remotes:
            git_repo.create_remote(gl_remote_name, url=project.remote_url_gitlab())

        # Push the changes to gitlab
        logger.info(f'{namespace.slug}/{project.slug}: Pushing {commit} on {branch} on gitlab')
        try:
            git_repo.git.push(gl_remote_name, branch)
        except git.exc.GitCommandError:
            logger.warning(f'{namespace.slug}/{project.slug}: Failed to push on {branch} on gitlab, force pushing ...')
            git_repo.git.push(gl_remote_name, branch, force=True)

    # The pull request was closed, delete the branch pr/XX on Gitlab
    elif event == 'closed':
        if branch in git_repo.branches:
            git_repo.delete_head(branch, force=True)
            git_repo.delete_remote(gh_remote_name)
        project.gitlab().branches.delete(branch)
        logger.info(f'{namespace.slug}/{project.slug}: Deleted branch {branch}')

    return HttpResponse(rep)


def push(request: HttpRequest, source: SOURCES, rep: str) -> HttpResponse:
    """Someone pushed on github or gitlab. Synchronise local & remote repos."""
    data = loads(request.body.decode())
    slug = slugify(data['repository']['name'])

    if 'ros-release' in slug:  # Don't sync ros-release repositories
        return HttpResponse(rep)

    if source == SOURCES.gitlab:
        namespace = get_object_or_404(Namespace,
                                      slug_gitlab=slugify(data['project']['path_with_namespace'].split('/')[0]))
    else:
        namespace = get_object_or_404(Namespace, slug_github=slugify(data['repository']['owner']['login']))

    project = get_object_or_404(Project, main_namespace=namespace, slug=slug)

    branch = data['ref'][11:]  # strip 'refs/heads/'
    commit = data['after']
    gl_remote_name = f'gitlab/{namespace.slug}'
    gh_remote_name = f'github/{namespace.slug}'
    git_repo = project.git()
    logger.debug(f'{namespace.slug}/{slug}: Push detected on {source.name} {branch} (commit {commit})')

    if branch.startswith('pr/'):  # Don't sync pr/XX branches here, they are already handled by pull_request()
        return HttpResponse(rep)

    if branch.startswith('release/'):  # Don't sync release/X.Y.Z branches at all
        return HttpResponse(rep)

    # Fetch the latest commit from gitlab
    if gl_remote_name in git_repo.remotes:
        gl_remote = git_repo.remote(gl_remote_name)
    else:
        gl_remote = git_repo.create_remote(gl_remote_name, url=project.remote_url_gitlab())
    gl_remote.fetch()

    # Fetch the latest commit from github
    if gh_remote_name in git_repo.remotes:
        gh_remote = git_repo.remote(gh_remote_name)
    else:
        gh_remote = git_repo.create_remote(gh_remote_name, url=project.remote_url_github())
    gh_remote.fetch()

    # The branch was deleted on one remote, delete the branch on the other remote as well
    if commit == "0000000000000000000000000000000000000000":
        if branch in git_repo.branches:
            git_repo.delete_head(branch, force=True)
            if source == SOURCES.gitlab:
                project.github().get_git_ref(f'heads/{branch}').delete()
            else:
                project.gitlab().branches.delete(branch)
            logger.info(f'{namespace.slug}/{slug}: Deleted branch {branch}')
        return HttpResponse(rep)

    # Make sure we fetched the latest commit
    ref = gl_remote.refs[branch] if source == SOURCES.gitlab else gh_remote.refs[branch]
    if str(ref.commit) != commit:
        fail = f'Push: wrong commit: {ref.commit} vs {commit}'
        logger.error(f'{namespace.slug}/{slug}: ' + fail)
        return HttpResponseBadRequest(fail)

    # Update the branch to the latest commit
    if branch in git_repo.branches:
        git_repo.heads[branch].commit = commit
    else:
        git_repo.create_head(branch, commit=commit)

    # Push the changes to other remote
    try:
        if source == SOURCES.gitlab and (branch not in gh_remote.refs or str(gh_remote.refs[branch].commit) != commit):
            logger.info(f'{namespace.slug}/{slug}: Pushing {commit} on {branch} on github')
            git_repo.git.push(gh_remote_name, branch)
        elif branch not in gl_remote.refs or str(gl_remote.refs[branch].commit) != commit:
            logger.info(f'{namespace.slug}/{slug}: Pushing {commit} on {branch} on gitlab')
            git_repo.git.push(gl_remote_name, branch)
        else:
            return HttpResponse('already synced')
    except git.exc.GitCommandError:
        # Probably failed because of a force push
        logger.exception(f'{namespace.slug}/{slug}: Forge sync failed')
        message = traceback.format_exc()
        message = re.sub(r'://.*@', '://[REDACTED]@', message)  # Hide access tokens in the mail
        mail_admins(f'Forge sync failed for {namespace.slug}/{slug}', message)

    return HttpResponse(rep)


def pipeline(request: HttpRequest, rep: str) -> HttpResponse:
    """Something happened on a Gitlab pipeline. Tell Github if necessary."""
    data = loads(request.body.decode())
    branch, commit, gl_status, pipeline_id = (data['object_attributes'][key] for key in ['ref', 'sha', 'status', 'id'])
    namespace = get_object_or_404(Namespace, slug_gitlab=slugify(data['project']['path_with_namespace'].split('/')[0]))
    project = get_object_or_404(Project, main_namespace=namespace, slug=slugify(data['project']['name']))
    gh_repo = project.github()
    ci_web_url = project.url_gitlab() + '/pipelines/' + str(pipeline_id)
    logger.debug(f'{namespace.slug}/{project.slug}: Pipeline #{pipeline_id} on commit {commit} for branch {branch}, '
                 f'status: {gl_status}')

    # Report the status to Github
    if gl_status in ['pending', 'success', 'failed']:
        gh_status = gl_status if gl_status != 'failed' else 'failure'
        if branch.startswith('pr/'):
            gh_repo.get_commit(sha=commit).create_status(state=gh_status, target_url=ci_web_url, context='gitlab-ci')
        else:
            try:
                gh_commit = gh_repo.get_branch(branch).commit
                gh_commit.create_status(state=gh_status, target_url=ci_web_url, context='gitlab-ci')
            except github.GithubException as e:
                if e.status == 404:
                    # Happens when a new branch is created on gitlab and the pipeline event comes before the push event
                    logger.warning(f"Branch {branch} does not exist on github, unable to report the pipeline status.")
                else:
                    raise

    return HttpResponse(rep)


@csrf_exempt
def webhook(request: HttpRequest) -> HttpResponse:
    """
    Process request incoming from a github webhook.

    thx https://simpleisbetterthancomplex.com/tutorial/2016/10/31/how-to-handle-github-webhooks-using-django.html
    """
    # validate ip source
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR').split(', ')[0]
    # networks = httpx.get('https://api.github.com/meta').json()['hooks'] # Fails if API rate limit exceeded
    networks = ['185.199.108.0/22', '140.82.112.0/20']
    if not any(ip_address(forwarded_for) in ip_network(net) for net in networks):
        logger.warning('not from github IP')
        return HttpResponseRedirect(reverse('login'))

    # validate signature
    signature = request.META.get('HTTP_X_HUB_SIGNATURE')
    if signature is None:
        logger.warning('no signature')
        return HttpResponseRedirect(reverse('login'))
    algo, signature = signature.split('=')
    if algo != 'sha1':
        logger.warning('signature not sha-1')
        return HttpResponseServerError('I only speak sha1.', status=501)

    mac = hmac.new(force_bytes(settings.GITHUB_WEBHOOK_KEY), msg=force_bytes(request.body), digestmod=sha1)
    if not hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature)):
        logger.warning('wrong signature')
        return HttpResponseForbidden('wrong signature.')

    # process event
    event = request.META.get('HTTP_X_GITHUB_EVENT', 'ping')
    if event == 'ping':
        return HttpResponse('pong')
    if event == 'push':
        return push(request, SOURCES.github, 'push event detected')
    if event == 'check_suite':
        return check_suite(request, 'check_suite event detected')
    if event == 'pull_request':
        return pull_request(request, 'pull_request event detected')

    return HttpResponseForbidden('event not found')


@csrf_exempt
def gl_webhook(request: HttpRequest) -> HttpResponse:
    """Process request incoming from a gitlab webhook."""

    # validate ip source
    if not ip_laas(request):
        logger.warning('not from LAAS IP')
        return HttpResponseRedirect(reverse('login'))

    # validate token
    token = request.META.get('HTTP_X_GITLAB_TOKEN')
    if token is None:
        logger.warning('no token')
        return HttpResponseRedirect(reverse('login'))
    if token != settings.GITLAB_WEBHOOK_KEY:
        logger.warning('wrong token')
        return HttpResponseForbidden('wrong token.')

    event = request.META.get('HTTP_X_GITLAB_EVENT')
    if event == 'ping':
        return HttpResponse('pong')
    elif event == 'Pipeline Hook':
        return pipeline(request, 'pipeline event detected')
    elif event == 'Push Hook':
        return push(request, SOURCES.gitlab, 'push event detected')

    return HttpResponseForbidden('event not found')

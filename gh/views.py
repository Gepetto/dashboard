"""Views for dashboard_apps."""

import hmac
import logging
import re
import traceback
from hashlib import sha1
from ipaddress import ip_address, ip_network
from json import loads

import git
import github
from asgiref.sync import async_to_sync, sync_to_async
from autoslug.utils import slugify
from django.conf import settings
from django.core.mail import mail_admins
from django.http import HttpRequest
from django.http.response import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseRedirect,
    HttpResponseServerError,
)
from django.shortcuts import get_object_or_404, reverse
from django.utils.encoding import force_bytes
from django.views.decorators.csrf import csrf_exempt
from gitlab import GitlabDeleteError

from dashboard.middleware import ip_laas
from rainboard.models import Namespace, Project
from rainboard.utils import SOURCES

from . import models

logger = logging.getLogger(__name__)

PR_MASTER_MSG = (
    "Hi ! This project doesn't usually accept pull requests on the main branch.\n"
    "If this wasn't intentionnal, you can change the base branch of this PR to devel\n"
    "(No need to close it for that). Best, a bot."
)


async def check_suite(request: HttpRequest, rep: str) -> HttpResponse:
    """Manage Github's check suites."""
    data = loads(request.body.decode())
    slug = slugify(data["repository"]["name"])

    if "ros-release" in slug:  # Don't run check suites on ros-release repositories
        return HttpResponse(rep)

    await models.GithubCheckSuite.objects.aget_or_create(id=data["check_suite"]["id"])
    return HttpResponse(rep)


async def pull_request(request: HttpRequest, rep: str) -> HttpResponse:
    """Manage Github's Pull Requests."""
    logger.info("process gh pr")
    data = loads(request.body.decode())
    event = data["action"]
    branch = f'pr/{data["number"]}'
    login = slugify(data["pull_request"]["head"]["repo"]["owner"]["login"])

    namespace = await sync_to_async(get_object_or_404)(
        Namespace,
        slug_github=slugify(data["repository"]["owner"]["login"]),
    )
    project = await sync_to_async(get_object_or_404)(
        Project,
        main_namespace=namespace,
        slug=slugify(data["repository"]["name"]).replace("_", "-"),
    )
    git_repo = await sync_to_async(project.git)()
    logger.debug(
        "%s/%s: Pull request on %s: %s",
        namespace.slug,
        project.slug,
        branch,
        event,
    )

    # Prevent pull requests on master when necessary
    if event in ["opened", "reopened"]:
        gh = await sync_to_async(project.github)()
        pr = await sync_to_async(gh.get_pull)(data["number"])
        pr_branch = pr.base.ref
        branches = [b.name for b in await sync_to_async(gh.get_branches)()]
        if (
            not project.accept_pr_to_master
            and pr_branch in ["master", "main"]
            and "devel" in branches
            and login != namespace.slug_github
        ):
            logger.info(
                "%s/%s: New pr %s to master",
                namespace.slug,
                project.slug,
                data["number"],
            )
            await sync_to_async(pr.create_issue_comment)(PR_MASTER_MSG)

    gh_remote_name = f"github/{login}"
    if gh_remote_name not in git_repo.remotes:
        remote = await sync_to_async(git_repo.create_remote)(
            gh_remote_name,
            data["pull_request"]["head"]["repo"]["clone_url"],
        )
    else:
        remote = await sync_to_async(git_repo.remote)(gh_remote_name)

    # Sync the pull request with the pr/XX branch on Gitlab
    if event in ["opened", "reopened", "synchronize"]:
        remote.fetch()
        commit = data["pull_request"]["head"]["sha"]

        # Update branch to the latest commit
        if branch in git_repo.branches:
            git_repo.heads[branch].commit = commit
        else:
            await sync_to_async(git_repo.create_head)(branch, commit=commit)

        # Create a gitlab remote if it doesn't exist
        gl_remote_name = f"gitlab/{namespace.slug}"
        if gl_remote_name not in git_repo.remotes:
            url = await sync_to_async(project.remote_url_gitlab)()
            await sync_to_async(git_repo.create_remote)(gl_remote_name, url=url)

        await models.PushQueue.objects.acreate(
            namespace=namespace,
            project=project,
            gl_remote_name=gl_remote_name,
            branch=branch,
        )

    # The pull request was closed, delete the branch pr/XX on Gitlab
    elif event == "closed":
        if branch in git_repo.branches:
            git_repo.delete_head(branch, force=True)
            git_repo.delete_remote(gh_remote_name)
        gitlab = await sync_to_async(project.gitlab)()
        try:
            await sync_to_async(gitlab.branches.delete)(branch)
            logger.info(
                "%s/%s: Deleted branch %s",
                namespace.slug,
                project.slug,
                branch,
            )
        except GitlabDeleteError as e:
            logger.info(
                "%s/%s: branch %s not delete: %s",
                namespace.slug,
                project.slug,
                branch,
                e,
            )

    return HttpResponse(rep)


async def push(  # noqa: C901
    request: HttpRequest,
    source: SOURCES,
    rep: str,
) -> HttpResponse:
    """Someone pushed on github or gitlab. Synchronise local & remote repos."""
    data = loads(request.body.decode())
    slug = slugify(data["repository"]["name"])

    if "ros-release" in slug:  # Don't sync ros-release repositories
        return HttpResponse(rep)

    if source == SOURCES.gitlab:
        namespace = await sync_to_async(get_object_or_404)(
            Namespace,
            slug_gitlab=slugify(data["project"]["path_with_namespace"].split("/")[0]),
        )
    else:
        namespace = await sync_to_async(get_object_or_404)(
            Namespace,
            slug_github=slugify(data["repository"]["owner"]["login"]),
        )

    project = await sync_to_async(get_object_or_404)(
        Project,
        main_namespace=namespace,
        slug=slug,
    )

    branch = data["ref"][11:]  # strip 'refs/heads/'
    commit = data["after"]
    gl_remote_name = f"gitlab/{namespace.slug}"
    gh_remote_name = f"github/{namespace.slug}"
    git_repo = await sync_to_async(project.git)()
    logger.debug(
        "%s/%s: Push detected on %s %s (commit %s)",
        namespace.slug,
        slug,
        source.name,
        branch,
        commit,
    )

    if branch.startswith(
        "pr/",
    ):  # Don't sync pr/XX branches here, they are already handled by pull_request()
        return HttpResponse(rep)

    if branch.startswith("release/"):  # Don't sync release/X.Y.Z branches at all
        return HttpResponse(rep)

    if branch.startswith("pre-commit-ci-update-config"):  # Don't sync neither
        return HttpResponse(rep)

    # Fetch the latest commit from gitlab
    if gl_remote_name in git_repo.remotes:
        gl_remote = await sync_to_async(git_repo.remote)(gl_remote_name)
    else:
        url = await sync_to_async(project.remote_url_gitlab)()
        gl_remote = await sync_to_async(git_repo.create_remote)(gl_remote_name, url=url)
    gl_remote.fetch()

    # Fetch the latest commit from github
    if gh_remote_name in git_repo.remotes:
        gh_remote = await sync_to_async(git_repo.remote)(gh_remote_name)
    else:
        url = await sync_to_async(project.remote_url_github)()
        gh_remote = await sync_to_async(git_repo.create_remote)(gh_remote_name, url=url)
    gh_remote.fetch()

    # The branch was deleted on one remote,
    # delete the branch on the other remote as well
    if commit == "0000000000000000000000000000000000000000":
        if branch in git_repo.branches:
            git_repo.delete_head(branch, force=True)
            if source == SOURCES.gitlab:
                github = await sync_to_async(project.github)()
                github.get_git_ref(f"heads/{branch}").delete()
            else:
                gitlab = await sync_to_async(project.gitlab)()
                gitlab.branches.delete(branch)
            logger.info("%s/%s: Deleted branch %s", namespace.slug, slug, branch)
        return HttpResponse(rep)

    # Make sure we fetched the latest commit
    ref = gl_remote.refs[branch] if source == SOURCES.gitlab else gh_remote.refs[branch]
    if str(ref.commit) != commit:
        fail = f"Push: wrong commit: {ref.commit} vs {commit}"
        logger.error("%s/%s: %s", namespace.slug, slug, fail)
        return HttpResponseBadRequest(fail)

    # Update the branch to the latest commit
    if branch in git_repo.branches:
        git_repo.heads[branch].commit = commit
    else:
        await sync_to_async(git_repo.create_head)(branch, commit=commit)

    # Push the changes to other remote
    try:
        if source == SOURCES.gitlab and (
            branch not in gh_remote.refs or str(gh_remote.refs[branch].commit) != commit
        ):
            logger.info(
                "%s/%s: Pushing %s on %s on github",
                namespace.slug,
                slug,
                commit,
                branch,
            )
            await sync_to_async(git_repo.git.push)(gh_remote_name, branch)
        elif (
            branch not in gl_remote.refs or str(gl_remote.refs[branch].commit) != commit
        ):
            logger.info(
                "%s/%s: Pushing %s on %s on gitlab",
                namespace.slug,
                slug,
                commit,
                branch,
            )
            await sync_to_async(git_repo.git.push)(gl_remote_name, branch)
        else:
            return HttpResponse("already synced")
    except git.exc.GitCommandError:
        # Probably failed because of a force push
        logger.exception("%s/%s: Forge sync failed", namespace.slug, slug)
        message = traceback.format_exc()
        message = re.sub(
            r"://.*@",
            "://[REDACTED]@",
            message,
        )  # Hide access tokens in the mail
        await sync_to_async(mail_admins)(
            f"Forge sync failed for {namespace.slug}/{slug}",
            message,
        )

    return HttpResponse(rep)


async def pipeline(request: HttpRequest, rep: str) -> HttpResponse:
    """Something happened on a Gitlab pipeline. Tell Github if necessary."""
    data = loads(request.body.decode())
    branch, commit, gl_status, pipeline_id = (
        data["object_attributes"][key] for key in ["ref", "sha", "status", "id"]
    )
    namespace = await sync_to_async(get_object_or_404)(
        Namespace,
        slug_gitlab=slugify(data["project"]["path_with_namespace"].split("/")[0]),
    )
    project = await sync_to_async(get_object_or_404)(
        Project,
        main_namespace=namespace,
        slug=slugify(data["project"]["name"]),
    )
    gh_repo = await sync_to_async(project.github)()
    ci_web_url = f"{project.url_gitlab()}/-/pipelines/{pipeline_id}"
    logger.debug(
        "%s/%s: Pipeline #%s on commit %s for branch %s, status: %s",
        namespace.slug,
        project.slug,
        pipeline_id,
        commit,
        branch,
        gl_status,
    )

    # Report the status to Github
    if gl_status in ["pending", "success", "failed"]:
        gh_status = gl_status if gl_status != "failed" else "failure"
        if branch.startswith("pr/"):
            sha = await sync_to_async(gh_repo.get_commit)(sha=commit)
            await sync_to_async(sha.create_status)(
                state=gh_status,
                target_url=ci_web_url,
                context="gitlab-ci",
            )
        else:
            try:
                sha = await sync_to_async(gh_repo.get_branch)(branch)
                await sync_to_async(sha.commit.create_status)(
                    state=gh_status,
                    target_url=ci_web_url,
                    context="gitlab-ci",
                )
            except github.GithubException as e:
                if e.status == 404:
                    # Happens when a new branch is created on gitlab
                    # and the pipeline event comes before the push event
                    logger.warning(
                        "Branch %s does not exist on github, "
                        "unable to report the pipeline status.",
                        branch,
                    )
                else:
                    raise

    return HttpResponse(rep)


@sync_to_async
@csrf_exempt
@async_to_sync
async def webhook(request: HttpRequest) -> HttpResponse:
    """
    Process request incoming from a github webhook.

    thx https://simpleisbetterthancomplex.com/tutorial/2016/10/31/
    how-to-handle-github-webhooks-using-django.html
    """
    # validate ip source
    forwarded_for = request.headers.get("x-forwarded-for").split(", ")[0]
    # Fails if API rate limit exceeded
    # networks = httpx.get('https://api.github.com/meta').json()['hooks']
    networks = ["185.199.108.0/22", "140.82.112.0/20"]
    if not any(ip_address(forwarded_for) in ip_network(net) for net in networks):
        logger.warning("not from github IP")
        return HttpResponseRedirect(reverse("login"))

    # validate signature
    signature = request.headers.get("x-hub-signature")
    if signature is None:
        logger.warning("no signature")
        return HttpResponseRedirect(reverse("login"))
    algo, signature = signature.split("=")
    if algo != "sha1":
        logger.warning("signature not sha-1")
        return HttpResponseServerError("I only speak sha1.", status=501)

    mac = hmac.new(
        force_bytes(settings.GITHUB_WEBHOOK_KEY),
        msg=force_bytes(request.body),
        digestmod=sha1,
    )
    if not hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature)):
        logger.warning("wrong signature")
        return HttpResponseForbidden("wrong signature.")

    # process event
    event = request.headers.get("x-github-event", "ping")
    if event == "ping":
        return HttpResponse("pong")
    if event == "push":
        return await push(request, SOURCES.github, "push event detected")
    if event == "check_suite":
        return await check_suite(request, "check_suite event detected")
    if event == "pull_request":
        return await pull_request(request, "pull_request event detected")

    return HttpResponseForbidden("event not found")


@sync_to_async
@csrf_exempt
@async_to_sync
async def gl_webhook(request: HttpRequest) -> HttpResponse:
    """Process request incoming from a gitlab webhook."""

    # validate ip source
    if not ip_laas(request):
        logger.warning("not from LAAS IP")
        return HttpResponseRedirect(reverse("login"))

    # validate token
    token = request.headers.get("x-gitlab-token")
    if token is None:
        logger.warning("no token")
        return HttpResponseRedirect(reverse("login"))
    if token != settings.GITLAB_WEBHOOK_KEY:
        logger.warning("wrong token")
        return HttpResponseForbidden("wrong token.")

    event = request.headers.get("x-gitlab-event")
    if event == "ping":
        return HttpResponse("pong")
    if event == "Pipeline Hook":
        return await pipeline(request, "pipeline event detected")
    if event == "Push Hook":
        return await push(request, SOURCES.gitlab, "push event detected")

    return HttpResponseForbidden("event not found")

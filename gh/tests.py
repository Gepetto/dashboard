import hmac
import logging
import re
from asyncio import sleep
from hashlib import sha1

import git
from asgiref.sync import sync_to_async
from autoslug.utils import slugify
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes

from rainboard.models import Forge, Namespace, Project

from .models import PushQueue

LOGGER = logging.getLogger("dashboard.gh.tests")


def redact_token(func):
    """Decorator used to prevent git from leaking tokens in exception messages."""

    def wrapped_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except git.GitCommandError as e:
            e.stderr = re.sub(r"://.*@", "://[REDACTED]@", e.stderr)
            raise e

    return wrapped_function


class GhTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Run only once before the tests to avoid getting the objects in each test."""
        super().setUpClass()
        cls.namespace, _ = Namespace.objects.get_or_create(
            name="gsaurel",
            slug_gitlab=slugify("gsaurel"),
            slug_github=slugify("hrp2-14"),
        )
        cls.project, _ = Project.objects.get_or_create(
            name="rainboard-tests",
            main_namespace=Namespace.objects.get(name="gsaurel"),
            main_forge=Forge.objects.get(name="Gitlab"),
        )
        cls.github = cls.project.github()
        cls.gitlab = cls.project.gitlab()

        # Cleanup previous test
        for pr in cls.github.get_pulls(state="open"):
            pr.edit(state="closed")

        gh_branches = [b.name for b in cls.github.get_branches()]
        gl_branches = [b.name for b in cls.gitlab.branches.list()]
        for branch_name in gl_branches:
            if branch_name.startswith("pr/"):
                cls.gitlab.branches.delete(branch_name)

        for branch_name in ["test-branch-gitlab", "test-branch-github"]:
            if branch_name in gh_branches:
                cls.github.get_git_ref(f"heads/{branch_name}").delete()
            if branch_name in gl_branches:
                cls.gitlab.branches.delete(branch_name)

        LOGGER.info("start gh tests")

    def assertSync(self, branch):  # noqa: N802
        """Raise an exception if the branch is not synced between both repos."""
        last_commit_github = self.github.get_branch(branch).commit.sha
        last_commit_gitlab = (
            self.gitlab.commits.list(ref_name=branch, iterator=True).next().id
        )
        self.assertEqual(last_commit_github, last_commit_gitlab)

    @redact_token
    async def sync(self):
        """Force both repos to be synced."""
        for branch in ("master", "devel"):
            last_commit_github = self.github.get_branch(branch).commit.sha
            last_commit_gitlab = (
                self.gitlab.commits.list(
                    ref_name=branch,
                    iterator=True,
                )
                .next()
                .id
            )

            if last_commit_github != last_commit_gitlab:
                LOGGER.warning(
                    "sync: %s is not synced, force pushing commit %s on github",
                    branch,
                    last_commit_gitlab,
                )
                git_repo = self.project.git()

                # Create the remotes if necessary
                gl_remote_name = f"gitlab/{self.namespace.slug}"
                gh_remote_name = f"github/{self.namespace.slug}"
                if gl_remote_name not in git_repo.remotes:
                    git_repo.create_remote(
                        gl_remote_name,
                        url=await sync_to_async(self.project.remote_url_gitlab)(),
                    )
                if gh_remote_name not in git_repo.remotes:
                    git_repo.create_remote(
                        gh_remote_name,
                        url=await sync_to_async(self.project.remote_url_github)(),
                    )

                # Force push the latest gitlab commit on github
                git_repo.remote(gl_remote_name).fetch()
                git_repo.git.push(
                    "-f",
                    gh_remote_name,
                    f"{last_commit_gitlab}:{branch}",
                )

                self.assertSync(branch)

    @redact_token
    async def gh_webhook_event(
        self,
        event,
        last_commit="",
        branch="master",
        pr_action="",
        pr_number="",
        pr_login="",
    ):
        """Simulate receiving an event from a github webhook."""
        data = {
            "repository": {
                "name": self.project.slug,
                "owner": {"login": self.namespace.slug_github},
            },
            "ref": f"refs/heads/{branch}",
            "after": last_commit,
            "action": pr_action,
            "number": pr_number,
            "pull_request": {
                "head": {
                    "repo": {
                        "owner": {"login": pr_login},
                        "clone_url": await sync_to_async(
                            self.project.remote_url_github,
                        )(),
                    },
                    "sha": last_commit,
                },
            },
        }

        encoded_data = self.client._encode_json(
            {} if data is None else data,
            content_type="application/json",
        )
        request_body = self.client._encode_data(
            encoded_data,
            content_type="application/json",
        )
        msg = force_bytes(request_body)
        signature = (
            "sha1="
            + hmac.new(
                force_bytes(settings.GITHUB_WEBHOOK_KEY),
                msg,
                digestmod=sha1,
            ).hexdigest()
        )
        LOGGER.info("posting a simulated gh webhook event")
        return await self.async_client.post(
            reverse("webhook"),
            data,
            content_type="application/json",
            X_FORWARDED_FOR="140.82.112.1",
            X_HUB_SIGNATURE=signature,
            X_GITHUB_EVENT=event,
        )

    @redact_token
    async def gl_webhook_event(self, event, last_commit="", branch="master", status=""):
        """Simulate receiving an event from a gitlab webhook."""
        path_with_namespace = f"{self.namespace.slug_gitlab}/{self.project.slug}"
        data = {
            "repository": {
                "name": self.project.slug,
            },
            "project": {
                "name": self.project.slug,
                "path_with_namespace": path_with_namespace,
            },
            "ref": f"refs/heads/{branch}",
            "after": last_commit,
            "object_attributes": {
                "ref": branch,
                "sha": last_commit,
                "status": status,
                "id": 1,
            },
        }
        return await self.async_client.post(
            reverse("gl-webhook"),
            data,
            content_type="application/json",
            X_FORWARDED_FOR="140.93.0.1",
            X_GITLAB_TOKEN=settings.GITLAB_WEBHOOK_KEY,
            X_GITLAB_EVENT=event,
        )

    async def test_gh_webhook(self):
        """Test the security of the github webhook."""

        # Not from github IP
        response = await self.async_client.get(
            reverse("webhook"),
            X_FORWARDED_FOR="5.5.5.5",
        )
        self.assertEqual(response.status_code, 302)

        # No signature
        response = await self.async_client.get(
            reverse("webhook"),
            X_FORWARDED_FOR="140.82.112.1",
        )
        self.assertEqual(response.status_code, 302)

        # Signature not sha1
        response = await self.async_client.get(
            reverse("webhook"),
            X_FORWARDED_FOR="140.82.112.1",
            X_HUB_SIGNATURE="sha256=foo",
        )
        self.assertEqual(response.status_code, 501)

        # Wrong signature
        response = await self.async_client.get(
            reverse("webhook"),
            X_FORWARDED_FOR="140.82.112.1",
            X_HUB_SIGNATURE="sha1=foo",
        )
        self.assertEqual(response.status_code, 403)

        # Ping
        response = await self.gh_webhook_event("ping")
        self.assertEqual(response.status_code, 200)

    async def test_gl_webhook(self):
        """Test the security of the gitlab webhook."""

        # Not from gitlab IP
        response = await self.async_client.get(
            reverse("gl-webhook"),
            X_FORWARDED_FOR="5.5.5.5",
        )
        self.assertEqual(response.status_code, 302)

        # No token
        response = await self.async_client.get(
            reverse("gl-webhook"),
            X_FORWARDED_FOR="140.93.0.1",
        )
        self.assertEqual(response.status_code, 302)

        # Wrong token
        response = await self.async_client.get(
            reverse("gl-webhook"),
            X_FORWARDED_FOR="140.93.0.1",
            X_GITLAB_TOKEN="foo",
        )
        self.assertEqual(response.status_code, 403)

        # Ping
        response = await self.async_client.get(
            reverse("gl-webhook"),
            X_FORWARDED_FOR="140.93.0.1",
            X_GITLAB_TOKEN=settings.GITLAB_WEBHOOK_KEY,
            X_GITLAB_EVENT="ping",
        )
        self.assertEqual(response.status_code, 200)

    async def test_push_already_synced(self):
        """Test push when both repos are already synced."""
        await self.sync()

        last_commit = self.github.get_branch("master").commit.sha
        response = await self.gh_webhook_event("push", last_commit)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "already synced")

    async def push_github(self, branch):
        """Test sync after pushing to the given branch on github."""
        await self.sync()

        last_commit = self.github.get_branch(branch).commit.sha
        file = self.github.get_contents("README.md", branch)
        self.github.update_file(
            "README.md",
            message=f"Test push on github {branch}",
            content=last_commit[:8],
            sha=file.sha,
            branch=branch,
        )

        await sleep(5)
        async for q in PushQueue.objects.all():
            await sync_to_async(q.push)()

        last_commit_github = self.github.get_branch(branch).commit.sha
        self.assertNotEqual(last_commit, last_commit_github)

        response = await self.gh_webhook_event("push", last_commit_github, branch)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "push event detected")

        last_commit_gitlab = (
            self.gitlab.commits.list(ref_name=branch, iterator=True).next().id
        )
        self.assertEqual(last_commit_github, last_commit_gitlab)

    async def test_push_github_master(self):
        """Test sync after pushing to github on master."""
        await self.push_github("master")

    async def test_push_github_devel(self):
        """Test sync after pushing to github on devel."""
        await self.push_github("devel")

    async def push_gitlab(self, branch):
        """Test sync after pushing to the given branch on gitlab."""
        await self.sync()
        last_commit = self.gitlab.commits.list(ref_name=branch, iterator=True).next().id

        # Push a new commit to gitlab
        file = self.gitlab.files.get(file_path="README.md", ref=branch)
        file.content = last_commit[:8]
        file.save(branch=branch, commit_message=f"Test push on gitlab {branch}")

        last_commit_gitlab = (
            self.gitlab.commits.list(ref_name=branch, iterator=True).next().id
        )
        self.assertNotEqual(last_commit, last_commit_gitlab)

        response = await self.gl_webhook_event("Push Hook", last_commit_gitlab, branch)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "push event detected")

        last_commit_github = self.github.get_branch(branch).commit.sha
        self.assertEqual(last_commit_github, last_commit_gitlab)

    async def test_push_gitlab_master(self):
        """Test sync after pushing to gitlab on master."""
        await self.push_gitlab("master")

    async def test_push_gitlab_devel(self):
        """Test sync after pushing to gitlab on devel."""
        await self.push_gitlab("devel")

    async def test_branch_github(self):
        """Test sync after creating or deleting a branch on github."""
        await self.sync()
        source_branch_name = "master"
        target_branch_name = "test-branch-github"
        last_commit = self.github.get_branch(source_branch_name).commit.sha

        # Test sync after creating a new branch
        source_branch = self.github.get_branch(source_branch_name)
        if target_branch_name in [b.name for b in self.github.get_branches()]:
            branch_ref = self.github.get_git_ref(ref=f"heads/{target_branch_name}")
        else:
            branch_ref = self.github.create_git_ref(
                ref=f"refs/heads/{target_branch_name}",
                sha=source_branch.commit.sha,
            )
        file = self.github.get_contents("README.md", target_branch_name)
        self.github.update_file(
            "README.md",
            message="Test new branch on github",
            content=last_commit[:8],
            sha=file.sha,
            branch=target_branch_name,
        )

        target_branch = self.github.get_branch(target_branch_name)
        last_commit_github = target_branch.commit.sha
        response = await self.gh_webhook_event(
            "push",
            last_commit_github,
            target_branch_name,
        )
        print(f"{response.content=}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "push event detected")

        async for q in PushQueue.objects.all():
            await sync_to_async(q.push)()

        last_commit_gitlab = (
            self.gitlab.commits.list(
                ref_name=target_branch_name,
                iterator=True,
            )
            .next()
            .id
        )
        self.assertEqual(last_commit_github, last_commit_gitlab)

        # Test sync after deleting a branch
        branch_ref.delete()
        self.assertNotIn(
            target_branch_name,
            [b.name for b in self.github.get_branches()],
        )

        response = await self.gh_webhook_event(
            "push",
            "0000000000000000000000000000000000000000",
            target_branch_name,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "push event detected")
        self.assertNotIn(
            target_branch_name,
            [b.name for b in self.gitlab.branches.list()],
        )

    async def test_branch_gitlab(self):
        """Test sync after creating or deleting a branch on gitlab."""
        await self.sync()
        source_branch_name = "master"
        target_branch_name = "test-branch-gitlab"
        last_commit = (
            self.gitlab.commits.list(
                ref_name=source_branch_name,
                iterator=True,
            )
            .next()
            .id
        )

        # Test sync after creating a new branch
        if target_branch_name in [b.name for b in self.gitlab.branches.list()]:
            target_branch = self.gitlab.branches.get(target_branch_name)
        else:
            target_branch = self.gitlab.branches.create(
                {"branch": target_branch_name, "ref": source_branch_name},
            )

        file = self.gitlab.files.get(file_path="README.md", ref=target_branch_name)
        file.content = last_commit[:8]
        file.save(branch=target_branch_name, commit_message="Test new branch on gitlab")

        last_commit_gitlab = (
            self.gitlab.commits.list(ref_name=target_branch_name, iterator=True)
            .next()
            .id
        )
        response = await self.gl_webhook_event(
            "Push Hook",
            last_commit_gitlab,
            target_branch_name,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "push event detected")

        await sleep(5)
        await self.sync()
        last_commit_github = self.github.get_branch(target_branch_name).commit.sha
        self.assertEqual(last_commit_github, last_commit_gitlab)

        # Test sync after deleting a branch
        target_branch.delete()
        self.assertNotIn(
            target_branch_name,
            [b.name for b in self.gitlab.branches.list()],
        )

        response = await self.gl_webhook_event(
            "Push Hook",
            "0000000000000000000000000000000000000000",
            target_branch_name,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "push event detected")
        self.assertNotIn(
            target_branch_name,
            [b.name for b in self.github.get_branches()],
        )

    async def test_pipeline(self):
        """Test reporting the gitlab pipeline status to github."""
        await self.sync()
        last_commit = (
            self.gitlab.commits.list(ref_name="master", iterator=True).next().id
        )
        response = await self.gl_webhook_event(
            "Pipeline Hook",
            last_commit,
            status="success",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "success",
            [
                status.state
                for status in self.github.get_branch("master").commit.get_statuses()
            ],
        )

    async def test_pr(self):
        """Test github's pull requests."""
        await self.sync()
        not_accepted_string = "doesn't usually accept pull requests on the main branch."

        # Test pr on master
        last_commit = self.github.get_branch("devel").commit.sha
        github = await sync_to_async(self.project.github)()
        pr_master = github.create_pull(
            title="Test pr on master",
            body="",
            head="devel",
            base="master",
        )
        response = await self.gh_webhook_event(
            "pull_request",
            last_commit=last_commit,
            pr_action="opened",
            pr_login="foo",
            pr_number=pr_master.number,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            [
                c.body
                for c in pr_master.get_issue_comments()
                if not_accepted_string in c.body
            ],
        )
        async for q in PushQueue.objects.all():
            await sync_to_async(q.push)()
        await sleep(30)
        self.assertIn(
            f"pr/{pr_master.number}",
            [b.name for b in self.gitlab.branches.list()],
        )

        # Test pr on devel
        last_commit = self.github.get_branch("master").commit.sha
        pr_devel = github.create_pull(
            title="Test pr on devel",
            body="",
            head="master",
            base="devel",
        )
        response = await self.gh_webhook_event(
            "pull_request",
            last_commit=last_commit,
            pr_action="opened",
            pr_login="foo",
            pr_number=pr_devel.number,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            [
                c.body
                for c in pr_devel.get_issue_comments()
                if not_accepted_string in c.body
            ],
        )
        await sleep(30)
        self.assertIn(
            f"pr/{pr_devel.number}",
            [b.name for b in self.gitlab.branches.list()],
        )

        # Close the pr
        for pr in [pr_master, pr_devel]:
            pr.edit(state="closed")
            response = await self.gh_webhook_event(
                "pull_request",
                pr_action="closed",
                pr_login="foo",
                pr_number=pr.number,
            )
            self.assertEqual(response.status_code, 200)
            await sleep(30)
            self.assertNotIn(
                f"pr/{pr.number}",
                [b.name for b in self.gitlab.branches.list()],
            )

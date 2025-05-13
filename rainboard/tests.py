import doctest

from django.test import TestCase
from django.urls import reverse

from . import models, utils
from .models import IssuePr, Repo


class RainboardTests(TestCase):
    def test_utils(self):
        failure_count, test_count = doctest.testmod(utils)
        self.assertEqual(failure_count, 0)
        self.assertEqual(test_count, 5)

    def test_models(self):
        license_count = models.License.objects.count()
        project_count = models.Project.objects.count()
        models.License.objects.create(
            name='BSD 2-Clause "Simplified" License',
            spdx_id="BSD-2-Clause",
            url="http://spdx.org/licenses/BSD-2-Clause.json",
        )
        models.Project.objects.create(
            name="Rainboard Tests 2",
            main_namespace=models.Namespace.objects.get(slug="gepetto"),
            main_forge=models.Forge.objects.get(source=utils.SOURCES.github),
            license=models.License.objects.first(),
        )
        self.assertEqual(models.License.objects.count(), license_count + 1)
        self.assertEqual(models.Project.objects.count(), project_count + 1)

        project = models.Project.objects.get(name="rainboard tests 2")

        self.assertEqual(project.slug, "rainboard-tests-2")
        self.assertEqual(project.registry(), "memmos.laas.fr:5000")
        self.assertEqual(
            project.url_travis(),
            "https://travis-ci.org/gepetto/rainboard-tests-2",
        )
        self.assertEqual(
            project.url_gitlab(),
            "https://gitlab.laas.fr/gepetto/rainboard-tests-2",
        )
        badges = project.badges()
        for chunk in ['<img src="https://gitlab.laas', 'href="https://gepettoweb.laas']:
            self.assertIn(chunk, badges)

        # Test Middleware
        response = self.client.get(
            reverse("rainboard:project", kwargs={"slug": project.slug}),
            headers={"x-real-ip": "9.9.9.9"},
        )
        self.assertEqual(response.status_code, 302)
        response = self.client.get(
            reverse("rainboard:project", kwargs={"slug": project.slug}),
            headers={"x-real-ip": "140.93.5.4"},
        )
        self.assertEqual(response.status_code, 200)

        # Test Views
        content = response.content.decode()
        for chunk in [
            "<title>Gepetto Packages</title>",
            "<h1>rainboard tests 2</h1>",
            'Main forge</dt> <dd class="col-9"><a href="https://github.com">Github</a></dd>',
            '<label class="label label-primary">BSD-2-Clause</label>',
        ]:
            self.assertIn(chunk, content)

        # Test issues and pull requests view
        repo = Repo.objects.create(
            name="foo",
            forge=models.Forge.objects.get(source=utils.SOURCES.github),
            namespace=models.Namespace.objects.get(slug="gepetto"),
            project=project,
            default_branch="master",
            repo_id=4,
            clone_url="https://github.com",
        )

        IssuePr.objects.create(
            title="Test issue",
            repo=repo,
            number=7,
            url="https://github.com",
            is_issue=True,
        )

        response = self.client.get(
            reverse("rainboard:issues_pr"),
            headers={"x-real-ip": "140.93.5.4"},
        )
        self.assertEqual(response.status_code, 200)

        content = response.content.decode()
        for chunk in [
            "<title>Gepetto Packages</title>",
            '<a class="btn btn-primary" href="/issues/update">Update</a>',
            '<button class="btn btn-primary">filter</button>',
            f'<a href="/project/{project.slug}/robotpkg">{project.name}</a>',
            "<td >Test issue</td>",
            '<a href="https://github.com">issue #7</a>',
        ]:
            self.assertIn(chunk, content)

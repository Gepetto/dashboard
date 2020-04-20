import doctest

from django.test import TestCase

from . import models, utils


class RainboardTests(TestCase):
    def test_utils(self):
        failure_count, test_count = doctest.testmod(utils)
        self.assertEqual(failure_count, 0)
        self.assertEqual(test_count, 5)

    def test_models(self):
        self.assertEqual(models.License.objects.count(), 0)
        self.assertEqual(models.Project.objects.count(), 0)
        models.License.objects.create(name='BSD 2-Clause "Simplified" License',
                                      spdx_id='BSD-2-Clause',
                                      url='http://spdx.org/licenses/BSD-2-Clause.json')
        models.Project.objects.create(name='Rainboard Tests',
                                      main_namespace=models.Namespace.objects.get(slug='gepetto'),
                                      main_forge=models.Forge.objects.get(source=utils.SOURCES.github),
                                      license=models.License.objects.first())
        self.assertEqual(models.License.objects.count(), 1)
        self.assertEqual(models.Project.objects.count(), 1)

        project = models.Project.objects.first()

        self.assertEqual(project.slug, 'rainboard-tests')
        self.assertEqual(project.registry(), 'memmos.laas.fr:5000')
        self.assertEqual(project.url_travis(), 'https://travis-ci.org/gepetto/rainboard-tests')
        self.assertEqual(project.url_gitlab(), 'https://gitlab.laas.fr/gepetto/rainboard-tests')
        badges = project.badges()
        for chunk in ['<img src="https://gitlab.laas', 'travis-ci', 'href="https://gepettoweb.laas']:
            self.assertIn(chunk, badges)

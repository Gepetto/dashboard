import doctest

from django.test import TestCase

from . import utils


class RainboardTests(TestCase):
    def test_doctests(self):
        failure_count, test_count = doctest.testmod(utils)
        self.assertEqual(failure_count, 0)
        self.assertEqual(test_count, 5)

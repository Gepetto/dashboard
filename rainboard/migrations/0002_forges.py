# Generated by Django 2.0.1 on 2018-01-05 10:20

import os

from django.db import migrations

import requests

from rainboard.utils import SOURCES


def forges(apps, schema_editor):
    Forge = apps.get_model('rainboard', 'Forge')
    Forge.objects.create(name='Gitlab', source=SOURCES.gitlab, url='https://eur0c.laas.fr', verify=False,
                         token=os.getenv('GITLAB_TOKEN'))
    Forge.objects.create(name='Github', source=SOURCES.github, url='https://github.com',
                         token=os.getenv('GITHUB_TOKEN'))
    Forge.objects.create(name='Redmine', source=SOURCES.redmine, url='https://redmine.laas.fr',
                         token=os.getenv('REDMINE_TOKEN'))
    # Forge.objects.create(name='Openrobots', source=SOURCES.redmine, url='https://git.openrobots.org',
                         # token=os.getenv('OPENROB_TOKEN'))


class Migration(migrations.Migration):

    dependencies = [
        ('rainboard', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forges),
    ]

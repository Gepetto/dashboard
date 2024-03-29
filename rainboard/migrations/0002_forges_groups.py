# Generated by Django 2.0.1 on 2018-01-05 10:20

import os

from django.db import migrations

from rainboard.utils import SOURCES


def forges(apps, schema_editor):
    Forge = apps.get_model("rainboard", "Forge")
    gitlab_token = os.getenv("GITLAB_TOKEN")
    if gitlab_token is None:
        gitlab_token = os.getenv("GITLAB_PIPELINE_TOKEN")
    Forge.objects.create(
        name="Gitlab",
        source=SOURCES.gitlab,
        url="https://gepgitlab.laas.fr",
        token=gitlab_token,
    )
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token is None:
        github_token = os.getenv("GITHUB_PIPELINE_TOKEN")
    Forge.objects.create(
        name="Github",
        source=SOURCES.github,
        url="https://github.com",
        token=github_token,
    )
    Forge.objects.create(
        name="Redmine",
        source=SOURCES.redmine,
        url="https://redmine.laas.fr",
        token=os.getenv("REDMINE_TOKEN"),
    )
    Forge.objects.create(
        name="Openrobots",
        source=SOURCES.redmine,
        url="https://git.openrobots.org",
        token=os.getenv("OPENROB_TOKEN"),
    )
    Forge.objects.create(
        name="Travis",
        source=SOURCES.travis,
        url="https://travis-ci.org",
        token=os.getenv("TRAVIS_TOKEN"),
    )


def groups(apps, schema_editor):
    Namespace = apps.get_model("rainboard", "Namespace")
    Namespace.objects.create(name="Stack Of Tasks", group=True)
    Namespace.objects.create(name="Humanoid Path Planner", group=True)
    Namespace.objects.create(name="Gepetto", group=True)
    Namespace.objects.create(name="Pyrène Dev", group=True)
    Namespace.objects.create(name="HRP2 Dev", group=True)


class Migration(migrations.Migration):
    dependencies = [
        ("rainboard", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(forges),
        migrations.RunPython(groups),
    ]

# Generated by Django 2.0.2 on 2018-02-15 18:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rainboard", "0003_image"),
    ]

    operations = [
        migrations.CreateModel(
            name="Contributor",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("projects", models.ManyToManyField(to="rainboard.Project")),
            ],
        ),
        migrations.CreateModel(
            name="ContributorMail",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("mail", models.EmailField(max_length=254, unique=True)),
                ("invalid", models.BooleanField(default=False)),
                (
                    "contributor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="rainboard.Contributor",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ContributorName",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200, unique=True)),
                (
                    "contributor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="rainboard.Contributor",
                    ),
                ),
            ],
        ),
    ]

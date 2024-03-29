# Generated by Django 2.1.7 on 2019-03-07 01:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rainboard", "0031_started"),
    ]

    operations = [
        migrations.CreateModel(
            name="CIJob",
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
                ("passed", models.NullBooleanField()),
                ("job_id", models.PositiveIntegerField()),
                ("started", models.DateTimeField()),
                (
                    "branch",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="rainboard.Branch",
                    ),
                ),
                (
                    "repo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="rainboard.Repo"
                    ),
                ),
            ],
            options={
                "ordering": ("-started",),
            },
        ),
    ]

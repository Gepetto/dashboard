# Generated by Django 5.0.6 on 2024-10-07 17:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("gh", "0002_big"),
        ("rainboard", "0087_alter_project_slug_us"),
    ]

    operations = [
        migrations.CreateModel(
            name="PushQueue",
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
                ("gl_remote_name", models.CharField(max_length=255)),
                ("branch", models.CharField(max_length=255)),
                (
                    "namespace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="rainboard.namespace",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="rainboard.project",
                    ),
                ),
            ],
        ),
    ]
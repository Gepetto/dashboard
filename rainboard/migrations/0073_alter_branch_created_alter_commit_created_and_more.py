# Generated by Django 4.2.1 on 2023-06-05 15:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rainboard", "0072_drop_bionic"),
    ]

    operations = [
        migrations.AlterField(
            model_name="branch",
            name="created",
            field=models.DateTimeField(auto_now_add=True, verbose_name="created"),
        ),
        migrations.AlterField(
            model_name="commit",
            name="created",
            field=models.DateTimeField(auto_now_add=True, verbose_name="created"),
        ),
        migrations.AlterField(
            model_name="commit",
            name="name",
            field=models.CharField(max_length=200, unique=True, verbose_name="name"),
        ),
        migrations.AlterField(
            model_name="commit",
            name="updated",
            field=models.DateTimeField(auto_now=True, verbose_name="updated"),
        ),
        migrations.AlterField(
            model_name="forge",
            name="name",
            field=models.CharField(max_length=200, unique=True, verbose_name="name"),
        ),
        migrations.AlterField(
            model_name="forge",
            name="token",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name="image",
            name="image",
            field=models.CharField(blank=True, max_length=12),
        ),
        migrations.AlterField(
            model_name="namespace",
            name="name",
            field=models.CharField(max_length=200, unique=True, verbose_name="name"),
        ),
        migrations.AlterField(
            model_name="project",
            name="cmake_name",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AlterField(
            model_name="project",
            name="created",
            field=models.DateTimeField(auto_now_add=True, verbose_name="created"),
        ),
        migrations.AlterField(
            model_name="project",
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="project",
            name="homepage",
            field=models.URLField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="project",
            name="name",
            field=models.CharField(max_length=200, unique=True, verbose_name="name"),
        ),
        migrations.AlterField(
            model_name="project",
            name="version",
            field=models.CharField(blank=True, default="", max_length=20),
        ),
        migrations.AlterField(
            model_name="repo",
            name="created",
            field=models.DateTimeField(auto_now_add=True, verbose_name="created"),
        ),
        migrations.AlterField(
            model_name="repo",
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="repo",
            name="homepage",
            field=models.URLField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="repo",
            name="updated",
            field=models.DateTimeField(auto_now=True, verbose_name="updated"),
        ),
        migrations.AlterField(
            model_name="repo",
            name="url",
            field=models.URLField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="robotpkg",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="robotpkg",
            name="homepage",
            field=models.URLField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="robotpkg",
            name="name",
            field=models.CharField(max_length=200, unique=True, verbose_name="name"),
        ),
        migrations.AlterField(
            model_name="target",
            name="name",
            field=models.CharField(max_length=200, unique=True, verbose_name="name"),
        ),
    ]

# Generated by Django 2.1.7 on 2019-03-26 14:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rainboard", "0034_dependency_mandatory"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="allow_format_failure",
            field=models.BooleanField(default=True),
        ),
    ]

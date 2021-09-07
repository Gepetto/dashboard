# Generated by Django 3.2.5 on 2021-07-28 15:56

from django.db import migrations, models


def remove_all_images(apps, schema_editor):
    Image = apps.get_model('rainboard', 'Image')
    Image.objects.all().delete()


def create_all_images(apps, schema_editor):
    # TODO: doesn't work, run this manually :/
    Robotpkg = apps.get_model('rainboard', 'Robotpkg')
    for rpkg in Robotpkg.objects.all():
        rpkg.update_images()


class Migration(migrations.Migration):

    dependencies = [
        ('rainboard', '0057_target_public'),
    ]

    operations = [
        migrations.RunPython(remove_all_images),
        migrations.RemoveField(
            model_name='target',
            name='py2_available',
        ),
        migrations.AlterField(
            model_name='forge',
            name='source',
            field=models.PositiveSmallIntegerField(
                choices=[(1, 'Github'), (2, 'Gitlab'), (3, 'Redmine'), (4, 'Robotpkg'), (5, 'Travis')]),
        ),
        migrations.AlterUniqueTogether(
            name='image',
            unique_together={('robotpkg', 'target')},
        ),
        migrations.RemoveField(
            model_name='image',
            name='debug',
        ),
        migrations.RemoveField(
            model_name='image',
            name='py3',
        ),
        # migrations.RunPython(create_all_images),
    ]
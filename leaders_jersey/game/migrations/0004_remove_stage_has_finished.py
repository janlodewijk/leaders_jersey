# Generated by Django 5.1.7 on 2025-05-04 19:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_stage_has_finished'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stage',
            name='has_finished',
        ),
    ]

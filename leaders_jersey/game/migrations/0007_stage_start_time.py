# Generated by Django 5.1.7 on 2025-03-28 14:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_alter_stage_stage_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='stage',
            name='start_time',
            field=models.TimeField(default=datetime.time(12, 0)),
        ),
    ]

# Generated by Django 5.1.7 on 2025-04-07 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0016_alter_stageresult_stage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='race',
            name='year',
            field=models.PositiveSmallIntegerField(default=2025),
        ),
    ]

# Generated by Django 5.1.7 on 2025-04-03 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0012_alter_stageresult_stage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stageresult',
            name='ranking',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]

# Generated by Django 5.1.7 on 2025-04-17 08:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ETLRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('etl_type', models.CharField(choices=[('startlist', 'Startlist'), ('stage_info', 'Stage Info'), ('stage_results', 'Stage Results')], max_length=20)),
                ('executed_at', models.DateTimeField(auto_now_add=True)),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.race')),
                ('stage', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='game.stage')),
            ],
        ),
    ]

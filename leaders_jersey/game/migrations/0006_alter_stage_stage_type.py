# Generated by Django 5.1.7 on 2025-03-24 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_stage_arrival_stage_departure_stage_distance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stage',
            name='stage_type',
            field=models.CharField(blank=True, choices=[('Flat', 'Flat'), ('Hills', 'Hills'), ('Mountain', 'Mountain'), ('TT', 'Time Trial'), ('Team TT', 'Team Time Trial')], max_length=20, null=True),
        ),
    ]

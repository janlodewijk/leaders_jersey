from django.db import models
from game.models import Race, Stage

class ETLRun(models.Model):
    ETL_TYPE_CHOICES = [
        ('startlist', 'Startlist'),
        ('stage_info', 'Stage Info'),
        ('stage_results', 'Stage Results'),
    ]

    etl_type = models.CharField(max_length=20, choices=ETL_TYPE_CHOICES)
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.SET_NULL, null=True, blank=True)
    executed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_etl_type_display()} - {self.race.race_name} ({self.race.year})"
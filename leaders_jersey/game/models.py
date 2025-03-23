from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta


class Race(models.Model):
    race_name = models.CharField(max_length=100)
    year = models.PositiveSmallIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    url_reference = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.race_name} ({self.year})"


class Stage(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='stages', null=True)
    stage_number = models.PositiveSmallIntegerField()
    stage_date = models.DateField()
    departure = models.CharField(max_length=100, null=True)
    arrival = models.CharField(max_length=100, null=True, default='Unknown')
    distance = models.PositiveSmallIntegerField(null=True)
    stage_type = models.CharField(max_length=50, null=True, blank=True)     # mountain, sprint, TT etc.

    class Meta:
        unique_together = ('race', 'stage_number')  # prevents duplicate stage numbers per race
        ordering = ['race', 'stage_number']

    def __str__(self):
        return f"{self.race.race_name} - Stage {self.stage_number}"


class Rider(models.Model):
    rider_name = models.CharField(max_length=100)
    team = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100)
    external_id = models.CharField(max_length=100, unique=True)
    start_number = models.PositiveSmallIntegerField(null=True, blank=True)
    is_participating = models.BooleanField(default=False)

    class Meta:
        ordering = ['start_number']

    def __str__(self):
        return f"{self.start_number}: {self.rider_name} ({self.team})"


class StageResult(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='results')
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name='stage_results')
    finishing_time = models.DurationField()
    ranking = models.PositiveSmallIntegerField()
    bonus = models.DurationField(default=timedelta(seconds=0))


class PlayerSelection(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='selections')
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='player_selections')
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    selected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player', 'stage')   # to ensure that the player will select only one rider per stage

    def __str__(self):
        return f"{self.player.username} - Stage {self.stage.stage_number}:{self.rider.rider_name}"
from django.db import models
from django.contrib.auth.models import User


class Tour(models.Model):
    tour_name = models.CharField(max_length=100)
    year = models.PositiveSmallIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.tour_name} ({self.year})"


class Stage(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='stages')
    stage_number = models.PositiveSmallIntegerField()
    stage_date = models.DateField()
    stage_type = models.CharField(max_length=50)     # mountain, sprint, TT etc.

    class Meta:
        unique_together = ('tour', 'stage_number')  # prevents duplicate stage numbers per tour
        ordering = ['tour', 'stage_number']

    def __str__(self):
        return f"{self.tour.tour_name} - Stage {self.stage_number}"


class Rider(models.Model):
    rider_name = models.CharField(max_length=100)
    team = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100)
    external_id = models.CharField(max_length=100, unique=True)
    start_number = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['start_number']

    def __str__(self):
        return f"{self.start_number}: {self.rider_name} ({self.team})"


class StageResult(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='results')
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name='stage_results')
    finishing_time = models.DurationField()
    ranking = models.PositiveSmallIntegerField()


class PlayerSelection(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='selections')
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='player_selections')
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    selected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player', 'stage')   # to ensure that the player will select only one rider per stage

    def __str__(self):
        return f"{self.player.username} - Stage {self.stage.stage_number}:{self.rider.rider_name}"
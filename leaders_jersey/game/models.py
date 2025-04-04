from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, time


class Race(models.Model):
    race_name = models.CharField(max_length=100)
    year = models.PositiveSmallIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    url_reference = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.race_name} ({self.year})"


class Stage(models.Model):
    STAGE_TYPE_CHOICES = [
        ('Flat', 'Flat'),
        ('Hills', 'Hills'),
        ('Punch', 'Punch'),
        ('Mountain', 'Mountain'),
        ('Mountain climb finish', 'Mountain climb finish'),
        ('Indiv. Time Trial', 'Indiv. Time Trial'),
        ('Team TT', 'Team Time Trial')
    ]
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='stages', null=True)
    stage_number = models.PositiveSmallIntegerField()
    stage_date = models.DateField()
    departure = models.CharField(max_length=100, null=True)
    arrival = models.CharField(max_length=100, null=True, default='Unknown')
    distance = models.PositiveSmallIntegerField(null=True)
    stage_type = models.CharField(max_length=30, choices=STAGE_TYPE_CHOICES, null=True, blank=True)     # mountain, sprint, TT etc.
    start_time = models.TimeField(default=time(12,0))

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
    stage = models.ForeignKey(Stage, on_delete=models.SET_NULL, related_name='results', null=True, blank=True)
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name='stage_results')
    finishing_time = models.DurationField(null=True, blank=True)
    ranking = models.PositiveSmallIntegerField(null=True, blank=True)
    bonus = models.DurationField(default=timedelta(seconds=0))
    gc_time = models.DurationField(null=True, blank=True)
    gc_rank = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.stage} - {self.rider}"


class PlayerSelection(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='selections')
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, null=True, blank=True, related_name='player_selections')
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    selected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # Only one rider per stage
            models.UniqueConstraint(fields=['player', 'stage'], name='unique_stage_selection'),
            # Only one backup rider for the whole race, if selected stage rider did not finish
            models.UniqueConstraint(fields=['player'], condition=models.Q(stage__isnull=True), name='unique_backup_selection')
        ]

    def __str__(self):
        if self.stage:
            return f"{self.player.username} - Stage {self.stage.stage_number}: {self.rider.rider_name}"
        else:
            return f"{self.player.username} - Backup rider: {self.rider.rider_name}"
        


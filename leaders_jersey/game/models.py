from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, time
from django.db.models import Q


class Race(models.Model):
    race_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    year = models.PositiveSmallIntegerField(default=2025)
    start_date = models.DateField()
    end_date = models.DateField()
    url_reference = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        unique_together = ('slug', 'year')  # ensures URL uniqueness per year

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
    is_canceled = models.BooleanField(default=False)

    class Meta:
        unique_together = ('race', 'stage_number')  # prevents duplicate stage numbers per race
        ordering = ['race', 'stage_number']

    def __str__(self):
        return f"{self.race.race_name} - Stage {self.stage_number}"


class Team(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Rider(models.Model):
    rider_name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    nationality = models.CharField(max_length=100)
    external_id = models.CharField(max_length=100, unique=True)
    start_number = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['start_number']

    def __str__(self):
        return f"{self.start_number}: {self.rider_name} ({self.team})"


class StageResult(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='results', null=True, blank=True)
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name='stage_results')
    finishing_time = models.DurationField(null=True, blank=True)
    ranking = models.PositiveSmallIntegerField(null=True, blank=True)
    bonus = models.DurationField(default=timedelta(seconds=0))
    gc_time = models.DurationField(null=True, blank=True)
    gc_rank = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.stage} - {self.rider}"
        

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class StartlistEntry(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='startlist_entries')
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name='startlist_entries')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    start_number = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('race', 'rider')
        ordering = ['start_number']

    def __str__(self):
        return f"{self.rider.rider_name} - {self.race.race_name} ({self.race.year})"


class RaceParticipant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='race_participations')
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='participants')
    backup_rider = models.ForeignKey(StartlistEntry, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ('user', 'race')
    
    def __str__(self):
        return f"{self.user.username} in {self.race.race_name} ({self.race.year})"
    

class PlayerSelection(models.Model):
    race_participant = models.ForeignKey(RaceParticipant, on_delete=models.CASCADE, related_name='selections')
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, null=True, blank=True, related_name='player_selections')
    rider = models.ForeignKey(StartlistEntry, on_delete=models.CASCADE)
    selected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['race_participant', 'stage'], name='unique_stage_selection'),
            models.UniqueConstraint(fields=['race_participant'], condition=Q(stage__isnull=True), name='unique_backup_selection')
        ]

    def __str__(self):
        if self.stage:
            return f"{self.race_participant.user.username} - Stage {self.stage.stage_number}: {self.rider.rider.rider_name}"
        else:
            return f"{self.race_participant.user.username} - Backup rider: {self.rider.rider.rider_name}"


class PlayerUciPoints(models.Model):
    race_participant = models.ForeignKey(RaceParticipant, on_delete=models.CASCADE)
    uci_points = models.SmallIntegerField(blank=True, null=True)
    gc_rank = models.SmallIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

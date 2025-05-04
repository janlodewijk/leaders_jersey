# game/context_processors.py

from .models import RaceParticipant

def race_dropdown_data(request):
    if not request.user.is_authenticated:
        return {}

    race_participations = RaceParticipant.objects.filter(user=request.user).select_related('race')
    current_races = []
    finished_races = []

    for participation in race_participations:
        race = participation.race
        if race.stages.filter(has_finished=False).exists():
            current_races.append(participation)
        else:
            finished_races.append(participation)

    return {
        'current_races': current_races,
        'finished_races': finished_races,
    }

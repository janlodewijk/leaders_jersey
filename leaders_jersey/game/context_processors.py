from .models import RaceParticipant, Race

def race_dropdown_data(request):
    if not request.user.is_authenticated:
        return {}

    participations = RaceParticipant.objects.filter(user=request.user).select_related('race')
    joined_race_ids = [p.race.id for p in participations]

    current_races = []
    finished_races = []

    for p in participations:
        race = p.race
        if race.has_finished:
            finished_races.append(p)
        else:
            current_races.append(p)

    available_races = Race.objects.exclude(id__in=joined_race_ids).order_by('start_date')

    return {
        'current_races': current_races,
        'finished_races': finished_races,
        'available_races': available_races,
    }

from datetime import timedelta, datetime
from django.utils import timezone
from game.models import RaceParticipant, PlayerSelection, StageResult, Stage, PlayerUciPoints, Race
from etl.transform.transform_uci import transform_uci_points

from collections import defaultdict

def calculate_game_gc_standings(race):
    stages = Stage.objects.filter(race=race).order_by('stage_date', 'stage_number')
    participants = RaceParticipant.objects.filter(race=race).select_related('user')

    standings = []

    for participant in participants:
        selections = PlayerSelection.objects.filter(
            race_participant=participant,
            stage__in=stages
        ).select_related('stage', 'rider__rider')

        backup_selection = PlayerSelection.objects.filter(
            race_participant=participant,
            stage=None
        ).select_related('rider__rider').first()

        backup_rider = backup_selection.rider.rider if backup_selection and backup_selection.rider else None

        total_gc_time = timedelta(0)

        for stage in stages:
            # Only process finished stages
            if not StageResult.objects.filter(stage=stage).exists():
                continue

            result = None
            selection = next((s for s in selections if s.stage_id == stage.id), None)

            # 1. Use selected rider if valid
            if selection and selection.rider:
                result = StageResult.objects.filter(
                    stage=stage,
                    rider=selection.rider.rider,
                    ranking__isnull=False,
                    finishing_time__isnull=False
                ).first()

            # 2. Use backup rider if no result yet
            if not result and backup_rider:
                result = StageResult.objects.filter(
                    stage=stage,
                    rider=backup_rider,
                    ranking__isnull=False,
                    finishing_time__isnull=False
                ).first()

            # 3. Fallback: last classified finisher
            if not result:
                result = StageResult.objects.filter(
                    stage=stage,
                    ranking__isnull=False,
                    finishing_time__isnull=False
                ).order_by('-ranking').first()

            # 4. Add time
            if result and result.finishing_time:
                is_selected_rider = (
                    selection
                    and selection.rider
                    and result.rider == selection.rider.rider
                )
                time_to_add = result.finishing_time
                if is_selected_rider:
                    time_to_add -= result.bonus or timedelta(0)

                total_gc_time += time_to_add

        standings.append({
            'participant': participant,
            'user': participant.user,
            'total_gc_time': total_gc_time
        })

    # Sort standings by total time
    standings.sort(key=lambda x: x['total_gc_time'])

    # Assign GC ranks (with ties)
    for i, row in enumerate(standings):
        if i > 0 and row['total_gc_time'] == standings[i - 1]['total_gc_time']:
            row['gc_rank'] = standings[i - 1]['gc_rank']
        else:
            row['gc_rank'] = i + 1

    return standings


def assign_uci_points(race_slug, race):
    uci_points = transform_uci_points(race_slug)
    race_results = calculate_game_gc_standings(race)

    # Group players with the same GC time
    time_groups = defaultdict(list)
    for entry in race_results:
        time_groups[entry['total_gc_time']].append(entry)
    
    # Loop through time groups and assign points
    current_rank = 1

    for gc_time in sorted(time_groups.keys()):
        tied_players = time_groups[gc_time]
        tie_count = len(tied_players)
    
        # Get points for this groups of ranks (e.g., if two players at rank 2, give them the avg points of rank 2 and 3)
        point_values = [
            uci_points.get(rank) for rank in range(current_rank, current_rank + tie_count)
            if uci_points.get(rank) is not None
        ]

        avg_points = round(sum(point_values) / len(point_values)) if point_values else 0

        for player in tied_players:
            PlayerUciPoints.objects.update_or_create(
                race_participant=player['participant'],
                defaults={
                    'uci_points': avg_points,
                    'gc_rank': current_rank,
                    'timestamp': timezone.now()
                }
            )
    
        current_rank += tie_count


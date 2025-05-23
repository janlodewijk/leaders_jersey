from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from game.models import Race, Stage, Rider, PlayerSelection, StageResult, RaceParticipant, StartlistEntry, PlayerUciPoints
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.db.models import Sum
from collections import defaultdict
from .forms import CustomUserCreationForm
from django.utils.timezone import make_aware

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        team_name = request.POST.get('team_name')

        if form.is_valid():
            user = form.save()
            user.profile.team_name = team_name
            user.profile.save()
            
            messages.success(request, 'Registration successful!')
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})


class CustomLoginView(LoginView):
    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().username}!")
        return super().form_valid(form)
    

def custom_logout_view(request):
    logout(request)
    messages.success(request, "You've been logged out successfully.")
    return redirect('login')


def home(request):
    return render(request, 'home.html')


@login_required
def profile(request):
    return render(request, 'profile.html')


@login_required
def rider_selection(request, race_slug, year):
    race = get_object_or_404(Race, url_reference=race_slug, year=year)

    try:
        participant = RaceParticipant.objects.get(user=request.user, race=race)
    except RaceParticipant.DoesNotExist:
        return redirect('join_race', race_slug=race_slug, year=year)

    if request.method == 'POST':
        rider_id = request.POST.get('rider_id')
        stage_id = request.POST.get('stage_id')

        if rider_id:
            entry = get_object_or_404(StartlistEntry, rider_id=rider_id, race=race)

            if not stage_id:
                PlayerSelection.objects.update_or_create(
                    race_participant=participant,
                    stage=None,
                    defaults={'rider': entry}
                )
            else:
                stage = get_object_or_404(Stage, id=stage_id)
                PlayerSelection.objects.update_or_create(
                    race_participant=participant,
                    stage=stage,
                    defaults={'rider': entry}
                )

            return redirect(request.path)

    stages = Stage.objects.filter(race=race).exclude(stage_number__isnull=True).order_by('stage_date', 'stage_number')
    race_length = len(stages)
    rider_limit = 1 if race_length <= 8 else 2 if race_length <= 14 else 3

    entries = StartlistEntry.objects.filter(race=race).select_related('rider', 'team').order_by('start_number')
    riders = [entry.rider for entry in entries]

    dnf_riders = StageResult.objects.filter(
        stage__race=race,
        ranking__isnull=True
    ).values_list('rider_id', flat=True)

    valid_stage_ids = stages.filter(is_canceled=False).values_list('id', flat=True)
    player_selections = PlayerSelection.objects.filter(
        race_participant=participant,
        stage_id__in=valid_stage_ids
    ).select_related('stage', 'rider')

    selection_lookup = {sel.stage_id: sel for sel in player_selections}
    selected_stage_rider_ids = {sel.rider.rider.id for sel in player_selections if sel.rider and sel.stage}

    backup_selection = PlayerSelection.objects.filter(
        race_participant=participant,
        stage=None
    ).first()

    backup_rider_id = backup_selection.rider.id if backup_selection and backup_selection.rider else None
    backup_rider_dnf = backup_rider_id in dnf_riders if backup_rider_id else False

    backup_locked = True
    if stages:
        stage1_start = timezone.make_aware(datetime.combine(stages[0].stage_date, stages[0].start_time))
        backup_locked = timezone.now() > stage1_start and not backup_rider_dnf

    stage_data = []
    total_gc_time = timedelta(0)

    for stage in stages:
        deadline = timezone.make_aware(datetime.combine(stage.stage_date, stage.start_time))
        locked = timezone.now() > deadline

        selection = selection_lookup.get(stage.id)
        selected_rider = selection.rider if selection else None

        result = None
        used_backup = False
        used_fallback = False

        if selected_rider:
            result = StageResult.objects.filter(
                stage=stage,
                rider=selected_rider.rider,
                ranking__isnull=False,
                finishing_time__isnull=False
            ).first()

        if not result and backup_selection and backup_selection.rider:
            result = StageResult.objects.filter(stage=stage,
                                                rider=backup_selection.rider.rider,
                                                ranking__isnull=False,
                                                finishing_time__isnull=False
                                                ).first()
            used_backup = result is not None

        if not result:
            result = StageResult.objects.filter(stage=stage).order_by('-ranking').first()
            used_fallback = result is not None

        if result:
            if used_fallback:
                total_gc_time += result.finishing_time
            else:
                total_gc_time += result.finishing_time - result.bonus

        stage_data.append({
            'stage': stage,
            'locked': locked,
            'selection': selected_rider,
            'result': result,
            'deadline': deadline,
            'deadline_iso': deadline.isoformat(),
            'used_backup': used_backup,
            'used_fallback': used_fallback,
            'is_canceled': stage.is_canceled,
        })

    rider_usage = {}
    for selection in player_selections:
        if selection.rider:
            rider_id = selection.rider.rider.id
            rider_usage[rider_id] = rider_usage.get(rider_id, 0) + 1

    team_riders = defaultdict(list)
    for entry in entries:
        rider = entry.rider
        team = entry.team or rider.team

        selection_count = rider_usage.get(rider.id, 0)
        is_backup = backup_selection and backup_selection.rider and rider.id == backup_selection.rider.rider.id

        is_unavailable = (
            is_backup
            or selection_count >= rider_limit
            or rider.id in dnf_riders
        )

        team_riders[team].append({
            'id': rider.id,
            'start_number': entry.start_number,
            'rider_name': rider.rider_name,
            'team': team.short_name if team and team.short_name else (team.name if team else str(team)),
            'team_code': team.code if team else "UNK",
            'is_dnf': rider.id in dnf_riders,
            'is_backup': is_backup,
            'selection_count': selection_count,
            'is_unavailable': is_unavailable,
        })

    backup_riders_data = []
    sorted_teams = sorted(
        team_riders.items(),
        key=lambda item: min(
            [r['start_number'] for r in item[1] if r['start_number'] is not None] or [9999]
        )
    )

    for team, members in sorted_teams:
        backup_riders_data.append({
            'team': team.short_name if team and team.short_name else (team.name if team else str(team)),
            'riders': sorted(members, key=lambda x: x['start_number'] or 9999)
        })

    countdown_data = [
        {
            'stage_number': item['stage'].stage_number,
            'deadline_iso': item['deadline_iso'],
        }
        for item in stage_data
    ]

    return render(request, 'rider_selection.html', {
        'stage_data': stage_data,
        'total_gc_time': total_gc_time,
        'backup_selection': backup_selection,
        'backup_locked': backup_locked,
        'backup_riders': backup_riders_data,
        'rider_limit': rider_limit,
        'race': race,
        'countdown_data': countdown_data,
    })


@require_POST
@login_required
def save_selection(request, stage_id):
    rider_id = request.POST.get("rider_id")
    stage = get_object_or_404(Stage, id=stage_id)
    user = request.user

    # Handle empty rider selection
    if not rider_id:
        # Optionally: delete the selection if one exists
        PlayerSelection.objects.filter(player=user, stage=stage).delete()
        return redirect('rider_selection')

    rider = get_object_or_404(Rider, id=rider_id)

    # Create or update the user's player selection
    selection, created = PlayerSelection.objects.get_or_create(
        player=user,
        stage=stage,
        defaults={'rider': rider}
    )

    if not created:
        selection.rider = rider
        selection.save()

    return redirect('rider_selection')


@login_required
def leaderboard(request, race_slug, year):
    race = get_object_or_404(Race, url_reference=race_slug, year=year)
    stages = Stage.objects.filter(race=race).order_by('stage_date', 'stage_number')

    # GC standings from real race
    stages_with_gc = StageResult.objects.filter(
        stage__in=stages,
        gc_rank__isnull=False
    ).values('stage').distinct()

    most_recent_stage = None
    if stages_with_gc:
        latest_stage_id = max(stage['stage'] for stage in stages_with_gc)
        most_recent_stage = Stage.objects.get(id=latest_stage_id)

    top_10_riders = []
    if most_recent_stage:
        top_10_riders = StageResult.objects.filter(
            stage=most_recent_stage,
            gc_rank__isnull=False
        ).order_by('gc_rank')[:10]
    
    gc_leader_time = None
    if top_10_riders:
        gc_leader_time = top_10_riders[0].gc_time

    gc_data = []
    for result in top_10_riders:
        time = result.gc_time
        formatted_gc_time = (
            f"{int(time.total_seconds() // 3600)}:"
            f"{int((time.total_seconds() % 3600) // 60):02}:" 
            f"{int(time.total_seconds() % 60):02}"
        ) if time else "-"
        gc_data.append({
            'name': result.rider.rider_name,
            'team': result.rider.team.code if result.rider.team else "UNK",
            'gc_time': formatted_gc_time,
            'gc_rank': result.gc_rank,
        })

    now = timezone.now()
    latest_locked_stage = None
    for stage in reversed(stages):
        if stage.start_time:
            deadline = timezone.make_aware(datetime.combine(stage.stage_date, stage.start_time))
            if now > deadline:
                latest_locked_stage = stage
                break

    final_stage = stages.last()
    race_finished = StageResult.objects.filter(stage=final_stage).exists()
    uci_points_assigned = PlayerUciPoints.objects.filter(race_participant__race=race).exists()
    uci_points_dict = {}

    if race_finished and uci_points_assigned:
        uci_points_entries = PlayerUciPoints.objects.filter(race_participant__race=race).values_list('race_participant__user_id', 'uci_points')
        uci_points_dict = dict(uci_points_entries)

    participants = RaceParticipant.objects.filter(race=race).select_related('user')
    leaderboard_data = []

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
        total_time = timedelta(0)
        latest_rider_display = "-"
        used_backup_display = False

        for stage in stages:
            result = None
            selection = next((s for s in selections if s.stage_id == stage.id), None)
            used_backup = False
            used_fallback = False

            if selection and selection.rider:
                result = StageResult.objects.filter(
                    stage=stage,
                    rider=selection.rider.rider,
                    ranking__isnull=False,
                    finishing_time__isnull=False
                ).first()

            if not result and backup_rider:
                result = StageResult.objects.filter(
                    stage=stage,
                    rider=backup_rider,
                    ranking__isnull=False,
                    finishing_time__isnull=False
                ).first()
                used_backup = result is not None

            if not result:
                result = StageResult.objects.filter(
                    stage=stage,
                    ranking__isnull=False,
                    finishing_time__isnull=False
                ).order_by('-ranking').first()
                used_fallback = result is not None
            
            if latest_locked_stage and stage.id == latest_locked_stage.id:
                rider_to_use = None

                if selection and selection.rider:
                    result = StageResult.objects.filter(
                        stage=stage,
                        rider=selection.rider.rider,
                        ranking__isnull=False,
                        finishing_time__isnull=False
                    ).first()
                    if result:
                        rider_to_use = selection.rider.rider
                        used_backup_display = False

                if not rider_to_use and backup_rider:
                    result = StageResult.objects.filter(
                        stage=stage,
                        rider=backup_rider,
                        ranking__isnull=False,
                        finishing_time__isnull=False
                    ).first()
                    if result:
                        rider_to_use = backup_rider
                        used_backup_display = True

                if not rider_to_use:
                    result = StageResult.objects.filter(
                        stage=stage,
                        ranking__isnull=False,
                        finishing_time__isnull=False
                    ).order_by('-ranking').first()
                    if result:
                        rider_to_use = result.rider
                        used_backup_display = False

                if rider_to_use:
                    latest_rider_display = rider_to_use.rider_name


            if result and result.finishing_time:
                total_time += result.finishing_time - (result.bonus or timedelta(0))

        # Compute time for latest past stage
        latest_stage_time = "-"
        if latest_locked_stage:
            selection = next((s for s in selections if s.stage_id == latest_locked_stage.id), None)
            result = None
            used_backup_time = False
            used_fallback_time = False

            if selection and selection.rider:
                result = StageResult.objects.filter(
                    stage=latest_locked_stage,
                    rider=selection.rider.rider,
                    ranking__isnull=False,
                    finishing_time__isnull=False
                ).first()

            if not result and backup_rider:
                result = StageResult.objects.filter(
                    stage=latest_locked_stage,
                    rider=backup_rider,
                    ranking__isnull=False,
                    finishing_time__isnull=False
                ).first()
                used_backup_time = result is not None

            if not result:
                result = StageResult.objects.filter(
                    stage=latest_locked_stage,
                    ranking__isnull=False,
                    finishing_time__isnull=False
                ).order_by('-ranking').first()
                used_fallback_time = result is not None

            if result and result.finishing_time:
                time = result.finishing_time - (result.bonus or timedelta(0)) if not used_fallback_time else result.finishing_time
                seconds = time.total_seconds()
                latest_stage_time = f"{int(seconds // 3600)}:{int((seconds % 3600) // 60):02}:{int(seconds % 60):02}"


        total_seconds = total_time.total_seconds()
        formatted_total_time = (
            f"{int(total_seconds // 3600)}:{int((total_seconds % 3600) // 60):02}:{int(total_seconds % 60):02}"
            if total_seconds else "0:00:00"
        )

        entry = {
            'player': participant.user,
            'team_name': participant.user.profile.team_name,
            'total_time': formatted_total_time,
            'total_time_obj': total_time,
            'selected_rider': latest_rider_display,
            'used_backup': used_backup_display,
            'num_selections': selections.count(),
            'latest_stage_time': latest_stage_time,
        }

        if race_finished and uci_points_assigned:
            entry['uci_points'] = uci_points_dict.get(participant.user.id)

        leaderboard_data.append(entry)

    leaderboard_data.sort(key=lambda x: x['total_time'])

    return render(request, 'leaderboard.html', {
        'leaderboard_data': leaderboard_data,
        'gc_data': gc_data,
        'race': race,
        'gc_leader_time': gc_leader_time,
    })


@require_POST
@login_required
def save_backup_selection(request):
    rider_id = request.POST.get("rider_id")
    user = request.user

    # If empty, remove the backup rider
    if not rider_id:
        PlayerSelection.objects.filter(player=user, stage=None).delete()
        return redirect('rider_selection')

    rider = get_object_or_404(Rider, id=rider_id)

    # Create or update
    selection, created = PlayerSelection.objects.get_or_create(
        player=user,
        stage=None,
        defaults={'rider': rider}
    )

    if not created:
        selection.rider = rider
        selection.save()

    return redirect('rider_selection')


from django.shortcuts import redirect

@login_required
def profile(request):
    profile = request.user.profile

    # 📝 Handle form submission
    if request.method == 'POST':
        new_team_name = request.POST.get('team_name', '').strip()
        if new_team_name:
            profile.team_name = new_team_name
            profile.save()
        return redirect('profile')  # prevent resubmission on refresh

    # 🧾 Build joined races section
    joined_races = RaceParticipant.objects.filter(user=request.user).select_related('race')
    races_data = []

    for entry in joined_races:
        race = entry.race
        stage_selections = PlayerSelection.objects.filter(race_participant=entry, stage__isnull=False).count()
        has_backup = PlayerSelection.objects.filter(race_participant=entry, stage=None).exists()

        races_data.append({
            'race': race,
            'team_name': profile.team_name,
            'stage_selections': stage_selections,
            'has_backup': has_backup,
            'url_reference': race.url_reference,
            'year': race.year,
        })

    return render(request, 'profile.html', {
        'profile': profile,
        'races_data': races_data,
    })


@login_required
def join_race(request, race_slug, year):
    race = get_object_or_404(Race, url_reference=race_slug, year=year)

    participant, created = RaceParticipant.objects.get_or_create(
        user=request.user,
        race=race
    )

    if created:
        print(f"{request.user.username} joined {race}")
    else:
        print(f"{request.user.username} is already a participant in {race}")
    
    return redirect('rider_selection', race_slug=race.url_reference, year=race.year)


@login_required
def race_list(request):
    today = date.today()
    upcoming_races = Race.objects.filter(start_date__gte=today).order_by('start_date')

    joined_races = RaceParticipant.objects.filter(user=request.user).values_list('race_id', flat=True)

    return render(request, 'game/race_list.html', {
        'upcoming_races': upcoming_races,
        'joined_race_ids': set(joined_races)
    })


@login_required
def total_uci_points(request):
    current_year = date.today().year

    total_uci_points = (
        PlayerUciPoints.objects
        .filter(timestamp__year=current_year)
        .values('race_participant__user__id')
        .annotate(total_points=Sum('uci_points'))
        .order_by('-total_points')
    )

    # Collect usernames and team names
    for entry in total_uci_points:
        user_id = entry['race_participant__user__id']
        user = User.objects.get(id=user_id)
        entry['username'] = user.username
        entry['teamname'] = user.profile.team_name if hasattr(user, 'profile') else ""
        entry['user_id'] = user.id

    # Prepare race-by-race details
    player_details = {}

    details_queryset = (
        PlayerUciPoints.objects
        .filter(timestamp__year=current_year)
        .select_related('race_participant__user', 'race_participant__race')
    )

    for result in details_queryset:
        user_id = result.race_participant.user.id
        race_name = result.race_participant.race.race_name
        gc_rank = result.gc_rank
        uci_points = result.uci_points

        if user_id not in player_details:
            player_details[user_id] = []

        player_details[user_id].append({
            'race_name': race_name,
            'gc_rank': gc_rank,
            'uci_points': uci_points,
        })

    return render(request, 'overall_leaderboard.html', {
        'total_uci_points': total_uci_points,
        'year': current_year,
        'player_details': player_details,
    })


def home(request):
    today = timezone.now().date()
    upcoming_races = Race.objects.filter(start_date__gte=today).order_by('start_date')[:3]
    
    top_players = (
        PlayerUciPoints.objects
        .values('race_participant__user__username')
        .annotate(total_points=Sum('uci_points'))
        .order_by('-total_points')[:5]
    )
    
    return render(request, 'home.html', {
        'upcoming_races': upcoming_races,
        'top_players': top_players,
    })


def how_to_play(request):
    return render(request, 'how_to_play.html')


@require_POST
@login_required
def delete_account(request):
    user = request.user
    user.delete()
    messages.success(request, "Your account has been deleted.")
    return redirect('home')

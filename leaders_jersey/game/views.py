from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from game.models import Race, Stage, Rider, PlayerSelection, StageResult, RaceParticipant, StartlistEntry
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.db.models import Sum
from collections import defaultdict
from .forms import CustomUserCreationForm

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

    # Check if the user has joined this race
    try:
        participant = RaceParticipant.objects.get(user=request.user, race=race)
    except RaceParticipant.DoesNotExist:
        return redirect('join_race', race_slug=race_slug, year=year)

    # Handle POST selection
    if request.method == 'POST':
        rider_id = request.POST.get('rider_id')
        stage_id = request.POST.get('stage_id')

        if rider_id:
            rider = Rider.objects.get(id=rider_id)

            if not stage_id:
                PlayerSelection.objects.update_or_create(
                    race_participant=participant,
                    stage=None,
                    defaults={'rider': rider}
                )
            else:
                stage = Stage.objects.get(id=stage_id)
                PlayerSelection.objects.update_or_create(
                    race_participant=participant,
                    stage=stage,
                    defaults={'rider': rider}
                )

            return redirect(request.path)

    # Get stages for this race
    stages = Stage.objects.filter(race=race).exclude(stage_number__isnull=True).order_by('stage_date', 'stage_number')
    race_length = len(stages)
    rider_limit = 1 if race_length <= 8 else 2 if race_length <= 14 else 3

    # Get riders from the startlist
    entries = StartlistEntry.objects.filter(race=race).select_related('rider', 'team').order_by('start_number')
    riders = [entry.rider for entry in entries]

    dnf_riders = StageResult.objects.filter(
        stage__race=race,
        finishing_time__isnull=True
    ).values_list('rider_id', flat=True)

    # Player selections
    player_selections = PlayerSelection.objects.filter(
        race_participant=participant,
        stage__in=stages,
        stage__is_canceled=False
    ).select_related('stage', 'rider')

    selection_lookup = {sel.stage_id: sel for sel in player_selections}
    selected_stage_rider_ids = {sel.rider.id for sel in player_selections if sel.rider and sel.stage}

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

    # --- Stage data ---
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
            result = StageResult.objects.filter(stage=stage, rider=selected_rider).first()

        if not result and backup_selection and backup_selection.rider:
            result = StageResult.objects.filter(stage=stage, rider=backup_selection.rider).first()
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

    # --- Rider usage ---
    rider_usage = {}
    for selection in player_selections:
        if selection.rider:
            rider_id = selection.rider.id
            rider_usage[rider_id] = rider_usage.get(rider_id, 0) + 1

    # --- Build modal data ---
    team_riders = defaultdict(list)
    for entry in entries:
        rider = entry.rider
        team = entry.team or rider.team

        selection_count = rider_usage.get(rider.id, 0)
        is_backup = backup_selection and backup_selection.rider and rider.id == backup_selection.rider.id
        is_unavailable = is_backup or selection_count >= rider_limit or rider.id in selected_stage_rider_ids

        team_riders[team].append({
            'id': rider.id,
            'start_number': entry.start_number,
            'rider_name': rider.rider_name,
            'team_name': team.name if team else "Unknown",
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
            'team': team.name if team else str(team),
            'riders': sorted(members, key=lambda x: x['start_number'] or 9999)
        })

    return render(request, 'rider_selection.html', {
        'stage_data': stage_data,
        'total_gc_time': total_gc_time,
        'backup_selection': backup_selection,
        'backup_locked': backup_locked,
        'backup_riders': backup_riders_data,
        'rider_limit': rider_limit,
        'race': race,
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
    stages = Stage.objects.filter(race=race)

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

    # Player leaderboard using RaceParticipant
    participants = RaceParticipant.objects.filter(race=race).select_related('user')
    leaderboard_data = []

    for participant in participants:
        selections = PlayerSelection.objects.filter(
            race_participant=participant,
            stage__in=stages
        ).select_related('stage', 'rider')

        backup_selection = PlayerSelection.objects.filter(
            race_participant=participant,
            stage=None
        ).first()

        backup_rider = backup_selection.rider if backup_selection else None
        total_time = timedelta(0)

        for stage in stages:
            result = None
            selection = next((s for s in selections if s.stage_id == stage.id), None)

            if selection and selection.rider:
                result = StageResult.objects.filter(stage=stage, rider=selection.rider).first()

            if not result and backup_rider:
                result = StageResult.objects.filter(stage=stage, rider=backup_rider).first()

            if not result:
                result = StageResult.objects.filter(stage=stage).order_by('-ranking').first()

            if result:
                total_time += result.finishing_time - result.bonus

        total_seconds = total_time.total_seconds()
        formatted_total_time = (
            f"{int(total_seconds // 3600)}:{int((total_seconds % 3600) // 60):02}:{int(total_seconds % 60):02}"
            if total_seconds else "0:00:00"
        )

        leaderboard_data.append({
            'player': participant.user,
            'team_name': participant.user.profile.team_name,
            'total_time': formatted_total_time,
            'num_selections': selections.count(),
        })

    leaderboard_data.sort(key=lambda x: x['total_time'])

    return render(request, 'leaderboard.html', {
        'leaderboard_data': leaderboard_data,
        'gc_data': gc_data,
        'race': race,
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
    
    return redirect('race_list')


@login_required
def race_list(request):
    today = date.today()
    upcoming_races = Race.objects.filter(start_date__gte=today).order_by('start_date')

    joined_races = RaceParticipant.objects.filter(user=request.user).values_list('race_id', flat=True)

    return render(request, 'game/race_list.html', {
        'upcoming_races': upcoming_races,
        'joined_race_ids': set(joined_races)
    })
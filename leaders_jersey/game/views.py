from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from game.models import Race, Stage, Rider, PlayerSelection, StageResult
from datetime import datetime, time, timedelta
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
import pandas as pd
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
def rider_selection(request):
    if request.method == 'POST':
        rider_id = request.POST.get('rider_id')
        stage_id = request.POST.get('stage_id')

        if rider_id:
            rider = Rider.objects.get(id=rider_id)

            if not stage_id:
                # Backup rider
                PlayerSelection.objects.update_or_create(
                    player=request.user,
                    stage=None,
                    defaults={'rider': rider}
                )
            else:
                # Stage rider
                stage = Stage.objects.get(id=stage_id)
                PlayerSelection.objects.update_or_create(
                    player=request.user,
                    stage=stage,
                    defaults={'rider': rider}
                )

            return redirect(request.path)

    # Get current race and stages
    current_race = Race.objects.order_by('-year').first()
    if current_race:
        stages = Stage.objects.filter(race=current_race).order_by('stage_date', 'stage_number')
    else:
        stages = []

    race_length = len(stages)
    rider_limit = 1 if race_length <= 8 else 2 if race_length <= 14 else 3

    riders = Rider.objects.filter(is_participating=True).order_by('start_number')
    dnf_riders = StageResult.objects.filter(
        stage__race=current_race,
        finishing_time__isnull=True
    ).values_list('rider_id', flat=True)

    player_selections = PlayerSelection.objects.filter(
        player=request.user,
        stage__in=stages,
        stage__is_canceled=False
    ).select_related('stage', 'rider')

    selected_stage_rider_ids = set(sel.rider.id for sel in player_selections if sel.rider and sel.stage is not None)
    selection_lookup = {sel.stage_id: sel for sel in player_selections}

    backup_selection = PlayerSelection.objects.filter(player=request.user, stage=None).first()
    backup_rider_id = backup_selection.rider.id if backup_selection and backup_selection.rider else None
    backup_rider_dnf = backup_rider_id in dnf_riders if backup_rider_id else False

    if stages:
        stage1_start = timezone.make_aware(datetime.combine(stages[0].stage_date, stages[0].start_time))
        backup_locked = timezone.now() > stage1_start and not backup_rider_dnf
    else:
        backup_locked = True

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
            try:
                result = StageResult.objects.get(stage=stage, rider=selected_rider)
            except StageResult.DoesNotExist:
                pass

        if not result and selection and backup_selection and backup_selection.rider:
            try:
                result = StageResult.objects.get(stage=stage, rider=backup_selection.rider)
                used_backup = True
            except StageResult.DoesNotExist:
                pass

        if not result:
            last_result = StageResult.objects.filter(stage=stage).order_by('-ranking').first()
            if last_result:
                result = last_result
                used_fallback = True

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

    # --- Calculate rider usage ---
    rider_usage = {}
    for selection in player_selections:
        if selection.rider:
            rider_id = selection.rider.id
            rider_usage[rider_id] = rider_usage.get(rider_id, 0) + 1

    # --- Build teams and riders for modal ---
    team_riders = defaultdict(list)
    for rider in riders:
        selection_count = rider_usage.get(rider.id, 0)
        is_backup = backup_selection and backup_selection.rider and rider.id == backup_selection.rider.id

        # ✨ Mark unavailable riders
        is_unavailable = False
        if is_backup or selection_count >= rider_limit or rider.id in selected_stage_rider_ids:
            is_unavailable = True

        team_riders[rider.team].append({
            'id': rider.id,
            'start_number': rider.start_number,
            'rider_name': rider.rider_name,
            'team_name': rider.team.name if rider.team else "Unknown",
            'team_code': rider.team.code if rider.team else "UNK",
            'is_dnf': rider.id in dnf_riders,
            'is_backup': is_backup,
            'selection_count': selection_count,
            'is_unavailable': is_unavailable,
        })

    backup_riders_data = []
    sorted_teams = sorted(
        team_riders.items(),
        key=lambda item: min(r['start_number'] for r in item[1])
    )

    for team_name, members in sorted_teams:
        backup_riders_data.append({
            'team': team_name.name if hasattr(team_name, 'name') else str(team_name),
            'riders': sorted(members, key=lambda x: x['start_number'])
        })

    return render(request, 'rider_selection.html', {
        'stage_data': stage_data,
        'total_gc_time': total_gc_time,
        'backup_selection': backup_selection,
        'backup_locked': backup_locked,
        'backup_riders': backup_riders_data,
        'rider_limit': rider_limit,
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


from datetime import timedelta

@login_required
def leaderboard(request):
    current_race = Race.objects.order_by('-year').first()
    stages = Stage.objects.filter(race=current_race)

    # Get the latest stage that has GC data
    stages_with_gc = StageResult.objects.filter(
        stage__in=stages,
        gc_rank__isnull=False
    ).values('stage').distinct()

    if stages_with_gc:
        latest_stage_with_gc_id = max(stage['stage'] for stage in stages_with_gc)
        most_recent_stage = Stage.objects.get(id=latest_stage_with_gc_id)
    else:
        most_recent_stage = None

    # Get top 10 GC riders after that stage
    top_10_riders = StageResult.objects.filter(
        stage=most_recent_stage,
        gc_rank__isnull=False
    ).order_by('gc_rank')[:10]

    # ✅ Collect GC data for display (with pretty formatting!)
    gc_data = []
    for result in top_10_riders:
        if result.gc_time:
            total_seconds = result.gc_time.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
            formatted_gc_time = f"{hours}:{minutes:02}:{seconds:02}"
        else:
            formatted_gc_time = "-"

        gc_rider_data = {
            'name': result.rider.rider_name,
            'team': result.rider.team.code if result.rider.team else "UNK",
            'gc_time': formatted_gc_time,
            'gc_rank': result.gc_rank,
        }

        gc_data.append(gc_rider_data)

    # 🎮 Game leaderboard
    users_with_selections = User.objects.filter(
        selections__stage__in=stages
    ).distinct()

    leaderboard_data = []

    for user in users_with_selections:
        total_time = timedelta(0)

        # Get selections and backup for this user
        selections = PlayerSelection.objects.filter(
            player=user,
            stage__in=stages
        ).select_related('stage', 'rider')

        backup_selection = PlayerSelection.objects.filter(player=user, stage=None).first()
        backup_rider = backup_selection.rider if backup_selection else None

        # Lookup per stage
        stage_lookup = {s.stage_id: s for s in selections}

        for stage in stages:
            result = None
            used_fallback = False

            # 1. Check selected rider
            selection = stage_lookup.get(stage.id)
            if selection and selection.rider:
                try:
                    result = StageResult.objects.get(stage=stage, rider=selection.rider)
                except StageResult.DoesNotExist:
                    result = None

            # 2. Check backup rider
            if not result and backup_rider:
                try:
                    result = StageResult.objects.get(stage=stage, rider=backup_rider)
                except StageResult.DoesNotExist:
                    result = None

            # 3. Fallback: last classified finisher
            if not result:
                result = StageResult.objects.filter(stage=stage).order_by('-ranking').first()
                used_fallback = True

            # 4. Add time
            if result:
                if used_fallback:
                    total_time += result.finishing_time  # no bonus
                else:
                    total_time += result.finishing_time - result.bonus
        total_seconds = total_time.total_seconds()

        if total_seconds > 0:
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
            formatted_total_time = f"{hours}:{minutes:02}:{seconds:02}"
        else:
            formatted_total_time = "0:00:00"

        leaderboard_data.append({
            'player': user,
            'team_name': user.profile.team_name,
            'total_time': formatted_total_time,
            'num_selections': selections.count()
        })

    leaderboard_data.sort(key=lambda x: x['total_time'])

    return render(request, 'leaderboard.html', {
        'leaderboard_data': leaderboard_data,
        'gc_data': gc_data,
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


@login_required
def profile(request):
    if request.method == 'POST':
        team_name = request.POST.get('team_name')
        request.user.profile.team_name = team_name
        request.user.profile.save()
        messages.success(request, '✅ Team name updated!')

        return redirect('profile')

    return render(request, 'profile.html', {})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from game.models import Race, Stage, Rider, PlayerSelection, StageResult
from datetime import datetime, time, timedelta
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


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

    # Get the most recent race
    current_race = Race.objects.order_by('-year').first()

    # Retrieve the stages for this race
    if current_race:
        stages = Stage.objects.filter(race=current_race).order_by('stage_date', 'stage_number')
    else:
        stages = []
    
    # Define selection limit per rider
    race_length = len(stages)

    if race_length <= 8:
        rider_limit = 1
    elif race_length <= 14:
        rider_limit = 2
    else:
        rider_limit = 3
    
    # Get all riders to show in the dropdown
    riders = Rider.objects.filter(is_participating=True).order_by('rider_name')

    # Get all riders who did not finish in the last stage (or a previous stage)
    dnf_riders = StageResult.objects.filter(
        stage__race=current_race,
        finishing_time__isnull=True
    ).values_list('rider_id', flat=True)

    # To make sure the dnf riders are at the bottom
    eligible_riders = riders.exclude(id__in=dnf_riders)
    dnf_riders_qs = riders.filter(id__in=dnf_riders)
    sorted_riders = list(eligible_riders) + list(dnf_riders_qs)

    # Get all PlayerSelections for this user and race
    player_selections = PlayerSelection.objects.filter(
        player=request.user,
        stage__in=stages
    ).select_related('stage', 'rider')

    # Count number of times a rider is selected:
    rider_usage = {}
    for selection in player_selections:
        if selection.rider:
            rider_id = selection.rider.id
            rider_usage[rider_id] = rider_usage.get(rider_id, 0) + 1

    # Get all selected stage rider IDs
    selected_stage_rider_ids = set(sel.rider.id for sel in player_selections if sel.rider and sel.stage is not None)

    # Build a lookup dictionary: { stage_id: selection }
    selection_lookup = { sel.stage_id: sel for sel in player_selections }

    # Get the backup rider selection (stage=None)
    backup_selection = PlayerSelection.objects.filter(player=request.user, stage=None).first()

    # Get the backup rider ID
    backup_rider_id = backup_selection.rider.id if backup_selection and backup_selection.rider else None

    # Allow changing the backup rider if current one DNF
    backup_rider_dnf = backup_rider_id in dnf_riders if backup_rider_id else False

    # Determine stage 1 deadline
    if stages:
        stage1_deadline = timezone.make_aware(datetime.combine(stages[0].stage_date, time(hour=12)))
        backup_locked = timezone.now() > stage1_deadline and not backup_rider_dnf
    else:
        backup_locked = True

    stage_data = []
    total_gc_time = timedelta(0)

    # Define selection deadline for each stage (12:00 by default)
    for stage in stages:
        deadline = timezone.make_aware(datetime.combine(stage.stage_date, stage.start_time))
        locked = timezone.now() > deadline
        # locked = False  # This line is just for testing with a race from the past. Remove it if you want it to operate in the present.

        deadline_iso = deadline.isoformat()

        # Check if user already made a selection for this stage
        selection = selection_lookup.get(stage.id)
        selected_rider = selection.rider if selection else None

        # Check result logic with fallback and backup rider
        result = None
        used_backup = False
        used_fallback = False
        result_source = None

        if selected_rider:
            result_source = None
            try:
                result = StageResult.objects.get(stage=stage, rider=selected_rider)
                result_source = "selection"
            except StageResult.DoesNotExist:
                result = None

        # Try backup rider if main rider has no result
        if not result and backup_selection and backup_selection.rider:
            try:
                result = StageResult.objects.get(stage=stage, rider=backup_selection.rider)
                used_backup = True
                result_source = "backup"
            except StageResult.DoesNotExist:
                pass

        # Final fallback to last finisher if both failed
        if not result:
            last_result = StageResult.objects.filter(stage=stage).order_by('-ranking').first()
            if last_result:
                result = last_result
                used_fallback = True
                result_source = "last finisher"

        if result:
            if used_fallback:
                total_gc_time += result.finishing_time  # no bonus
            else:
                total_gc_time += result.finishing_time - result.bonus


        stage_data.append({
            'stage': stage,
            'locked': locked,
            'selection': selected_rider,
            'result': result,
            'riders': riders.exclude(id=backup_rider_id) if backup_rider_id else riders,
            'sorted_riders': sorted_riders,
            'deadline': deadline_iso,
            'used_backup': used_backup,
            'used_fallback': used_fallback,
            'result_source': result_source
        })

    return render(request, 'rider_selection.html', {
        'stage_data': stage_data,
        'total_gc_time': total_gc_time,
        'backup_selection': backup_selection,
        'backup_locked': backup_locked,
        'backup_riders': riders.exclude(id__in=selected_stage_rider_ids),
        'dnf_riders': dnf_riders,
        'rider_usage': rider_usage,
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


@login_required
def leaderboard(request):
    current_race = Race.objects.order_by('-year').first()
    stages = Stage.objects.filter(race=current_race)

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

        leaderboard_data.append({
            'player': user,
            'total_time': total_time,
            'num_selections': selections.count()
        })

    leaderboard_data.sort(key=lambda x: x['total_time'])

    return render(request, 'leaderboard.html', {
        'leaderboard_data': leaderboard_data
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

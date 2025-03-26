from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from game.models import Race, Stage, Rider, PlayerSelection, StageResult
from datetime import datetime, time
from django.utils import timezone
from django.views.decorators.http import require_POST

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
        stages = Stage.objects.filter(race=current_race).order_by('stage_number')
    else:
        stages = []

    # Get all riders to show in the dropdown
    riders = Rider.objects.filter(is_participating=True).order_by('start_number')

    # Get all PlayerSelections for this user and race
    player_selections = PlayerSelection.objects.filter(
        player=request.user,
        stage__in=stages
    ).select_related('stage', 'rider')

    # Build a lookup dictionary: { stage_id: selection }
    selection_lookup = { sel.stage_id: sel for sel in player_selections }
    
    stage_data = []

    # Define 12:00 selection deadline for each stage
    for stage in stages:
        deadline = timezone.make_aware(datetime.combine(stage.stage_date, time(hour=12)))
        locked = timezone.now() > deadline
        # locked = False  # This line is just for testing with a race from the past. Remove it if you want it to operate in the present.

        # Check if user already made a selection for this stage
        selection = selection_lookup.get(stage.id)
        selected_rider = selection.rider if selection else None

        # Check if the stage result exists for this rider
        result = None
        if selection:
            try:
                result = StageResult.objects.get(stage=stage, rider=selection.rider)
            except StageResult.DoesNotExist:
                result = None

        stage_data.append({
            'stage': stage,
            'locked': locked,
            'selection': selected_rider,
            'result': result,
            'riders': riders
        })
    
    return render(request, 'rider_selection.html', {
        'stage_data': stage_data
    })


@require_POST
def save_selection(request, stage_id):
    rider_id = request.POST.get("rider_id")

    # Get the Stage using stage_id from the URL, Rider object from the form and current user (already available)
    stage = get_object_or_404(Stage, id=stage_id)
    rider = get_object_or_404(Rider, id=rider_id)
    user = request.user

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


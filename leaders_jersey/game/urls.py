from django.urls import path
from .views import CustomLoginView, custom_logout_view, home, register, profile, rider_selection, save_selection, leaderboard, save_backup_selection, race_list, join_race, total_uci_points, how_to_play

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('', home, name='home'),
    path('profile/', profile, name='profile'),
    path('<slug:race_slug>/<int:year>/rider_selection/', rider_selection, name='rider_selection'),
    path('<slug:race_slug>/<int:year>/save_selection/<int:stage_id>/', save_selection, name='save_selection'),
    path('<slug:race_slug>/<int:year>/leaderboard/', leaderboard, name='leaderboard'),
    path('<slug:race_slug>/<int:year>/save_backup/', save_backup_selection, name='save_backup_selection'),
    path('races/', race_list, name='race_list'),
    path('join/<slug:race_slug>/<int:year>/', join_race, name='join_race'),
    path('overall_leaderboard/', total_uci_points, name='overall_leaderboard'),
    path('how-to-play/', how_to_play, name='how_to_play'),
]
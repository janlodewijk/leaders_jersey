from django.urls import path
from .views import CustomLoginView, custom_logout_view, home, register, profile, rider_selection, save_selection, leaderboard, save_backup_selection

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('', home, name='home'),
    path('profile/', profile, name='profile'),
    path('rider_selection/', rider_selection, name='rider_selection'),
    path('save_selection/<int:stage_id>/', save_selection, name='save_selection'),
    path('leaderboard/', leaderboard, name='leaderboard'),
    path('save_backup/', save_backup_selection, name='save_backup_selection'),
]
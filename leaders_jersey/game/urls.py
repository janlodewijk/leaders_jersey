from django.urls import path
from .views import CustomLoginView, custom_logout_view, home, register, profile

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('', home, name='home'),
    path('profile/', profile, name='profile')
]
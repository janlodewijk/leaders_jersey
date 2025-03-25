from django.urls import path
from . import views
from .views import CustomLoginView, custom_logout_view

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
]
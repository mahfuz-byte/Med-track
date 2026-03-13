from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/<int:pk>/', views.profile_detail, name='profile_detail'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/review/<int:pk>/', views.review_doctor, name='review_doctor'),
    path('admin-panel/approve/<int:pk>/', views.approve_doctor, name='approve_doctor'),
    path('admin-panel/reject/<int:pk>/', views.reject_doctor, name='reject_doctor'),
]

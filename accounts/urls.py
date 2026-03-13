from django.urls import path
from . import views

urlpatterns = [
    path('register/step1/', views.register_step1, name='register_step1'),
    path('register/step2/', views.register_step2, name='register_step2'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('pending/', views.pending_view, name='pending'),

    # Profile & password
    path('profile/edit/', views.profile_update, name='profile_update'),
    path('change-password/', views.change_password, name='change_password'),

    # Forgot password flow
    path('password-reset/', views.DoctorPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.DoctorPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', views.DoctorPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', views.DoctorPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
)
from django.urls import reverse_lazy
from .forms import (
    Step1Form, Step2Form, ProfileUpdateForm,
    PasswordChangeForm, DoctorPasswordResetForm, DoctorSetPasswordForm,
)
from .models import DoctorProfile
from .decorators import verified_required


# ── Registration ───────────────────────────────────────────────────────────────

def register_step1(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = Step1Form(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            user.is_active = False
            user.save()
            request.session['pending_user_id'] = user.pk
            return redirect('register_step2')
    else:
        form = Step1Form()
    return render(request, 'accounts/register_step1.html', {'form': form})


def register_step2(request):
    user_id = request.session.get('pending_user_id')
    if not user_id:
        return redirect('register_step1')
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return redirect('register_step1')

    if request.method == 'POST':
        form = Step2Form(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            # Sync email to User so password reset emails can be delivered
            user.email = profile.email
            user.save()
            del request.session['pending_user_id']
            return redirect('pending')
    else:
        form = Step2Form()
    return render(request, 'accounts/register_step2.html', {'form': form})


# ── Login / Logout ─────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        try:
            user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            user_obj = None

        if user_obj and user_obj.is_staff:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                error = "Invalid credentials."
        else:
            was_inactive = user_obj and not user_obj.is_active
            if was_inactive:
                user_obj.is_active = True
                user_obj.save()
            user = authenticate(request, username=username, password=password)
            if was_inactive and user_obj:
                user_obj.is_active = False
                user_obj.save()

            if user is None:
                error = "Invalid credentials."
            else:
                try:
                    profile = user.doctor_profile
                except Exception:
                    error = "No doctor profile found."
                    return render(request, 'accounts/login.html', {'error': error})

                if profile.is_rejected:
                    error = "Your registration was rejected. Please contact the admin."
                elif not profile.is_verified:
                    error = "Your account is awaiting admin approval."
                else:
                    user.is_active = True
                    user.save()
                    login(request, user)
                    return redirect('dashboard')

    return render(request, 'accounts/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


def pending_view(request):
    return render(request, 'accounts/pending.html')


# ── Profile Update ─────────────────────────────────────────────────────────────

@login_required
@verified_required
def profile_update(request):
    profile = request.user.doctor_profile
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            updated = form.save()
            # Keep User.email in sync for password reset emails
            request.user.email = updated.email
            request.user.save()
            return render(request, 'accounts/profile_edit.html', {
                'form': form, 'success': True
            })
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'accounts/profile_edit.html', {'form': form})


# ── Change Password ────────────────────────────────────────────────────────────

@login_required
@verified_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            if not request.user.check_password(form.cleaned_data['current_password']):
                form.add_error('current_password', 'Current password is incorrect.')
            else:
                request.user.set_password(form.cleaned_data['new_password'])
                request.user.save()
                # Keep the user logged in after password change
                update_session_auth_hash(request, request.user)
                return render(request, 'accounts/change_password.html', {
                    'form': PasswordChangeForm(), 'success': True
                })
    else:
        form = PasswordChangeForm()
    return render(request, 'accounts/change_password.html', {'form': form})


# ── Forgot Password (class-based, using Django's built-in token mechanism) ─────

class DoctorPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.txt'
    subject_template_name = 'accounts/password_reset_subject.txt'
    form_class = DoctorPasswordResetForm
    success_url = reverse_lazy('password_reset_done')


class DoctorPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class DoctorPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = DoctorSetPasswordForm
    success_url = reverse_lazy('password_reset_complete')


class DoctorPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'

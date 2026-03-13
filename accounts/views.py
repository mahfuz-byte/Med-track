from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import Step1Form, Step2Form
from .models import DoctorProfile


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
            del request.session['pending_user_id']
            return redirect('pending')
    else:
        form = Step2Form()
    return render(request, 'accounts/register_step2.html', {'form': form})


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
            # Temporarily activate for authentication check (doctor may be inactive/pending)
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

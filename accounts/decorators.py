from functools import wraps
from django.shortcuts import redirect


def verified_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            profile = request.user.doctor_profile
        except Exception:
            # Superusers / staff without a profile pass through
            if request.user.is_staff:
                return view_func(request, *args, **kwargs)
            return redirect('login')
        if not profile.is_verified:
            return redirect('pending')
        return view_func(request, *args, **kwargs)
    return wrapper

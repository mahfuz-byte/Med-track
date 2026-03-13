from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import verified_required
from accounts.models import DoctorProfile


@login_required
@verified_required
def dashboard(request):
    profiles = DoctorProfile.objects.filter(is_verified=True)

    specialization = request.GET.get('specialization', '').strip()
    workplace = request.GET.get('workplace', '').strip()
    graduation_year = request.GET.get('graduation_year', '').strip()
    name = request.GET.get('name', '').strip()

    if specialization:
        profiles = profiles.filter(specialization__icontains=specialization)
    if workplace:
        profiles = profiles.filter(workplace__icontains=workplace)
    if graduation_year:
        profiles = profiles.filter(graduation_year=graduation_year)
    if name:
        profiles = profiles.filter(user__username__icontains=name)

    context = {
        'profiles': profiles,
        'specialization': specialization,
        'workplace': workplace,
        'graduation_year': graduation_year,
        'name': name,
    }
    return render(request, 'doctors/dashboard.html', context)


@login_required
@verified_required
def profile_detail(request, pk):
    profile = get_object_or_404(DoctorProfile, pk=pk, is_verified=True)
    return render(request, 'doctors/profile_detail.html', {'profile': profile})

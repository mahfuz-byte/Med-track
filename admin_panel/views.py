from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from accounts.models import DoctorProfile
import logging

logger = logging.getLogger(__name__)


@staff_member_required(login_url='/login/')
def admin_dashboard(request):
    pending = DoctorProfile.objects.filter(is_verified=False, is_rejected=False).select_related('user')
    approved = DoctorProfile.objects.filter(is_verified=True).select_related('user')
    rejected = DoctorProfile.objects.filter(is_rejected=True).select_related('user')
    return render(request, 'admin_panel/dashboard.html', {
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
    })


@staff_member_required(login_url='/login/')
def approve_doctor(request, pk):
    profile = get_object_or_404(DoctorProfile, pk=pk)
    profile.is_verified = True
    profile.is_rejected = False
    profile.user.is_active = True
    profile.user.save()
    profile.save()
    try:
        send_mail(
            subject='Your MedTrack registration has been approved!',
            message=(
                f"Dear Dr. {profile.user.username},\n\n"
                "Congratulations! Your registration on MedTrack has been approved.\n"
                "You can now log in and access the doctor directory.\n\n"
                "Best regards,\nMedTrack Admin"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[profile.email],
            fail_silently=False,
        )
    except (BadHeaderError, Exception) as e:
        logger.error("Approval email failed for doctor %s: %s", profile.user.username, e)
    return redirect('admin_dashboard')


@staff_member_required(login_url='/login/')
def review_doctor(request, pk):
    profile = get_object_or_404(DoctorProfile, pk=pk)
    return render(request, 'admin_panel/review_doctor.html', {'profile': profile})


@staff_member_required(login_url='/login/')
def reject_doctor(request, pk):
    profile = get_object_or_404(DoctorProfile, pk=pk)
    profile.is_rejected = True
    profile.save()
    try:
        send_mail(
            subject='MedTrack registration update',
            message=(
                f"Dear Dr. {profile.user.username},\n\n"
                "We regret to inform you that your registration on MedTrack could not be approved at this time.\n"
                "Please contact the admin for further information.\n\n"
                "Best regards,\nMedTrack Admin"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[profile.email],
            fail_silently=False,
        )
    except (BadHeaderError, Exception) as e:
        logger.error("Rejection email failed for doctor %s: %s", profile.user.username, e)
    return redirect('admin_dashboard')

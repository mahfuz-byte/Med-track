from django.db import models
from django.contrib.auth.models import User


class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    graduation_year = models.IntegerField()
    specialization = models.CharField(max_length=200)
    workplace = models.CharField(max_length=300)
    degrees = models.TextField(help_text="List degrees separated by commas")
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    address = models.TextField()
    visiting_hours = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='doctor_photos/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} — {self.specialization}"

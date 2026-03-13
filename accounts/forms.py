from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from .models import DoctorProfile


class Step1Form(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        pw2 = cleaned.get('password_confirm')
        if pw and pw2 and pw != pw2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned


class Step2Form(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        exclude = ['user', 'is_verified', 'is_rejected', 'created_at']
        widgets = {
            'graduation_year': forms.NumberInput(attrs={'placeholder': 'e.g. 2010'}),
            'specialization': forms.TextInput(attrs={'placeholder': 'e.g. Cardiology'}),
            'workplace': forms.TextInput(attrs={'placeholder': 'Hospital / Clinic name'}),
            'degrees': forms.TextInput(attrs={'placeholder': 'e.g. MBBS, MD, FRCS'}),
            'email': forms.EmailInput(attrs={'placeholder': 'your@email.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '+20 1xx xxx xxxx'}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Your clinic address'}),
            'visiting_hours': forms.TextInput(attrs={'placeholder': 'e.g. Mon–Fri 9am–5pm'}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        exclude = ['user', 'is_verified', 'is_rejected', 'created_at']
        widgets = {
            'graduation_year': forms.NumberInput(attrs={'placeholder': 'e.g. 2010'}),
            'specialization': forms.TextInput(attrs={'placeholder': 'e.g. Cardiology'}),
            'workplace': forms.TextInput(attrs={'placeholder': 'Hospital / Clinic name'}),
            'degrees': forms.TextInput(attrs={'placeholder': 'e.g. MBBS, MD, FRCS'}),
            'email': forms.EmailInput(attrs={'placeholder': 'your@email.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '+20 1xx xxx xxxx'}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Your clinic address'}),
            'visiting_hours': forms.TextInput(attrs={'placeholder': 'e.g. Mon–Fri 9am–5pm'}),
        }


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Current password'})
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New password'}),
        min_length=8,
    )
    new_password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'})
    )

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('new_password')
        pw2 = cleaned.get('new_password_confirm')
        if pw and pw2 and pw != pw2:
            raise forms.ValidationError("New passwords do not match.")
        return cleaned


# Only lets verified doctors reset their password
class DoctorPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        try:
            profile = DoctorProfile.objects.get(email__iexact=email, is_verified=True)
            user = profile.user
            if user.is_active and user.has_usable_password():
                yield user
        except DoctorProfile.DoesNotExist:
            pass  # Reveal nothing about unregistered emails


class DoctorSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget = forms.PasswordInput(
            attrs={'placeholder': 'New password'}
        )
        self.fields['new_password2'].widget = forms.PasswordInput(
            attrs={'placeholder': 'Confirm new password'}
        )

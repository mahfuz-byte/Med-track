from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('login'), name='home'),
    path('django-admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('doctors.urls')),
    path('', include('admin_panel.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

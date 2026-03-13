import os
import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medtrack.settings')
django.setup()

app = get_wsgi_application()

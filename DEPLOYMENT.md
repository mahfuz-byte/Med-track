# MedTrack — Deployment Guide

## Checklist

- [ ] Move `SECRET_KEY` and `EMAIL_HOST_PASSWORD` to `.env`
- [ ] Add `.env` to `.gitignore`
- [ ] Set `DEBUG=False`
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Run `python manage.py collectstatic`
- [ ] Switch to PostgreSQL (optional but recommended)
- [ ] Install and configure whitenoise
- [ ] Create superuser on the production server

---

## 1. Secret Key & Environment Variables

Install python-decouple:
```bash
pip install python-decouple
```

Create a `.env` file in the project root (never commit this file):
```
SECRET_KEY=generate-a-new-random-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
EMAIL_HOST_PASSWORD=dozy anno sujm mnml
```

Update `medtrack/settings.py`:
```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
```

Generate a new secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 2. DEBUG = False + ALLOWED_HOSTS

With `DEBUG=False` you must set `ALLOWED_HOSTS` to your actual domain, otherwise Django rejects all requests:
```
ALLOWED_HOSTS=medtrack.yourdomain.com
```

---

## 3. Database — Switch from SQLite to PostgreSQL

```bash
pip install psycopg2-binary
```

Replace the `DATABASES` block in `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
```

Add to `.env`:
```
DB_NAME=medtrack
DB_USER=medtrack_user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
```

---

## 4. Static Files

Add to `settings.py`:
```python
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

Run before deploying:
```bash
python manage.py collectstatic
```

---

## 5. Whitenoise (Easiest Static File Solution)

Lets Django serve static files safely in production — no Nginx config needed for static.

```bash
pip install whitenoise
```

Add to `MIDDLEWARE` right after `SecurityMiddleware`:
```python
'whitenoise.middleware.WhiteNoiseMiddleware',
```

Add to `settings.py`:
```python
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

---

## 6. Security Headers

Add to `settings.py`:
```python
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
# Enable these only after HTTPS is set up:
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
```

---

## 7. Deployment Platform Options

| Platform | Effort | Cost |
|----------|--------|------|
| Railway | Easiest — push repo, set env vars, done | Free tier |
| Render | Similar to Railway | Free tier |
| PythonAnywhere | Good for Django beginners | Free tier |
| VPS (DigitalOcean / Hetzner) | Full control, needs Nginx + Gunicorn | ~$5/mo |

Run with Gunicorn on any platform:
```bash
pip install gunicorn
gunicorn medtrack.wsgi:application
```

---

## 8. After Deploying

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

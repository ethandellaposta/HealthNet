"""
WSGI config for HealthSite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""
import os
from django.core.wsgi import get_wsgi_application
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HealthSite.settings")
application = get_wsgi_application()

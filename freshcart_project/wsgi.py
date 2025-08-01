# FreshCart/freshcart_project/wsgi.py
# WSGI config for freshcart_project project.

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freshcart_project.settings')

application = get_wsgi_application()

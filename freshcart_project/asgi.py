# FreshCart/freshcart_project/asgi.py
# ASGI config for freshcart_project project.

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freshcart_project.settings')

application = get_asgi_application()


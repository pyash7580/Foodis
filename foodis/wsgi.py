"""
WSGI config for foodis project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')

application = get_wsgi_application()


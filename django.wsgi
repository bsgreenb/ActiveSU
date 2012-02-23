import os
import sys

sys.path.append('/home/ben/sources/django_activity')
sys.path.append('/home/ben/sources')

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

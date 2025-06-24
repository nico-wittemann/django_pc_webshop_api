import os
import sys
import django

# Add root folder to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Correct path to settings.py
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

"""Pytest configuration for Django-X-Clacks-Overhead."""

import os
import sys

import django
from django.conf import settings
# from django.http import HttpResponse
# from django.urls import path

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))


# # Minimal view for testing
# def _test_view(request):
#     return HttpResponse("OK")


# # Minimal URL config
# urlpatterns = [path("", _test_view)]

# Minimal Django settings for testing
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="test-secret-key-not-for-production",
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "rest_framework",
        ],
        ROOT_URLCONF="",
        MIDDLEWARE=[],
        LOGGING_CONFIG=None,
        # Required for pytest-django
        USE_TZ=True,
    )
    django.setup()


# pytest-django configuration
def pytest_configure(config):
    """Configure pytest-django."""
    config.addinivalue_line("markers", "django_db: mark test to use database")


pytest_plugins = ["pytest_django"]

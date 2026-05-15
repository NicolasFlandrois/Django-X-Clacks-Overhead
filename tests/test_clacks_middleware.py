import pytest
from django.http import HttpResponse
from django.test import RequestFactory, override_settings
from rest_framework.test import APIRequestFactory

from clacks import CLACKS_HEADER, DEFAULT_CLACKS_TRIBUTE, ClacksMiddleware

# ─────────────────────────────────────────────────────────────────────────────
# 🛠️ Test Fixtures & Helpers
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def django_rf():
    """Django RequestFactory for middleware tests."""
    return RequestFactory()


@pytest.fixture
def drf_rf():
    """DRF APIRequestFactory for ViewSet/Decorator tests."""
    return APIRequestFactory()


def _get_mock_response(request):
    """Standard get_response callable for middleware."""
    return HttpResponse("OK")


def _setup_viewset_instance(viewset_cls, request, format=None):
    """Helper to properly initialize a DRF ViewSet instance for testing."""
    instance = viewset_cls()
    instance.request = request
    instance.format_kwarg = format
    return instance


# ─────────────────────────────────────────────────────────────────────────────
# 🌐 Middleware Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestClacksMiddleware:
    @override_settings(CLACKS_OVERHEAD=None)
    def test_default_tribute_when_no_settings(self, django_rf):
        mw = ClacksMiddleware(_get_mock_response)
        response = mw(django_rf.get("/"))
        assert response[CLACKS_HEADER] == DEFAULT_CLACKS_TRIBUTE

    @override_settings(CLACKS_OVERHEAD="John Dearheart")
    def test_single_tribute_from_settings(self, django_rf):
        mw = ClacksMiddleware(_get_mock_response)
        response = mw(django_rf.get("/"))
        assert response[CLACKS_HEADER] == "GNU John Dearheart"

    @override_settings(CLACKS_OVERHEAD=["Terry Pratchett", "Alan Turing"])
    def test_multiple_tributes_from_settings(self, django_rf):
        mw = ClacksMiddleware(_get_mock_response)
        response = mw(django_rf.get("/"))
        assert response[CLACKS_HEADER] == "GNU Terry Pratchett, GNU Alan Turing"

    def test_skips_if_header_already_set(self, django_rf):
        """Middleware should respect higher-precedence layers."""

        def custom_get_response(req):
            resp = HttpResponse("OK")
            resp[CLACKS_HEADER] = "GNU Already Set"
            return resp

        with override_settings(CLACKS_OVERHEAD="Should Not Override"):
            mw = ClacksMiddleware(custom_get_response)
            response = mw(django_rf.get("/"))
            assert response[CLACKS_HEADER] == "GNU Already Set"

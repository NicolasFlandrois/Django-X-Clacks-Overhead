"""
Comprehensive test suite for Django-X-Clacks-Overhead.
Covers: Middleware, Mixin, Decorator, Precedence Logic, Security, Edge Cases.
"""
import pytest
from django.http import HttpResponse
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory

from clacks import DEFAULT_CLACKS_TRIBUTE, _format_clacks_value

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
# 🔬 Helper Function Tests (_format_clacks_value)
# ─────────────────────────────────────────────────────────────────────────────

class TestFormatClacksValue:
    """Test the core formatting & sanitization logic."""

    def test_none_falls_back_to_default(self):
        assert _format_clacks_value(None) == DEFAULT_CLACKS_TRIBUTE

    def test_empty_string_falls_back_to_default(self):
        assert _format_clacks_value("") == DEFAULT_CLACKS_TRIBUTE

    def test_single_string_adds_gnu_prefix(self):
        assert _format_clacks_value("Terry Pratchett") == "GNU Terry Pratchett"
        assert _format_clacks_value("GNU Alan Turing") == "GNU Alan Turing"  # Already prefixed

    def test_list_of_strings_formats_correctly(self):
        names = ["Ada Lovelace", "John von Neumann"]
        result = _format_clacks_value(names)
        assert result == "GNU Ada Lovelace, GNU John von Neumann"

    def test_mixed_list_with_existing_prefix(self):
        names = ["Terry Pratchett", "GNU Alan Turing"]
        result = _format_clacks_value(names)
        assert result == "GNU Terry Pratchett, GNU Alan Turing"

    def test_empty_list_falls_back_to_default(self):
        assert _format_clacks_value([]) == DEFAULT_CLACKS_TRIBUTE

    def test_security_strips_newlines_and_nulls(self):
        malicious = "Evil\nHeader\x00Injection"
        result = _format_clacks_value(malicious)
        assert result == "GNU EvilHeaderInjection"
        assert "\n" not in result
        assert "\r" not in result
        assert "\x00" not in result

    def test_security_strips_leading_trailing_whitespace(self):
        result = _format_clacks_value("  Terry Pratchett  ")
        assert result == "GNU Terry Pratchett"

    def test_non_string_falls_back_to_default(self):
        assert _format_clacks_value(123) == DEFAULT_CLACKS_TRIBUTE
        assert _format_clacks_value({}) == DEFAULT_CLACKS_TRIBUTE

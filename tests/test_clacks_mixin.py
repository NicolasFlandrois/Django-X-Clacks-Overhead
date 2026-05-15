from unittest.mock import patch

import pytest
from django.http import HttpResponse
from django.test import RequestFactory
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework.viewsets import ViewSet

from clacks import CLACKS_HEADER, ClacksMixin, clacks_overhead

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
# 🧩 Mixin Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestClacksMixin:
    """Unit tests for ClacksMixin logic."""

    class TestView(ClacksMixin, ViewSet):
        __test__ = False
        clacks_tribute = "Mixin Tribute"

        def list(self, request, *args, **kwargs):
            return Response({"status": "ok"})

        @action(detail=False, methods=["get"])
        @clacks_overhead("Decorator Tribute")
        def custom_action(self, request, *args, **kwargs):
            return Response({"status": "decorated"})

    def test_mixin_sets_header_on_response(self, drf_rf):
        """Mixin adds header when tribute is configured."""
        request = drf_rf.get("/")
        drf_request = Request(request)  # Wrap in DRF Request

        viewset = self.TestView()
        viewset.request = drf_request
        viewset.format_kwarg = None

        response = Response({"test": "data"})

        # Mock parent's finalize_response to avoid full DRF setup
        with patch("rest_framework.views.APIView.finalize_response", return_value=response):
            final_resp = viewset.finalize_response(drf_request, response)

        assert final_resp.get(CLACKS_HEADER) == "GNU Mixin Tribute"

    def test_mixin_handles_list_tributes(self, drf_rf):
        """Mixin formats list of tributes correctly."""

        class ListView(self.TestView):
            clacks_tribute = ["Grace Hopper", "John Backus"]

        request = drf_rf.get("/")
        drf_request = Request(request)

        viewset = ListView()
        viewset.request = drf_request

        response = Response({})

        with patch("rest_framework.views.APIView.finalize_response", return_value=response):
            final_resp = viewset.finalize_response(drf_request, response)

        assert final_resp.get(CLACKS_HEADER) == "GNU Grace Hopper, GNU John Backus"

    def test_mixin_skips_when_tribute_is_none(self, drf_rf):
        """Mixin does nothing when clacks_tribute is None."""

        class NoTributeView(self.TestView):
            clacks_tribute = None

        request = drf_rf.get("/")
        drf_request = Request(request)

        viewset = NoTributeView()
        viewset.request = drf_request

        response = Response({})

        with patch("rest_framework.views.APIView.finalize_response", return_value=response):
            final_resp = viewset.finalize_response(drf_request, response)

        # Header should NOT be set by mixin when tribute is None
        assert CLACKS_HEADER not in final_resp

    def test_mixin_respects_decorator_precedence(self, drf_rf):
        """Mixin skips if header already set (decorator won)."""
        request = drf_rf.get("/")
        drf_request = Request(request)

        viewset = self.TestView()
        viewset.request = drf_request

        # Simulate decorator having set the header first
        response = Response({"status": "decorated"})
        response[CLACKS_HEADER] = "GNU Decorator Wins"

        with patch("rest_framework.views.APIView.finalize_response", return_value=response):
            final_resp = viewset.finalize_response(drf_request, response)

        # Mixin should respect the existing header
        assert final_resp.get(CLACKS_HEADER) == "GNU Decorator Wins"

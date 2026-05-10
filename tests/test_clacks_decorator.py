import pytest
from django.http import HttpResponse
from django.test import RequestFactory
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework.viewsets import ViewSet

from clacks import CLACKS_HEADER, clacks_overhead

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
# 🎭 Decorator Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestClacksDecorator:
    def test_decorator_sets_header(self, drf_rf):
        class TestView(ViewSet):
            @action(detail=False, methods=["get"])
            @clacks_overhead("Ada Lovelace")
            def tribute(self, request):
                return Response({"msg": "ok"})

        viewset = TestView()
        viewset.request = drf_rf.get("/")
        response = viewset.tribute(viewset.request)
        assert response[CLACKS_HEADER] == "GNU Ada Lovelace"

    def test_decorator_handles_list_value(self, drf_rf):
        class TestView(ViewSet):
            @action(detail=False, methods=["get"])
            @clacks_overhead(["Terry Pratchett", "Alan Turing"])
            def tribute(self, request):
                return Response({"msg": "ok"})

        viewset = TestView()
        viewset.request = drf_rf.get("/")
        response = viewset.tribute(viewset.request)
        assert response[CLACKS_HEADER] == "GNU Terry Pratchett, GNU Alan Turing"

    def test_decorator_preserves_function_metadata(self):
        """Verify @wraps preserves original function metadata."""

        @clacks_overhead("Test")
        def my_view(view, request):
            """My view docstring"""
            return HttpResponse("OK")

        # Test what @wraps actually preserves — no need to call the function
        assert my_view.__name__ == "my_view", "Function name should be preserved"
        assert my_view.__doc__ == "My view docstring", "Docstring should be preserved"
        assert my_view.__module__ == __name__, "Module should be preserved"

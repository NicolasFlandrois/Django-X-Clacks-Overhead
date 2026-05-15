"""Clacks middleware, mixin, and decorator for Django.

This module provides the core functionality for injecting X-Clacks-Overhead headers.
"""
# This file is part of Django-X-Clacks-Overhead Python Package.
# Django-X-Clacks-Overhead Python Package is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
# Django-X-Clacks-Overhead Python Package is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with Django-X-Clacks-Overhead Python Package.
# If not, see <https://www.gnu.org/licenses/>.

import logging
import re
from functools import wraps
from importlib.metadata import PackageNotFoundError, version
from typing import List, Union

from django.conf import settings

__version__ = "1.0.1+dev"  # Fallback for dev/source runs - Update this when developing on new version.

try:
    __version__ = version("django-x-clacks-overhead")  # Prefer installed metadata
except PackageNotFoundError:
    pass

__all__ = ["ClacksMiddleware", "ClacksMixin", "clacks_overhead"]

logger = logging.getLogger(__name__)

DEFAULT_CLACKS_TRIBUTE = "GNU Terry Pratchett"
CLACKS_HEADER = "X-Clacks-Overhead"


def _normalize_tribute(tribute: str) -> str:
    """Normalize a single tribute: sanitize and ensure GNU prefix."""
    if not tribute or not isinstance(tribute, str):
        return DEFAULT_CLACKS_TRIBUTE

    safe = re.sub(r"[\r\n\x00]", "", tribute.strip())
    if not safe:
        return DEFAULT_CLACKS_TRIBUTE

    return safe if safe.startswith("GNU ") else f"GNU {safe}"


def _format_clacks_value(value: Union[str, List[str], None]) -> str:
    """Format clacks configuration into header-ready string."""
    if value is None:
        return DEFAULT_CLACKS_TRIBUTE

    if isinstance(value, str):
        return _normalize_tribute(value)

    if isinstance(value, (list, tuple)):
        normalized = [_normalize_tribute(str(v)) for v in value if v]
        return ", ".join(normalized) if normalized else DEFAULT_CLACKS_TRIBUTE

    return DEFAULT_CLACKS_TRIBUTE


class ClacksMiddleware:
    """
    Global middleware to inject X-Clacks-Overhead header.

    Precedence: LOWEST - Only sets header if not already set by Mixin/Decorator.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        raw_value = getattr(settings, "CLACKS_OVERHEAD", None)
        self.clacks_value = _format_clacks_value(raw_value)
        logger.info(f"[ClacksMiddleware] Initialized with: {self.clacks_value}")

    def __call__(self, request):
        response = self.get_response(request)

        # CRITICAL: Only set header if not already set by higher-priority layer
        if not response.has_header(CLACKS_HEADER):
            response[CLACKS_HEADER] = self.clacks_value
            logger.info(f"[ClacksMiddleware] Set header: {self.clacks_value}")
        else:
            logger.info("[ClacksMiddleware] Skipped (header already set)")

        return response


class ClacksMixin:
    """
    ViewSet mixin to set Clacks header at the ViewSet level.

    Precedence: MEDIUM - Overrides Middleware, but respects Decorator.
    """

    clacks_tribute = None

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)  # type: ignore[attr-defined]
        # ClacksMixin is designed to be mixed into a class like ViewSet or View that does have `finalize_response()`,
        # but the type checker can't infer this at analysis time.

        if self.clacks_tribute is None:
            logger.debug("[ClacksMixin] No tribute configured, skipping")
            return response

        # CRITICAL: Only set header if not already set by Decorator
        if response.has_header(CLACKS_HEADER):
            logger.info("[ClacksMixin] Skipped (header already set by Decorator)")
            return response

        formatted = _format_clacks_value(self.clacks_tribute)
        response[CLACKS_HEADER] = formatted
        logger.info(f"[ClacksMixin] Set header: {formatted}")

        return response


def clacks_overhead(value: Union[str, List[str]]):
    """
    Decorator to set Clacks header at the method level.

    Precedence: HIGHEST - Always sets header, overrides Mixin and Middleware.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view, request, *args, **kwargs):
            logger.info(f"[ClacksDecorator] Executing for: {view_func.__name__}")

            response = view_func(view, request, *args, **kwargs)

            formatted = _format_clacks_value(value)
            response[CLACKS_HEADER] = formatted
            logger.info(f"[ClacksDecorator] Set header: {formatted}")

            return response

        return _wrapped_view

    return decorator

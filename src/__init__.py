"""Django X-Clacks-Overhead: GNU Terry Pratchett tribute middleware."""
# This file is part of Django-X-Clacks-Overhead Python Package.
# Django-X-Clacks-Overhead Python Package is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
# Django-X-Clacks-Overhead Python Package is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with Django-X-Clacks-Overhead Python Package.
# If not, see <https://www.gnu.org/licenses/>.

try:
    from importlib.metadata import PackageNotFoundError, version
    __version__ = version("django-x-clacks-overhead")
except PackageNotFoundError:
    __version__ = "0.1.0+dev"

__all__ = [
    'clacks',
]
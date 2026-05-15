# Django-X-Clacks-Overhead
X-Clacks-Overhead package for Django!

## GNU Clacks Overhead

A Django/Django REST Framework middleware system for managing the **X-Clacks-Overhead** HTTP header, honoring the legacy of Sir Terry Pratchett and the Discworld Clacks semaphore network.

> *"A man is not dead while his name is still spoken."*
> — Going Postal, Chapter 4 prologue

---

## 📖 Background

In Terry Pratchett's Discworld, the **Clacks** is a semaphore tower network. When Robert Dearheart's son John died, he encoded his name into the Clacks overhead with the code **GNU**:
- **G** — Send the message on
- **N** — Do not log the message
- **U** — Turn the message around at the end of the line and send it back again

This ensures the name travels the Clacks forever. This package brings that tradition to the modern Internet (the "Roundworld Clacks").

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Three-Layer Precedence** | Middleware → Mixin → Decorator (each overrides the previous) |
| **DRF Compatible** | Works seamlessly with Django REST Framework ViewSets |
| **RFC Compliant** | Supports comma-separated multiple tributes |
| **Security Hardened** | Sanitizes header values to prevent injection attacks |
| **Tested** | Full test suite with 100% coverage of precedence logic |

---

## 🚀 Installation

### 1. Install package as par of your Django project

#### PIP

`pip3 install django-x-clacks-overhead`

#### UV

`uv add django-x-clacks-overhead`

_optional_:
```
### With DRF support
uv add django-x-clacks-overhead[drf]
```

### 2. Add Middleware to `settings.py`

```python
# settings.py
MIDDLEWARE = [
    # ... other middleware
    'clacks.ClacksMiddleware',
]

# Global default tribute (optional)
CLACKS_OVERHEAD = "Terry Pratchett"
```

### 3. Configure Tributes

The default X-Clacks-Overhead value is `GNU Terry Pratchett`, on all 3 applications: Middleware, Mixin, Decorator.

Unless you configure and spécify a tribute. (See more details bellow in **Usage** section)

#### Tribute configuration on Middleware level

```python
# settings.py

# Single tribute
CLACKS_OVERHEAD = "Terry Pratchett"

# Or

# Multiple tributes (comma-separated in header)
CLACKS_OVERHEAD = ["Terry Pratchett", "Alan Turing", "Ada Lovelace"]

# No setting = defaults to "GNU Terry Pratchett"
```

#### Tribute configuration on Mixin level

```python
# views.py
from rest_framework import viewsets
from clacks import ClacksMixin

class TributeViewSet(ClacksMixin, viewsets.ModelViewSet):
    clacks_tribute = ["Grace Hopper", "John Warner Backus"]

    queryset = MyModel.objects.all()
    serializer_class = MySerializer
```

#### Tribute configuration on Decorator level

```python
# views.py
from rest_framework.decorators import action
from clacks import clacks_overhead

class TributeViewSet(ClacksMixin, viewsets.ModelViewSet):
    clacks_tribute = ["Terry Pratchett", "Alan Turing"]

    @action(detail=False, methods=['get'])
    @clacks_overhead("Dennis Ritchie")
    def ada(self, request):
        return Response({"tribute": "Dennis Ritchie"})
```

---

## 📖 Usage

### Layer 1: Middleware (Global Default)

Applied to **all endpoints** automatically. Set in `settings.py`.

By default the `X-Clacks-Overhead` will deliver "GNU Terry Pratchett" if no settings specified.

#### Single Tribute

```python
# settings.py
CLACKS_OVERHEAD = "John Dearheart"

# All responses will include:
# X-Clacks-Overhead: GNU John Dearheart
```

#### Multiple Tribute

```python
# settings.py
# Multiple tributes (comma-separated in header)
CLACKS_OVERHEAD = ["John von Neumann", "Alan Turing", "Ada Lovelace"]

# All responses will include:
# X-Clacks-Overhead: GNU John von Neumann, GNU Alan Turing, GNU Ada Lovelace
```

---

### Layer 2: Mixin (ViewSet-Level Override)

Override the Middleware tribute for an **entire ViewSet**.

```python
# views.py
from rest_framework import viewsets
from clacks import ClacksMixin

class TributeViewSet(ClacksMixin, viewsets.ModelViewSet):
    clacks_tribute = ["Grace Hopper", "John Warner Backus"]

    queryset = MyModel.objects.all()
    serializer_class = MySerializer

# All endpoints in this ViewSet will include:
# X-Clacks-Overhead: GNU Grace Hopper, GNU John Warner Backus
```

---

### Layer 3: Decorator (Method-Level Override)

Override **both** Middleware and Mixin for a **specific endpoint**.

```python
# views.py
from rest_framework.decorators import action
from clacks import clacks_overhead

class TributeViewSet(ClacksMixin, viewsets.ModelViewSet):
    clacks_tribute = ["Terry Pratchett", "Alan Turing"]

    @action(detail=False, methods=['get'])
    @clacks_overhead("Dennis Ritchie")
    def ada(self, request):
        return Response({"tribute": "Dennis Ritchie"})

# This endpoint will include:
# X-Clacks-Overhead: GNU Dennis Ritchie
# (Overrides the Mixin's tributes)
```

---

## 🎯 Precedence Table

| Layer | Scope | Overrides | Example |
|-------|-------|-----------|---------|
| **Decorator** | Single endpoint | Middleware + Mixin | `@clacks_overhead("Dennis Ritchie")` |
| **Mixin** | Entire ViewSet | Middleware | `clacks_tribute = ["Grace Hopper", "John Warner Backus"]` |
| **Middleware** | All endpoints | (none) | `CLACKS_OVERHEAD = "John Dearheart"` |

**Rule:** If a higher-priority layer sets the header, lower-priority layers skip automatically.

---

## 🧪 Complete Example

```python
# settings.py
CLACKS_OVERHEAD = "John Dearheart"  # Global default

# views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from clacks import ClacksMixin, clacks_overhead

# Endpoint: /api/default/
# Header: X-Clacks-Overhead: GNU John Dearheart
class DefaultViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()

# Endpoint: /api/tributes/
# Header: X-Clacks-Overhead: GNU Terry Pratchett, GNU Alan Turing
class TributesViewSet(ClacksMixin, viewsets.ModelViewSet):
    clacks_tribute = ["Terry Pratchett", "Alan Turing"]
    queryset = MyModel.objects.all()

    # Endpoint: /api/tributes/ada/
    # Header: X-Clacks-Overhead: GNU Ada Lovelace
    @action(detail=False, methods=['get'])
    @clacks_overhead("Ada Lovelace")
    def ada(self, request):
        return Response({"message": "Honoring Ada Lovelace"})
```

---

## 🧪 Testing

```python
# tests.py
from django.test import override_settings
from rest_framework.test import APITestCase

@override_settings(CLACKS_OVERHEAD="John Dearheart")
class TestClacksHeader(APITestCase):

    def test_middleware_default(self):
        response = self.client.get('/api/default/')
        self.assertEqual(
            response.get("X-Clacks-Overhead"),
            "GNU John Dearheart"
        )

    def test_decorator_override(self):
        response = self.client.get('/api/tributes/ada/')
        self.assertEqual(
            response.get("X-Clacks-Overhead"),
            "GNU Ada Lovelace"
        )
```

---

## 🔧 Configuration Reference

### Settings

| Setting           | Type                 | Default                 | Description                          |
|-------------------|----------------------|-------------------------|--------------------------------------|
| `CLACKS_OVERHEAD` | `str` or `list[str]` | `"GNU Terry Pratchett"` | Global default tribute(s) [Optional] |

### Mixin Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `clacks_tribute` | `str` or `list[str]` | Tribute(s) for this ViewSet |

### Decorator Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `value` | `str` or `list[str]` | Tribute(s) for this endpoint |

---

## 🛡️ Security

All tribute values are sanitized to prevent HTTP header injection:

- Newlines (`\r`, `\n`) are stripped
- Null bytes (`\x00`) are removed
- Empty values fall back to default

```python
# Unsafe input is sanitized automatically
CLACKS_OVERHEAD = "Evil\nHeader"
# Result: X-Clacks-Overhead: GNU EvilHeader
```

---

## 📜 RFC Compliance

This implementation follows the [Clacks-over-HTTP Draft RFC](https://github.com/clacks-overhead/clacks-protocol):

- Header name: `X-Clacks-Overhead`
- Format: `GNU <name>` (prefix enforced)
- Multiple values: Comma-separated (`GNU Name1, GNU Name2`)

---

## 🤝 Contributing

1.  Fork the repository
2.  Create a feature branch
3.  Run tests: `uv run pytest`
4.  Submit a Pull Request

---

## 📄 License

GNU General Public License v3 (GPLv3).

---

## Acknowledgments

- **[Sir Terry Pratchett](https://en.wikipedia.org/wiki/Terry_Pratchett)** — For the Discworld series and the Clacks.
- **[GNU Terry Pratchett Project](http://www.gnuterrypratchett.com/)** — For keeping the legacy alive.
- **Discworld Fandom** — For maintaining the Clacks network.

*"Go well, and fare you well, and may the light of your going be a beacon to those who follow."*

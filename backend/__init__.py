"""
🌾 AgroForgeSIM Backend Package
-------------------------------
FastAPI-powered agronomic simulation backend.

Exports:
- `app`: FastAPI ASGI application (lazy import from .app)
- Package metadata: __version__, __author__
"""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

__all__ = ["app", "__version__", "__author__"]

# Package metadata (kept import-light for quick diagnostics/tools)
__version__ = "4.0.0"
__author__ = "AgroForgeSIM Research Team"


def __getattr__(name: str) -> Any:
    """
    Lazy attribute loader so importing package metadata does not pull FastAPI.
    `app` is imported from .app only when accessed.
    """
    if name == "app":
        return import_module(".app", __name__).app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


if TYPE_CHECKING:
    # For type checkers and IDEs, provide the symbol shape
    from fastapi import FastAPI as _FastAPI

    app: _FastAPI

"""Conftest.py for pytest — ensures the app package is importable."""

import sys
import os

# Add the backend directory to path so `from app.xxx import yyy` works
_BACKEND_DIR = os.path.abspath(".")
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

# Also add the parent (envman root) so we can import from top-level
_PARENT_DIR = os.path.abspath("..")
if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)

# Ensure the app package is importable
_APP_DIR = os.path.join(_BACKEND_DIR, "app")
if _APP_DIR not in sys.path:
    sys.path.insert(0, _APP_DIR)

print(f"[conftest] sys.path includes: {_BACKEND_DIR}, {_PARENT_DIR}, {_APP_DIR}")
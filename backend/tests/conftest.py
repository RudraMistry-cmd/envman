"""Conftest.py for pytest — ensures the app package is importable."""

import sys
import os

# Add the backend directory to path so `from app.xxx import yyy` works
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.dirname(_TESTS_DIR)
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

# Also add the parent (envman root) so we can import from top-level
_PARENT_DIR = os.path.dirname(_BACKEND_DIR)
if _PARENT_DIR not in sys.path:
    sys.path.append(_PARENT_DIR)

print(f"[conftest] sys.path includes: {_BACKEND_DIR}")
"""Tests for CLI entry point and static frontend mount."""

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
import app.cli as cli


def test_root_serves_frontend():
    """Verify GET / returns the bundled frontend HTML."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text or "<div id=\"root\">" in response.text


def test_health_check_takes_precedence():
    """Verify GET /health returns status ok even with static mount at root."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cors_headers_for_dev_and_packaged():
    """Verify CORS middleware responds with correct headers."""
    client = TestClient(app)
    # Dev server origin (:5173)
    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:5173"},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"

    # Packaged server origin (:8000)
    response2 = client.get(
        "/health",
        headers={"Origin": "http://localhost:8000"},
    )
    assert response2.status_code == 200
    assert response2.headers.get("access-control-allow-origin") == "http://localhost:8000"


@patch("app.cli.uvicorn.run")
@patch("sys.argv", ["envman", "--port", "9000", "--host", "0.0.0.0", "--no-browser"])
def test_cli_main_arguments(mock_uvicorn_run):
    """Verify cli.main correctly parses arguments and programmatically calls uvicorn.run."""
    cli.main()
    mock_uvicorn_run.assert_called_once_with(
        cli.app,
        host="0.0.0.0",
        port=9000,
        log_level="info",
    )

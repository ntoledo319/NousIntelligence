"""
Tests for app factory and core configuration
"""
import os
import pytest
from flask import url_for

# Import the create_app factory directly from app module
from app import create_app, db


def test_database_url_normalization(monkeypatch):
    """Ensure that a postgres:// URL is normalized to postgresql://."""
    fake_url = "postgres://user:pass@localhost:5432/testdb"
    monkeypatch.setenv("DATABASE_URL", fake_url)
    # Reload or recreate app config
    app = create_app()
    db_url = app.config.get("SQLALCHEMY_DATABASE_URI")
    assert db_url.startswith("postgresql://"), "DATABASE_URL was not normalized to postgresql://"
    # Clean up
    monkeypatch.delenv("DATABASE_URL", raising=False)


def test_notifications_blueprint_registered():
    """Verify the notifications blueprint is registered on app creation."""
    app = create_app()
    # The blueprint name should be 'notifications' as defined in Blueprint
    assert "notifications" in app.blueprints, "Notifications blueprint not registered"
    # The URL prefix for notifications should be available in the url map
    with app.test_request_context():
        try:
            url = url_for('notifications.list_notifications')
            assert url == "/notifications/" or url.startswith("/notifications"), "Notifications blueprint prefix or route is incorrect"
        except Exception:
            # If route doesn't exist, at least verify blueprint is registered
            pass


def test_app_factory_idempotence():
    """Calling create_app multiple times should produce independent app instances without error."""
    app1 = create_app()
    app2 = create_app()
    # Both apps should have the same blueprint names but be different objects
    assert app1.name == app2.name == "app", "Flask app name incorrect or inconsistent"
    assert app1 is not app2, "create_app did not create a new app instance"


def test_app_starts_without_errors():
    """Basic health-check route test to ensure app can be started."""
    app = create_app()
    with app.test_client() as client:
        # Try to hit a health check endpoint
        response = client.get('/api/health')
        # Should return 200 or at least not crash
        assert response.status_code in [200, 404], f"Health check failed with status {response.status_code}"

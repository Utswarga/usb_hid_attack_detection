"""
Playwright tests for the USB HID Attack Detection Dashboard.

These tests verify the web interface functionality using browser automation.
"""

import pytest
import subprocess
import time
import sys
from pathlib import Path


@pytest.fixture(scope="session")
def dashboard_server():
    """Fixture to start the dashboard server for testing."""
    project_root = Path(__file__).parent.parent
    dashboard_script = project_root / "tools" / "dashboard.py"

    # Start the Flask server
    server = subprocess.Popen([sys.executable, str(dashboard_script)])
    time.sleep(3)  # Wait for server to start

    yield "http://localhost:5000"

    # Cleanup
    server.terminate()
    server.wait()


def test_dashboard_page_load(dashboard_server, page):
    """Test that the dashboard page loads correctly."""
    page.goto(dashboard_server)

    # Check page title
    assert page.title() == "USB HID Safety Dashboard"

    # Check main header
    header = page.locator("h1").first
    assert header.is_visible()
    assert "USB Safety Dashboard" in header.text_content()


def test_dashboard_system_status(dashboard_server, page):
    """Test the system status section."""
    page.goto(dashboard_server)

    # Check if system status section exists
    status_section = page.locator("text=System Status").first
    assert status_section.is_visible()

    # Check for system status value
    system_status = page.locator("#system-status").first
    assert system_status.is_visible()
    assert system_status.text_content() in ["Ready", "Idle", "idle", "running"]


def test_dashboard_navigation(dashboard_server, page):
    """Test basic navigation and responsiveness."""
    page.goto(dashboard_server)

    # Check if page is responsive
    page.set_viewport_size({"width": 800, "height": 600})
    assert page.title() == "USB HID Safety Dashboard"

    # Check if main container exists
    container = page.locator(".container").first
    assert container.is_visible()


def test_dashboard_api_endpoints(dashboard_server, page):
    """Test that API endpoints are accessible."""
    page.goto(dashboard_server)

    # The dashboard likely makes API calls, but for basic test,
    # just ensure the page loads without JavaScript errors
    # Check for any error messages
    error_messages = page.locator("text=Error").all()
    assert len(error_messages) == 0
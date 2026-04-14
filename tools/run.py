"""
USB HID Attack Detection System - Command Runner

Convenient script to run tests, start dashboard, and manage the system.
Usage:
    python tools/run.py test       - Run all tests
    python tools/run.py dashboard  - Start web dashboard
    python tools/run.py all        - Run tests then start dashboard
    python tools/run.py install    - Install dependencies
"""

import subprocess
import sys
import time
import urllib.request
from pathlib import Path


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


def run_tests():
    """Run the comprehensive test suite."""
    print("\n" + "="*80)
    print("RUNNING USB HID ATTACK DETECTION SYSTEM TESTS")
    print("="*80 + "\n")

    project_root = get_project_root()
    test_file = project_root / "tests" / "test_detection_system.py"

    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            cwd=str(project_root)
        )
        return result.returncode == 0
    except Exception as e:
        print(f"✗ Error running tests: {e}")
        return False


def run_dashboard():
    """Start the web dashboard server."""
    print("\n" + "="*80)
    print("STARTING USB HID ATTACK DETECTION DASHBOARD")
    print("="*80 + "\n")

    project_root = get_project_root()
    dashboard_file = project_root / "tools" / "dashboard.py"

    try:
        subprocess.run(
            [sys.executable, str(dashboard_file)],
            cwd=str(project_root)
        )
    except KeyboardInterrupt:
        print("\n\n✓ Dashboard stopped")
    except Exception as e:
        print(f"✗ Error starting dashboard: {e}")


def is_url_reachable(url: str, timeout: int = 5) -> bool:
    """Return True if the given URL is reachable over HTTP."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return 200 <= response.status < 400
    except Exception:
        return False


def install_requirements():
    """Install required packages."""
    print("\n" + "="*80)
    print("INSTALLING REQUIREMENTS")
    print("="*80 + "\n")

    project_root = get_project_root()
    requirements_file = project_root / "requirements.txt"

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            cwd=str(project_root)
        )
        print("\n✓ Requirements installed successfully")
        return True
    except Exception as e:
        print(f"✗ Error installing requirements: {e}")
        return False


def run_playwright_codegen(url: str = "http://localhost:5000", output_file: str = "tests/generated_playwright_test.py"):
    """Launch Playwright codegen for the dashboard or any target URL.
    
    Auto-starts the dashboard if the target URL is unreachable.
    """
    print("\n" + "="*80)
    print("STARTING PLAYWRIGHT CODEGEN")
    print("="*80 + "\n")

    project_root = get_project_root()
    dashboard_file = project_root / "tools" / "dashboard.py"
    server_process = None

    if not is_url_reachable(url):
        print(f"URL {url} is not reachable. Starting the dashboard server first...")
        server_process = subprocess.Popen(
            [sys.executable, str(dashboard_file)],
            cwd=str(project_root),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        deadline = time.time() + 10
        while time.time() < deadline:
            if is_url_reachable(url):
                break
            time.sleep(0.5)

        if not is_url_reachable(url):
            print(f"✗ Could not reach {url} after starting dashboard.")
            if server_process:
                server_process.terminate()
            return

    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "codegen", url, "--target=python", "--output", output_file],
            cwd=str(project_root)
        )
    except KeyboardInterrupt:
        print("\n\n✓ Playwright codegen stopped")
    except Exception as e:
        print(f"✗ Error starting Playwright codegen: {e}")
    finally:
        if server_process:
            server_process.terminate()


def show_menu():
    """Show help menu."""
    print("\n" + "="*80)
    print("USB HID ATTACK DETECTION SYSTEM - COMMAND RUNNER")
    print("="*80)
    print("\nAvailable commands:")
    print("  python tools/run.py test       → Run comprehensive test suite")
    print("  python tools/run.py dashboard  → Start web dashboard (http://localhost:5000)")
    print("  python tools/run.py install    → Install required packages")
    print("  python tools/run.py codegen    → Launch Playwright codegen for the dashboard")
    print("  python tools/run.py all        → Run tests then start dashboard")
    print("\n" + "="*80 + "\n")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        show_menu()
        return

    # Dispatch command to a single operation mode for predictable CLI behavior.
    if command == 'test':
        success = run_tests()
        sys.exit(0 if success else 1)
    elif command == 'dashboard':
        run_dashboard()
    elif command == 'install':
        success = install_requirements()
        sys.exit(0 if success else 1)
    elif command == 'codegen':
        url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:5000"
        output_file = sys.argv[3] if len(sys.argv) > 3 else "tests/generated_playwright_test.py"
        run_playwright_codegen(url=url, output_file=output_file)
    elif command == 'all':
        if run_tests():
            print("\n✓ Tests completed successfully. Starting dashboard...\n")
            time.sleep(2)
            run_dashboard()
        else:
            print("\n✗ Tests failed. Please fix issues before starting dashboard.")
            sys.exit(1)
    elif command in ['-h', '--help', 'help']:
        show_menu()
    else:
        print(f"✗ Unknown command: {command}")
        show_menu()
        sys.exit(1)


if __name__ == "__main__":
    main()


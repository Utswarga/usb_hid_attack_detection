"""
Configuration constants for USB HID Attack Detection System.
"""

import os
from pathlib import Path

# Directories
BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Logging configuration
LOG_FILE = LOGS_DIR / "events.log"
INCIDENT_REPORTS_DIR = LOGS_DIR / "incidents"
INCIDENT_REPORTS_DIR.mkdir(exist_ok=True)
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
LOG_LEVEL = "INFO"

# Detection thresholds
KEYSTROKE_SPEED_THRESHOLD = 50  # WPM (words per minute) - threshold for "too fast" typing
KEYSTROKE_TIME_WINDOW = 2.0  # seconds - window to analyze keystroke patterns
MIN_KEYSTROKES_FOR_BURST = 10  # minimum keystrokes to trigger fast typing alert

# Suspicious processes that indicate potential attack
SUSPICIOUS_PROCESSES = [
    "cmd.exe",
    "powershell.exe",
    "terminal",
    "bash",
    "sh",
    "zsh",
    "python.exe",
    "python",
    "perl",
    "ruby",
    "ncat",
    "nc.exe",
]

# Correlation window - events within this window are correlated
CORRELATION_TIME_WINDOW = 5.0  # seconds

# USB HID device keywords to watch for
USB_HID_KEYWORDS = [
    "keyboard",
    "hid",
    "input device",
    "human interface device",
]

# Known USB identifiers commonly seen with Raspberry Pi Pico/Pico W boards.
# Format is uppercase hexadecimal strings without 0x prefix.
PICO_VENDOR_IDS = {
    "2E8A",  # Raspberry Pi Trading Ltd
}

# Example Pico boot/prog and custom HID product IDs that are often observed in
# security labs or DIY Rubber Ducky style emulation workflows.
PICO_PRODUCT_IDS = {
    "0003",
    "0005",
    "000A",
}

# Human-readable markers used when VID/PID is unavailable from platform APIs.
PICO_NAME_KEYWORDS = [
    "raspberry pi pico",
    "pico w",
    "tinyusb",
    "circuitpython",
    "micropython",
]

# Trusted HID devices that should be treated as lower risk in enterprise labs.
# Add your official keyboard models/manufacturers here.
TRUSTED_HID_NAME_KEYWORDS = [
    "logitech",
    "microsoft",
    "hp keyboard",
    "dell keyboard",
]

# USB policy mode:
# - monitor: detect and log only (default)
# - strict_allowlist: only allowed fingerprints are treated as trusted
# - strict_denylist: denylisted fingerprints are treated as critical
USB_POLICY_MODE = "monitor"

# Allowlist and denylist support "VID:PID" and free-form name keyword entries.
# Example fingerprint entry: "2E8A:000A"
USB_DEVICE_ALLOWLIST = {
    "046D:C31C",  # Example Logitech keyboard
    "045E:07F8",  # Example Microsoft keyboard
}

USB_DEVICE_DENYLIST = {
    "2E8A:000A",  # Example Pico custom HID profile
}

# Response actions
RESPONSE_ACTIONS = {
    "log": True,        # Always log
    "alert": True,      # Print alert to console
    "kill_process": False,  # Kill suspicious process (enable with caution)
    "quarantine_unknown_pico": True,  # Quarantine unknown Pico-like HID activity
    "export_incident_report": True,  # Save JSON report per detected attack
}

# Platform detection
PLATFORM = "windows"  # windows or linux

# Attack severity levels
SEVERITY_LEVELS = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}

# Simulation mode (for testing without actual HID devices)
SIMULATION_MODE = False

# Project Structure

This project is now organized by responsibility so code, tests, tools, UI, and logs are separated clearly.

## Current Folder Layout

```
usb_hid_attack_detection/
├── core/                          # Main detection logic
│   ├── __init__.py
│   ├── config.py
│   ├── detection_engine.py
│   ├── keystroke_analyzer.py
│   ├── logger.py
│   ├── process_monitor.py
│   ├── response_engine.py
│   ├── simulation.py
│   └── usb_monitor.py
│
├── tests/                         # Automated tests
│   ├── __init__.py
│   └── test_detection_system.py   # 19 tests
│
├── tools/                         # Utility/runner scripts
│   ├── dashboard.py               # Flask dashboard backend
│   └── run.py                     # Unified command runner
│
├── templates/                     # Dashboard frontend template
│   └── dashboard.html
│
├── logs/                          # Runtime artifacts/log output
│   ├── events.log
│   └── test_results.txt
│
├── main.py                        # Main app entry point
├── examples.py                    # Example usage scenarios
├── requirements.txt               # Python dependencies
├── .gitignore
│
├── README.md
└── docs/                          # Project documentation
   ├── ARCHITECTURE.md
   ├── COMPLETE_SETUP_GUIDE.md
   ├── DOCUMENTATION_INDEX.md
   ├── IMPLEMENTATION_SUMMARY.md
   ├── OVERVIEW_GUIDE.md
   ├── PROJECT_STATUS.md
   ├── PROJECT_STRUCTURE.md       # This file
   ├── QUICKSTART.md
   ├── SETUP_AND_RUN.md
   └── TESTING_AND_DASHBOARD_GUIDE.md
```

## What Goes Where

- `core/`: reusable detection components only (no CLI/tool glue).
- `tests/`: all test code only.
- `tools/`: operational scripts (test runner and dashboard launcher).
- `templates/`: HTML used by the dashboard.
- `logs/`: generated outputs and log files.
- root: entry points and documentation.

## File Descriptions

### Core Modules (`core/`)

- `core/__init__.py`: Package exports for the core detection components.
- `core/config.py`: Central detection thresholds, suspicious process list, and response toggles.
- `core/detection_engine.py`: Correlates signals over time and raises attack events.
- `core/keystroke_analyzer.py`: Detects abnormal typing bursts and automated key injection patterns.
- `core/logger.py`: Structured logging utilities for console and file output.
- `core/process_monitor.py`: Monitors process launches and flags suspicious executables.
- `core/response_engine.py`: Handles response actions when attacks are detected.
- `core/simulation.py`: Provides test scenarios to simulate attack behaviors safely.
- `core/usb_monitor.py`: Detects USB device insertion events (especially HID keyboard behavior).

### Test Modules (`tests/`)

- `tests/__init__.py`: Marks test package.
- `tests/test_detection_system.py`: Comprehensive suite (19 tests) for core components and integration.

### Tooling (`tools/`)

- `tools/dashboard.py`: Flask server that exposes dashboard UI and API endpoints.
- `tools/run.py`: Unified command runner for install, test, dashboard, and all-in-one flow.

### Templates (`templates/`)

- `templates/dashboard.html`: Frontend dashboard UI (status, signals, and controls).

### Runtime Output (`logs/`)

- `logs/events.log`: Runtime detection and event logs.
- `logs/test_results.txt`: Saved test run output.

### Root Entry Files

- `main.py`: Main orchestrator for live monitoring and detection.
- `examples.py`: Practical usage examples and demonstration flows.
- `requirements.txt`: Python dependencies for runtime.
- `.gitignore`: Ignore patterns for logs, virtual environment, and cache files.

### Documentation Files (`docs/`)

- `docs/ARCHITECTURE.md`: Design and component architecture details.
- `docs/COMPLETE_SETUP_GUIDE.md`: Full operational guide.
- `docs/DOCUMENTATION_INDEX.md`: Documentation and navigation index.
- `docs/IMPLEMENTATION_SUMMARY.md`: Consolidated implementation summary.
- `docs/OVERVIEW_GUIDE.md`: Alternative streamlined readme.
- `docs/PROJECT_STATUS.md`: Current project status and completion notes.
- `docs/PROJECT_STRUCTURE.md`: Structure map and file purpose guide.
- `docs/QUICKSTART.md`: Fast startup commands and workflow.
- `docs/SETUP_AND_RUN.md`: Step-by-step setup and run instructions.
- `docs/TESTING_AND_DASHBOARD_GUIDE.md`: Testing and dashboard usage guide.

## Standard Commands

From project root:

```powershell
python tools/run.py help
python tools/run.py install
python tools/run.py test
python tools/run.py dashboard
python tools/run.py all
```

Direct alternatives:

```powershell
python tests/test_detection_system.py
python tools/dashboard.py
python main.py
```

## Organization Rules

- New core logic files should go to `core/`.
- New tests should go to `tests/`.
- New operational scripts should go to `tools/`.
- New generated artifacts should go to `logs/`.
- Keep root focused on entry points and docs.

## Attack Detection Capabilities

### Detected Patterns:

1. **USB → Terminal Launch**
   ```
   Signal 1: USB insertion
   Signal 2: Suspicious process within 5 seconds
   Confidence: HIGH
   ```

2. **Keystroke Burst**
   ```
   Signal: >100 WPM sustained keystroke rate
   Confidence: CRITICAL
   Reason: Humans can't type >50-70 WPM normally
   ```

3. **Multi-Signal (USB + Keystroke + Process)**
   ```
   Signal 1: USB insertion
   Signal 2: Keystroke burst
   Signal 3: Terminal/command launch
   Confidence: CRITICAL (highest)
   ```

## Configuration Quick Reference

**Detection Thresholds** (edit in `core/config.py`):
```python
KEYSTROKE_SPEED_THRESHOLD = 50        # WPM threshold
MIN_KEYSTROKES_FOR_BURST = 10         # Min events to trigger
CORRELATION_TIME_WINDOW = 5.0         # Signal correlation window
```

**Suspicious Processes**:
```python
SUSPICIOUS_PROCESSES = [
    "cmd.exe", "powershell.exe",      # Windows shells
    "bash", "sh", "zsh",              # Unix shells
    "python", "perl", "ruby",         # Interpreters
    "ncat", "nc.exe",                 # Network tools
]
```

**Response Actions**:
```python
RESPONSE_ACTIONS = {
    "log": True,              # Log to file (always)
    "alert": True,            # Alert to console
    "kill_process": False,    # Terminate process
}
```

## Running the System

### Basic Monitoring
```bash
python main.py --duration 60
```

### Simulation Testing
```bash
python main.py --list-scenarios          # Show all scenarios
python main.py --simulate FULL_ATTACK    # Run full attack
```

### Examples
```bash
python examples.py 1  # Basic monitoring
python examples.py 2  # Custom handlers
python examples.py 3  # Multiple scenarios
```

## Production Readiness

✅ **Ready for Production**:
- Structured logging with audit trail
- Error handling & graceful degradation
- Configurable behavior
- Extended documentation
- Simulation for testing without hardware
- Custom response handler support

⚠️ **Before Deployment**:
- Adjust KEYSTROKE_SPEED_THRESHOLD for your users
- Test with actual USB devices
- Set up log aggregation/monitoring
- Configure SIEM integration
- Train security team on alert response

## Security Classification

This is a **Defensive Security Tool**:
- Designed to protect against attacks
- No offensive capabilities
- Logs for compliance & forensics
- Safe for production deployment
- Follows security best practices

## Version

**Version**: 1.0  
**Release Date**: 2024-01-15  
**Status**: Production Ready

---

## Next Steps

1. **Install**: `pip install -r requirements.txt`
2. **Test**: `python main.py --simulate FULL_ATTACK`
3. **Review**: Check `logs/events.log` for alerts
4. **Configure**: Edit `core/config.py` for your environment
5. **Deploy**: Run on protection systems
6. **Integrate**: Add SIEM integration via custom handlers

For more details, see [README.md](../README.md), [QUICKSTART.md](QUICKSTART.md), and [ARCHITECTURE.md](ARCHITECTURE.md).

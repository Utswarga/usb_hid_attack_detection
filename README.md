# USB HID Attack Detection System

A production-grade Python application for detecting and responding to USB Rubber Ducky-style keystroke injection attacks. This system correlates multiple signals (USB insertion, keystroke patterns, suspicious process launches) to identify coordinated attacks.

## Features

- **USB Device Monitoring**: Detects new USB HID keyboard connections in real-time
- **Keystroke Pattern Analysis**: Identifies abnormally fast typing speeds and automated keystroke injection
- **Process Monitoring**: Tracks suspicious application launches (terminals, interpreters, etc.)
- **Signal Correlation**: Analyzes temporal relationships between events to confirm attacks
- **Structured Logging**: JSON-formatted logs with full audit trail
- **Configurable Responses**: Alert, log, and optional process termination
- **Simulation Mode**: Test attack scenarios without actual USB devices
- **Cross-Platform**: Windows (primary) with Linux support via abstraction layer

## Documentation Map

- `docs/SETUP_AND_RUN.md`: Complete setup and run steps
- `docs/QUICKSTART.md`: Fast commands for getting started
- `docs/PROJECT_STRUCTURE.md`: Folder/file organization and file descriptions
- `docs/ARCHITECTURE.md`: Component design and data flow
- `docs/DOCUMENTATION_INDEX.md`: Index of all project documentation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Detection System (Main)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ USB Monitor  │  │  Keystroke   │  │  Process     │    │
│  │              │  │  Analyzer    │  │  Monitor     │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                  │            │
│         └─────────────────┼──────────────────┘            │
│                           │                              │
│         ┌─────────────────▼────────────────┐             │
│         │  Detection Engine (Correlation)  │             │
│         │     - USB + Terminal Attack      │             │
│         │     - Keystroke Injection        │             │
│         │     - Multi-Signal Attacks       │             │
│         └─────────────────┬────────────────┘             │
│                           │                              │
│         ┌─────────────────▼────────────────┐             │
│         │   Response Engine                │             │
│         │   - Log events                   │             │
│         │   - Console alerts               │             │
│         │   - Process termination          │             │
│         └──────────────────────────────────┘             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Module Structure

### Core Modules

- **`config.py`**: Centralized configuration (thresholds, suspicious processes, etc.)
- **`logger.py`**: Structured JSON logging to `logs/events.log`
- **`usb_monitor.py`**: Platform-specific USB device detection (Windows WMI / Linux /sys)
- **`keystroke_analyzer.py`**: Analyzes typing speed to detect automation
- **`process_monitor.py`**: Tracks process launches and identifies suspicious applications
- **`detection_engine.py`**: Correlates signals over a time window to detect attacks
- **`response_engine.py`**: Handles logging, alerting, and process termination
- **`simulation.py`**: Attack simulation scenarios for testing
- **`main.py`**: System orchestrator and entry point

## Installation

### Prerequisites
- Python 3.8+
- Windows 10+ or Linux

### Setup

```bash
# Clone or extract the project
cd usb_hid_attack_detection

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Windows) Install WMI support for USB detection
pip install pywin32
python -m Scripts/pywin32_postinstall.py -install
```

## Configuration

Edit `core/config.py` to customize:

- **Detection Thresholds**:
  - `KEYSTROKE_SPEED_THRESHOLD`: WPM threshold for "fast" typing (default: 50)
  - `MIN_KEYSTROKES_FOR_BURST`: Minimum keystrokes to trigger analysis (default: 10)
  - `CORRELATION_TIME_WINDOW`: Window for signal correlation in seconds (default: 5)

- **Suspicious Processes**:
  ```python
  SUSPICIOUS_PROCESSES = [
      "cmd.exe",
      "powershell.exe",
      "bash",
      "python.exe",
      # ... add more as needed
  ]
  ```

- **Response Actions**:
  ```python
  RESPONSE_ACTIONS = {
      "log": True,          # Always log
      "alert": True,        # Print to console
      "kill_process": False,  # Terminate process (enable with caution!)
  }
  ```

## Usage

### Run the Detection System

```bash
# Monitor for 60 seconds
python main.py --duration 60

# Monitor indefinitely (Ctrl+C to stop)
python main.py

# Run with custom duration
python main.py --duration 120
```

### Run Simulations

```bash
# List available scenarios
python main.py --list-scenarios

# Run FULL_ATTACK simulation
python main.py --simulate FULL_ATTACK --duration 30

# Run specific scenario
python main.py --simulate USB_INSERTION
python main.py --simulate KEYSTROKE_BURST
python main.py --simulate TERMINAL_LAUNCH
```

### Available Scenarios

1. **USB_INSERTION**: Simulates USB keyboard insertion
2. **KEYSTROKE_BURST**: Simulates abnormally fast typing (50 keystrokes in ~1.5 seconds)
3. **TERMINAL_LAUNCH**: Simulates terminal launch after USB insertion
4. **FULL_ATTACK**: Complete attack simulation with all signals (USB + keystroke + process)

## Attack Detection Patterns

The system detects the following attack patterns:

### Pattern 1: USB + Terminal Launch (High Confidence)
```
[T+1s] USB Keyboard Detected
[T+2s] Suspicious Terminal Launched
       ↓
ALERT: USB_HID_TERMINAL_ATTACK
```

### Pattern 2: Automated Keystroke Injection (Critical)
```
[T+0s] Keystroke Burst > 100 WPM detected
       ↓
ALERT: AUTOMATED_KEYSTROKE_INJECTION (CRITICAL)
```

### Pattern 3: Multi-Signal Attack (Highest Confidence)
```
[T+1s] USB Keyboard Detected
[T+2s] Keystroke Burst > 100 WPM
[T+3s] Terminal + Suspicious Command Launch
       ↓
ALERT: MULTI_SIGNAL_USB_HID_ATTACK (CRITICAL)
```

## Output Examples

### Console Alert

```
================================================================================
🚨 USB HID ATTACK DETECTED 🚨
Attack Type: MULTI_SIGNAL_USB_HID_ATTACK
Severity: CRITICAL
Time: 2024-01-15T14:23:45.123456
Attack ID: attack_1705329825.123456_140234567890

Correlated Signals (3):

  Signal 1:
    Type: usb_insertion
    Severity: MEDIUM
    Time: 2024-01-15T14:23:45.000000
    Details: {'device_id': 'USB_SIM_FULL', 'device_name': 'USB Keyboard Device'}

  Signal 2:
    Type: keystroke_burst
    Severity: CRITICAL
    Time: 2024-01-15T14:23:47.000000
    Details: {'pattern_type': 'automated', 'wpm': 120.5, 'keystroke_count': 60}

  Signal 3:
    Type: process_launch
    Severity: HIGH
    Time: 2024-01-15T14:23:48.000000
    Details: {'process_name': 'cmd.exe', 'pid': 5234, 'after_usb': True}

⚠️  IMMEDIATE ACTION REQUIRED
Check system logs for detailed information.
================================================================================
```

### Structured Log Format

```json
{
  "timestamp": "2024-01-15T14:23:45.123456",
  "level": "CRITICAL",
  "logger": "core.response_engine",
  "message": "ATTACK LOGGED: MULTI_SIGNAL_USB_HID_ATTACK",
  "module": "response_engine",
  "function": "_log_attack",
  "line": 89,
  "event_data": {
    "attack_id": "attack_1705329825.123456_140234567890",
    "attack_type": "MULTI_SIGNAL_USB_HID_ATTACK",
    "severity": "CRITICAL",
    "signal_count": 3,
    "signals": [...]
  }
}
```

## Logging

All events are logged to `logs/events.log` in JSON format for easy parsing and analysis.

```bash
# View recent alerts
tail -f logs/events.log | grep CRITICAL

# Parse logs with jq (requires jq installed)
cat logs/events.log | jq '.event_data | select(.severity=="CRITICAL")'
```

## Extending the System

### Add Custom Response Handler

```python
from core import DetectionSystem, logger

system = DetectionSystem()

def send_to_siem(attack_event):
    """Send attack to security information and event management system."""
    logger.info(f"Sending to SIEM: {attack_event.attack_type}")
    # Your SIEM integration code here

system.response_engine.register_custom_handler(send_to_siem)
system.start()
```

### Add Custom Suspicious Process

```python
from core import config

config.SUSPICIOUS_PROCESSES.append("malware.exe")
```

### Create Custom Simulation Scenario

```python
from core import AttackSimulator, SimulationScenario, DetectionSystem

system = DetectionSystem()
simulator = system.simulator

custom_scenario = SimulationScenario(
    name="CUSTOM_ATTACK",
    description="Custom attack pattern",
    duration_seconds=15,
    attack_type="CUSTOM_TYPE"
)

system.run_simulation(custom_scenario)
```

## Security Considerations

⚠️ **Important Notes**:

1. **Low-level HID Access**: Direct keystroke interception requires kernel-level drivers (unavailable without admin drivers on Windows). This system detects suspicious patterns instead.

2. **Process Termination**: The `kill_process` option is disabled by default. Enable only in controlled environments with proper authorization.

3. **False Positives**: Very fast typists or macro tools may trigger alerts. Adjust `KEYSTROKE_SPEED_THRESHOLD` in config if needed.

4. **USB Detection**: Requires WMI on Windows (available since Windows XP SP3).

5. **Privileges**: USB and process monitoring work best with administrator/root privileges.

## Performance

- **CPU**: Minimal (<1% idle)
- **Memory**: ~30-50 MB base
- **Logging**: ~1-5 KB per attack event
- **Latency**: <100ms from event to alert

## Limitations

- Only detects USB HID devices, not other attack vectors
- Keystroke analysis is pattern-based (not packet-level capture)
- Windows WMI may not detect some USB devices in consumer mode
- Process monitoring requires periodic polling (not real-time kernel events)

## Testing

Run the simulation suite:

```bash
# Run all scenarios
for scenario in USB_INSERTION KEYSTROKE_BURST TERMINAL_LAUNCH FULL_ATTACK; do
  echo "Testing $scenario..."
  python main.py --simulate $scenario --duration 15
done
```

## Troubleshooting

### "WMI not available" warning on Windows
- Install pywin32: `pip install pywin32`
- Run postinstall: `python -m Scripts/pywin32_postinstall.py -install`

### No USB devices detected
- Ensure USB device is connected and visible in Device Manager
- Try disconnecting and reconnecting the USB device
- Check that the application has appropriate privileges

### False positives from fast typists
- Increase `KEYSTROKE_SPEED_THRESHOLD` in config
- Adjust `MIN_KEYSTROKES_FOR_BURST` threshold

## License

This software is provided for defensive cybersecurity purposes. Ensure compliance with local laws regarding security monitoring and system access.

## References

- [USB Rubber Ducky](http://usbrubberducky.com) - Original attack tool
- [Keystroke Dynamics](https://en.wikipedia.org/wiki/Keystroke_dynamics)
- [Windows WMI Device Detection](https://docs.microsoft.com/en-us/windows/win32/wmisdk/wmi-start-page)

---

**Version**: 1.0  
**Last Updated**: 2024-01-15  
**Maintainers**: Cybersecurity Engineering Team

# Quick Start Guide

## Installation (5 minutes)

### 1. Install Dependencies

```bash
# On Windows
pip install -r requirements.txt

# (Windows only) Install WMI support
pip install pywin32
python -m Scripts/pywin32_postinstall.py -install
```

### 2. Run Basic Monitoring

```bash
python main.py --duration 60
```

You should see:
- System initialization message
- Console alerts if attacks are detected
- Detailed logs in `logs/events.log`

## Testing with Simulations (2 minutes)

### Run a Full Attack Simulation

```bash
# List all scenarios
python main.py --list-scenarios

# Run complete attack simulation
python main.py --simulate FULL_ATTACK --duration 30
```

Expected output:
1. System starts monitoring
2. After ~1-3 seconds: USB insertion detected
3. After ~2-4 seconds: Keystroke burst detected
4. After ~3-5 seconds: Terminal process launch detected
5. **ATTACK ALERT**: Multi-signal USB HID attack detected
6. Alert + detailed log entry created

## Key Features to Try

### 1. Individual Scenario Testing

```bash
# Test USB insertion only
python main.py --simulate USB_INSERTION

# Test keystroke burst detection
python main.py --simulate KEYSTROKE_BURST

# Test terminal launch pattern
python main.py --simulate TERMINAL_LAUNCH
```

### 2. View Attack Logs

```bash
# On Windows
type logs\events.log

# On Linux/Mac
cat logs/events.log | tail -20
```

Or with JSON formatting:
```bash
cat logs/events.log | grep -i "critical"
```

### 3. Run Examples

```bash
# Example 1: Basic monitoring
python examples.py 1

# Example 2: Custom response handlers
python examples.py 2

# Example 3: Multiple simulations
python examples.py 3

# Example 4: Statistics collection
python examples.py 4
```

## Configuration Quick Reference

Edit `core/config.py` to customize:

```python
# How fast is "too fast" typing? (words per minute)
KEYSTROKE_SPEED_THRESHOLD = 50

# Add more suspicious processes
SUSPICIOUS_PROCESSES.append("hacker-tool.exe")

# Enable process termination on critical attacks
RESPONSE_ACTIONS["kill_process"] = True

# Adjust signal correlation window
CORRELATION_TIME_WINDOW = 5.0
```

## What Gets Detected?

✅ **Pattern 1**: USB keyboard + terminal launch within 5 seconds  
✅ **Pattern 2**: Keystrokes faster than humans can type (>100 WPM)  
✅ **Pattern 3**: All three signals together = High confidence attack  

## Troubleshooting

### Not detecting USB devices?
- Ensure device is connected
- Run as Administrator (Windows)
- Try disconnecting and reconnecting USB

### Too many false positives?
- Increase `KEYSTROKE_SPEED_THRESHOLD` to 100+
- Add legitimate processes to exceptions

### WMI error on Windows?
```bash
pip install pywin32
python -m Scripts/pywin32_postinstall.py -install
```

## Architecture Overview

```
┌─ USB Monitor ──┐
│                ├─► Detection Engine ──► Response Engine
├─ Keystroke ────┤   (correlation)       (logging, alerts)
│  Analyzer      │
├─ Process ──────┤
│  Monitor       │
```

1. **USB Monitor**: Watches for new keyboard connections
2. **Keystroke Analyzer**: Detects superhuman typing speeds
3. **Process Monitor**: Tracks suspicious apps launching
4. **Detection Engine**: Correlates signals → detects attacks
5. **Response Engine**: Logs, alerts, optionally kills processes

## Production Deployment

### Enable Real Monitoring (No Simulation)

```python
from core import DetectionSystem

system = DetectionSystem(enable_simulation=False)
system.start()

# System will run indefinitely
# Press Ctrl+C to stop
```

### Add SIEM Integration

```python
def send_to_splunk(attack_event):
    import requests
    requests.post(
        "https://splunk-server/api/events",
        json={
            "attack_type": attack_event.attack_type,
            "severity": attack_event.severity.name,
            "timestamp": attack_event.timestamp.isoformat()
        }
    )

system.response_engine.register_custom_handler(send_to_splunk)
```

### Run as Service (Windows)

```batch
# Create batch file to run as service
REM start_detector.bat
@echo off
cd C:\path\to\usb_hid_attack_detection
python main.py
```

Then use Task Scheduler to run at startup with admin privileges.

## Performance Impact

- **CPU**: <1% idle (spikes to 2-5% during analysis)
- **Memory**: ~50 MB
- **Disk**: ~1-10 KB per attack event (logs only)

## Next Steps

1. ✅ Run a simulation: `python main.py --simulate FULL_ATTACK`
2. ✅ Check the logs: `cat logs/events.log`
3. ✅ Try examples: `python examples.py 1` through `6`
4. ✅ Customize config: Edit `core/config.py`
5. ✅ Deploy to production: Run with your own response handlers

## Support

For issues or questions:
- Check `logs/events.log` for detailed error information
- Review the full [README.md](README.md) for comprehensive docs
- Run with verbose output: `python main.py --duration 10` (watch console)

---

**Ready to defend against USB attacks!** 🛡️

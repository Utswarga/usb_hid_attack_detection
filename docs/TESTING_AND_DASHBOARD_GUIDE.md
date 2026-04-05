# USB HID Attack Detection System - Test & Dashboard Guide

## 📋 Overview

This guide explains how to run the comprehensive test suite and access the interactive web dashboard for the USB HID Attack Detection System.

---

## 🚀 Quick Start

### Option 1: Run Tests Only
```bash
python tests/test_detection_system.py
```

### Option 2: Start Dashboard Only
```bash
python tools/dashboard.py
```
Then open your browser to: **http://localhost:5000**

### Option 3: Use the Runner Script
```bash
# Run tests
python tools/run.py test

# Start dashboard
python tools/run.py dashboard

# Run tests then dashboard
python tools/run.py all

# Install requirements
python tools/run.py install
```

---

## 📊 Test Suite

### What's Tested

#### 1. **Detection Engine Tests** (`TestDetectionEngine`)
- ✓ Engine initialization
- ✓ Single signal addition
- ✓ Multiple signals handling
- ✓ Signal correlation detection
- ✓ Severity level handling

#### 2. **Keystroke Analyzer Tests** (`TestKeystrokeAnalyzer`)
- ✓ Analyzer initialization
- ✓ Normal typing pattern detection
- ✓ Abnormal typing speed detection
- ✓ Keystroke buffer management
- ✓ Typing statistics calculation

#### 3. **Process Monitor Tests** (`TestProcessMonitor`)
- ✓ Monitor initialization with baseline
- ✓ Suspicious process detection
- ✓ Process history tracking
- ✓ Baseline process management

#### 4. **Response Engine Tests** (`TestResponseEngine`)
- ✓ Engine initialization
- ✓ Attack response logging
- ✓ Action execution

#### 5. **Integration Tests** (`TestIntegration`)
- ✓ End-to-end attack detection flow
- ✓ Normal operation without false alerts
- ✓ Component interaction

#### 6. **Results Exportation Tests** (`TestResultsExportation`)
- ✓ JSON export functionality
- ✓ Data serialization
- ✓ Dashboard data formatting

### Running Specific Tests

```bash
# Run only detection engine tests
python -m unittest tests.test_detection_system.TestDetectionEngine

# Run only keystroke analyzer tests
python -m unittest tests.test_detection_system.TestKeystrokeAnalyzer

# Run a specific test
python -m unittest tests.test_detection_system.TestDetectionEngine.test_engine_initialization
```

### Test Output Example

```
================================================================================
USB HID ATTACK DETECTION SYSTEM - TEST SUITE
================================================================================

test_add_multiple_signals (tests.test_detection_system.TestDetectionEngine) ... ok
test_add_single_signal (tests.test_detection_system.TestDetectionEngine) ... ok
test_engine_initialization (tests.test_detection_system.TestDetectionEngine) ... ok
test_signal_correlation_detection (tests.test_detection_system.TestDetectionEngine) ... ok
test_signal_severity_levels (tests.test_detection_system.TestDetectionEngine) ... ok
test_analyzer_initialization (tests.test_detection_system.TestKeystrokeAnalyzer) ... ok
test_abnormal_typing_speed (tests.test_detection_system.TestKeystrokeAnalyzer) ... ok
test_keystroke_buffer_management (tests.test_detection_system.TestKeystrokeAnalyzer) ... ok
test_normal_typing_pattern (tests.test_detection_system.TestKeystrokeAnalyzer) ... ok

================================================================================
TEST SUMMARY
================================================================================
Tests run: 28
Successes: 28
Failures: 0
Errors: 0
================================================================================

✓ All tests passed!
```

---

## 🌐 Web Dashboard

### Access
- **URL**: http://localhost:5000
- **Port**: 5000 (configurable in `dashboard.py`)
- **Open Browser**: Automatically opens on startup (optional)

### Dashboard Features

#### 📡 **Real-Time Monitoring**
- Live system status updates every 2 seconds
- Signal history with sorting and filtering
- Uptime tracking
- Process and keystroke monitoring

#### 📊 **Statistics Panel**
- Severity distribution (Critical, High, Medium, Low)
- Total signals recorded
- Recent signals (last 5 seconds)
- Process count
- Keystroke metrics (WPM - Words Per Minute)

#### 🎮 **Interactive Controls**
- **Add Test Signal**: Inject a random signal for testing
- **Simulate Attack**: Create a multi-signal attack scenario
- **Refresh**: Manual data update
- **Clear Signals**: Reset all recorded signals

### Dashboard Sections

#### Status Bar
```
System Status: Ready              Total Signals: 15
Recent Signals (5s): 3            Uptime: 2m 30s
```

#### Recent Signals Panel
Displays the latest 10 signals with:
- Signal type (usb_insertion, process_launch, keystroke_burst, etc.)
- Severity indicator (color-coded)
- Timestamp
- Details (if available)

#### Statistics Panel
Shows:
- Critical/High/Medium/Low signal counts
- Total tracked processes
- Total recorded keystrokes
- Average WPM (typing speed)

---

## 📡 API Endpoints

All endpoints return JSON data and support real-time queries.

### System Status
```bash
GET /api/system-status

Response:
{
  "status": "idle",
  "uptime": "0:02:30.123456",
  "total_signals": 15,
  "recent_signals": 3,
  "baseline_processes": 112,
  "timestamp": "2026-04-06T00:08:58.867000"
}
```

### Get Signals
```bash
GET /api/signals?window=60

Parameters:
  - window: Time window in seconds (default: 60)

Response:
{
  "total": 15,
  "signals": [
    {
      "type": "process_launch",
      "severity": "HIGH",
      "severity_value": 3,
      "timestamp": "2026-04-06T00:08:59.024000",
      "details": {"process": "powershell.exe", "pid": 1672}
    }
  ],
  "timestamp": "2026-04-06T00:09:00.000000"
}
```

### Get Statistics
```bash
GET /api/statistics

Response:
{
  "signals": {
    "total": 15,
    "recent": 3,
    "severity_distribution": {
      "LOW": 0,
      "MEDIUM": 2,
      "HIGH": 10,
      "CRITICAL": 3
    }
  },
  "keystrokes": {
    "total_recorded": 47,
    "average_wpm": 45.5,
    "max_wpm": 120.0,
    "abnormal_patterns": 0
  },
  "processes": {
    "baseline_count": 112,
    "total_tracked": 23,
    "suspicious_recent": 1
  }
}
```

### Add Test Signal
```bash
POST /api/add-test-signal

Body:
{
  "type": "test_signal",
  "severity": "HIGH",
  "details": {"test": true}
}

Response:
{
  "success": true,
  "message": "Signal added: test_signal",
  "signal": {
    "type": "test_signal",
    "severity": "HIGH",
    "timestamp": "2026-04-06T00:09:01.000000"
  }
}
```

### Simulate Attack
```bash
POST /api/simulate-attack

Response:
{
  "success": true,
  "message": "Attack simulation added (3 correlated signals)",
  "signals_added": 3,
  "timestamp": "2026-04-06T00:09:02.000000"
}
```

### Clear Signals
```bash
POST /api/clear-signals

Response:
{
  "success": true,
  "message": "All signals cleared",
  "timestamp": "2026-04-06T00:09:03.000000"
}
```

### Health Check
```bash
GET /api/health

Response:
{
  "status": "healthy",
  "version": "1.0",
  "timestamp": "2026-04-06T00:09:04.000000"
}
```

---

## 🔍 Dashboard Color Scheme

### Severity Indicators
| Level | Color | Meaning |
|-------|-------|---------|
| CRITICAL | 🔴 Red (#dc2626) | Immediate threat detected |
| HIGH | 🟠 Orange (#ea580c) | Significant threat |
| MEDIUM | 🟡 Yellow (#eab308) | Minor concern |
| LOW | 🟢 Green (#22c55e) | Low risk |

---

## 📈 Testing Scenarios

### Scenario 1: Normal Operation Test
1. Run dashboard
2. Observe baseline signals
3. No alerts should appear with low severity signals
4. Expected result: System shows normal operation

### Scenario 2: Attack Simulation Test
1. Run dashboard
2. Click "Simulate Attack" button
3. Observe 3 correlated signals appearing
4. Check severity distribution shows HIGH signals
5. Expected result: Attack is properly detected and logged

### Scenario 3: Stress Test
1. Click "Add Test Signal" multiple times
2. Monitor performance
3. Verify all signals are logged
4. Check statistics update in real-time
5. Expected result: System handles high signal volume gracefully

---

## ⚙️ Configuration

### Test Configuration
Edit `tests/test_detection_system.py` to customize:
- Signal types to test
- Severity levels
- Time windows
- Baseline processes

### Dashboard Configuration
Edit `tools/dashboard.py` to customize:
- Port: `port=5000`
- Host: `host='0.0.0.0'`
- Auto-refresh interval: `setInterval(refreshData, 2000)`
- Debug mode: `debug=True`

### System Configuration
Edit `core/config.py` for:
- `KEYSTROKE_SPEED_THRESHOLD`: WPM threshold for fast typing
- `KEYSTROKE_TIME_WINDOW`: Analysis time window
- `CORRELATION_TIME_WINDOW`: Signal correlation window
- `SUSPICIOUS_PROCESSES`: List of suspicious process names

---

## 🐛 Troubleshooting

### Dashboard Won't Start
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Use a different port
# Edit dashboard.py: app.run(port=5001)
```

### Tests Fail
```bash
# Check dependencies
pip install -r requirements.txt

# Run with verbose output
python -m unittest tests.test_detection_system -v
```

### Missing Flask
```bash
pip install Flask>=2.3.0
```

### Cannot Import Core Modules
```bash
# Ensure you're in the project directory
cd \workspace\usb_hid_attack_detection

# Add project to Python path
set PYTHONPATH=%cd%;%PYTHONPATH%
python tests/test_detection_system.py
```

---

## 📝 Example Workflow

1. **Install Dependencies**
   ```bash
  python tools/run.py install
   ```

2. **Run Tests**
   ```bash
  python tools/run.py test
   ```

3. **Start Dashboard**
   ```bash
  python tools/run.py dashboard
   ```

4. **Test in Dashboard**
   - Open http://localhost:5000
   - Click "Simulate Attack"
   - Observe signals in real-time
   - Check statistics update
   - Click "Clear Signals" to reset

5. **Stop Dashboard**
   - Press `Ctrl+C` in the terminal

---

## 📚 Resources

- **Main Script**: [main.py](../main.py)
- **Test Suite**: [tests/test_detection_system.py](../tests/test_detection_system.py)
- **Dashboard**: [tools/dashboard.py](../tools/dashboard.py)
- **Core Components**: [core/](../core/)
- **Configuration**: [core/config.py](../core/config.py)

---

## ✅ Verification Checklist

- [ ] All tests pass
- [ ] Dashboard starts without errors
- [ ] API endpoints respond correctly
- [ ] Real-time updates work (2-second refresh)
- [ ] Signal simulation creates correlated events
- [ ] Statistics update accurately
- [ ] Color coding matches severity levels
- [ ] Clear function resets all data

---

## 📞 Support

For issues or questions:
1. Check the test output for detailed error messages
2. Review API responses in browser console (F12)
3. Check system logs in `logs/events.log`
4. Verify all requirements are installed

---

**Last Updated**: April 6, 2026
**Version**: 1.0

# USB HID Attack Detection System - Complete Setup & Run Guide

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Running Tests](#running-tests)
6. [Running Dashboard](#running-dashboard)
7. [Project Structure](#project-structure)
8. [API Reference](#api-reference)
9. [Testing Scenarios](#testing-scenarios)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

The **USB HID Attack Detection System** is a comprehensive security monitoring solution designed to detect and prevent USB-based HID (Human Interface Device) attacks, including:

- USB keyboard/mouse hijacking
- Keystroke injection attacks
- Suspicious process launches following USB insertion
- Abnormal typing patterns (automated keystroke injection)
- Multi-signal correlated attacks
- Raspberry Pi Pico-like HID fingerprinted attacks (Rubber Ducky style)

### Key Components:

- **Detection Engine** - Correlates multiple security signals
- **USB Monitor** - Tracks USB device connections
- **Process Monitor** - Detects suspicious process launches
- **Keystroke Analyzer** - Analyzes typing patterns for anomalies
- **Response Engine** - Takes responsive actions on detected threats
- **Web Dashboard** - Real-time visualization of system status and signals

### Pico-Specific Defense Features

- **USB fingerprinting** for Pico-like devices using VID/PID and product-name markers
- **Device trust labels** to reduce noise from known keyboard models
- **Risk reasons** attached to USB signals for explainable alerts in dashboard/API
- **Pico-focused attack types** in correlation engine:
  - `PICO_HID_TERMINAL_ATTACK`
  - `PICO_RUBBER_DUCKY_ATTACK`

---

## ✅ System Requirements

### Minimum Requirements:

- **OS**: Windows 10/11 (64-bit) or Linux/macOS
- **Python**: 3.9+ (3.11 recommended)
- **RAM**: 512 MB
- **Disk Space**: 500 MB
- **Network**: Optional (for dashboard access)

### Python Packages:

All dependencies are listed in `requirements.txt`:
- `psutil>=5.9.0` - System and process monitoring
- `pywin32>=305` - Windows API integration (Windows only)
- `Flask>=2.3.0` - Web dashboard framework
- `Werkzeug>=2.3.0` - WSGI utilities for Flask

---

## 🚀 Installation

### Step 1: Clone/Download the Repository

```bash
cd \workspace\usb_hid_attack_detection
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

**Using the runner script:**
```bash
python tools/run.py install
```

**Or manually:**
```bash
pip install -r requirements.txt
```

Expected output:
```
Successfully installed psutil-7.2.2 pywin32-311 Flask-2.3.0 Werkzeug-2.3.0
```

### Step 4: Verify Installation

```bash
python -c "import psutil; import flask; print('All dependencies installed!')"
```

---

## ⚡ Quick Start

### Option 1: Run Tests Only (Fastest)

```bash
python tests/test_detection_system.py
```

**Expected Output:**
```
================================================================================
USB HID ATTACK DETECTION SYSTEM - TEST SUITE
================================================================================

test_add_multiple_signals ... ok
test_add_single_signal ... ok
test_engine_initialization ... ok
[... 14 more tests ...]

================================================================================
TEST SUMMARY
================================================================================
Tests run: 19
Successes: 19
Failures: 0
Errors: 0
================================================================================

✓ All tests passed!
```

**Duration:** ~100ms

### Option 2: Run Dashboard Only

```bash
python tools/dashboard.py
```

**Expected Output:**
```
================================================================================
USB HID ATTACK DETECTION - DASHBOARD SERVER
================================================================================

🌐 Dashboard available at: http://localhost:5000

📊 API endpoints:
   - GET  /api/system-status
   - GET  /api/signals
   - GET  /api/statistics
   - POST /api/add-test-signal
   - POST /api/simulate-attack
   - POST /api/clear-signals
   - GET  /api/health

================================================================================
```

Then open browser: **http://localhost:5000**

### Option 3: Run Everything (Tests + Dashboard)

```bash
python tools/run.py all
```

This will:
1. Run All 19 tests
2. If tests pass → automatically start the dashboard
3. Open **http://localhost:5000** in your browser

---

## 🧪 Running Tests

### Run All Tests

```bash
python tests/test_detection_system.py
```

### Run Specific Test Class

```bash
python -m unittest tests.test_detection_system.TestDetectionEngine
```

### Run Specific Test

```bash
python -m unittest tests.test_detection_system.TestDetectionEngine.test_engine_initialization
```

### Run with Verbose Output

```bash
python -m unittest tests.test_detection_system -v
```

### Test Categories

The test suite includes **19 comprehensive tests** across 6 test classes:

#### 1. Detection Engine Tests (5 tests)
- `test_engine_initialization` - Verify engine initializes correctly
- `test_add_single_signal` - Test adding one signal
- `test_add_multiple_signals` - Test adding multiple signals
- `test_signal_correlation_detection` - Verify signal correlation works
- `test_signal_severity_levels` - Test all severity levels (LOW/MEDIUM/HIGH/CRITICAL)

#### 2. Keystroke Analyzer Tests (4 tests)
- `test_analyzer_initialization` - Verify analyzer initializes
- `test_normal_typing_pattern` - Test normal typing detection
- `test_abnormal_typing_speed` - Test fast typing detection
- `test_keystroke_buffer_management` - Verify buffer limits

#### 3. Process Monitor Tests (3 tests)
- `test_monitor_initialization` - Verify baseline processes loaded
- `test_detect_new_suspicious_process` - Test suspicious process detection
- `test_track_process_history` - Test process history tracking

#### 4. Response Engine Tests (2 tests)
- `test_response_engine_initialization` - Verify engine initializes
- `test_attack_response_logged` - Verify response logging

#### 5. Integration Tests (2 tests)
- `test_end_to_end_attack_detection` - Full attack detection flow
- `test_normal_operation_no_alerts` - Verify no false positives

#### 6. Results Exportation Tests (1 test)
- `test_export_results_json` - Verify JSON export functionality

---

## 🌐 Running Dashboard

### Start Dashboard

```bash
python tools/dashboard.py
```

### Access Dashboard

Open browser to: **http://localhost:5000**

### Dashboard Features

#### Status Bar
- **System Status** - Current system state (Running/Idle)
- **Total Signals** - Cumulative signal count
- **Recent Signals** - Signals in last 6 seconds
- **Uptime** - System uptime counter

#### Signals Monitor Panel
- Displays last 10 signals
- Shows signal type (USB insertion, process launch, keystroke burst, etc.)
- Color-coded severity indicators
- Timestamps for each signal

#### Statistics Panel
- **Severity Distribution** - Count of CRITICAL/HIGH/MEDIUM/LOW signals
- **Process Metrics** - Total processes tracked, suspicious processes
- **Keystroke Metrics** - Total keystrokes, average WPM (words per minute)

#### Interactive Controls
- **+ Add Test Signal** - Injects a random test signal
- **\* Simulate Attack** - Creates 3 correlated signals (USB + process + keystroke)
- **\* Refresh** - Manual data refresh (auto-refreshes every 2 seconds)
- **X Clear Signals** - Resets all signal history

### Auto-Refresh

Dashboard automatically updates every 2 seconds. Manually refresh anytime with the Refresh button.

---

## 📁 Project Structure

```
usb_hid_attack_detection/
│
├── main.py                             # Main detection system entry point
├── requirements.txt                    # Python dependencies
├── .gitignore                          # Git ignore rules
│
├── core/                               # Core system components
│   ├── __init__.py
│   ├── config.py                       # Configuration constants
│   ├── logger.py                       # Logging system
│   ├── detection_engine.py             # Attack detection engine
│   ├── keystroke_analyzer.py           # Keystroke pattern analysis
│   ├── process_monitor.py              # Process monitoring
│   ├── response_engine.py              # Response actions
│   ├── usb_monitor.py                  # USB device monitoring
│   └── simulation.py                   # Attack simulation
│
├── tests/                              # Test suite
│   ├── __init__.py
│   └── test_detection_system.py        # Comprehensive test suite (19 tests)
│
├── tools/                              # Utility scripts
│   ├── dashboard.py                    # Web dashboard server
│   └── run.py                          # Command runner script
│
├── templates/                          # Web templates
│   └── dashboard.html                  # Dashboard UI
│
├── logs/                               # Log files
│   ├── events.log                      # System event logs
│   └── .gitkeep
│
└── Documentation/
    ├── README.md                       # Project overview
    ├── ARCHITECTURE.md                 # System architecture
    ├── PROJECT_STRUCTURE.md            # Project organization
    ├── QUICKSTART.md                   # Quick start guide
    ├── IMPLEMENTATION_SUMMARY.md             # Solution overview
    ├── TESTING_AND_DASHBOARD_GUIDE.md         # Detailed test/dashboard guide
    └── SETUP_AND_RUN.md                # This file
```

---

## 📡 API Reference

All endpoints return JSON responses. Base URL: `http://localhost:5000`

### System Status

**GET** `/api/system-status`

Returns current system status and metrics.

**Response:**
```json
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

**GET** `/api/signals?minutes=1`

Returns signals within specified time window.

**Parameters:**
- `minutes` (optional) - Time window in minutes (default: 1)

**Response:**
```json
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

**GET** `/api/statistics`

Returns comprehensive system statistics.

**Response:**
```json
{
  "signals": {
    "total": 15,
    "recent": 3,
    "severity_distribution": {
      "LOW": 2,
      "MEDIUM": 4,
      "HIGH": 6,
      "CRITICAL": 3
    }
  },
  "keystrokes": {
    "total_recorded": 47,
    "average_wpm": 45.5,
    "max_wpm": 120.0,
    "abnormal_patterns": 2
  },
  "processes": {
    "baseline_count": 112,
    "total_tracked": 23,
    "suspicious_recent": 1
  }
}
```

### Add Test Signal

**POST** `/api/add-test-signal`

Adds a test signal to the detection engine.

**Request Body:**
```json
{
  "type": "test_signal",
  "severity": "HIGH",
  "details": {"test": true}
}
```

**Response:**
```json
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

**POST** `/api/simulate-attack`

Creates 3 correlated signals simulating a real attack scenario.

**Response:**
```json
{
  "success": true,
  "message": "Attack simulation added (3 correlated signals)",
  "signals_added": 3,
  "timestamp": "2026-04-06T00:09:02.000000"
}
```

### Clear Signals

**POST** `/api/clear-signals`

Clears all recorded signals from history.

**Response:**
```json
{
  "success": true,
  "message": "All signals cleared",
  "timestamp": "2026-04-06T00:09:03.000000"
}
```

### Health Check

**GET** `/api/health`

Simple health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0",
  "timestamp": "2026-04-06T00:09:04.000000"
}
```

---

## 🧬 Testing Scenarios

### Scenario 1: Basic Functionality Test

**Goal:** Verify all tests pass

**Steps:**
1. Run tests:
   ```bash
   python tests/test_detection_system.py
   ```
2. Verify output shows "17 successes, 0 failures"
3. Expected duration: ~100ms

**Expected Result:** ✅ All tests pass

### Scenario 2: Dashboard Simulation Test

**Goal:** Test attack detection with real-time visualization

**Steps:**
1. Start dashboard:
   ```bash
   python tools/dashboard.py
   ```
2. Open browser to `http://localhost:5000`
3. Click "Simulate Attack" button
4. Observe 3 signals appear in Signals Monitor panel
5. Check Statistics panel shows HIGH severity signals
6. Click "Refresh" to update manually
7. Click "Clear Signals" to reset

**Expected Result:** ✅ Attack simulation creates correlated signals, dashboard updates in real-time

### Scenario 3: Manual Signal Injection

**Goal:** Test individual signal injection

**Steps:**
1. Dashboard running at `http://localhost:5000`
2. Click "+ Add Test Signal" multiple times
3. Each click adds a random severity signal
4. Observe signals appear immediately
5. Check severity distribution updates
6. Note timestamps are current

**Expected Result:** ✅ Signals appear in real-time with correct timestamps

### Scenario 4: Stress Test

**Goal:** Verify system handles high signal volume

**Steps:**
1. Dashboard running
2. Click "+ Add Test Signal" 50+ times rapidly
3. Observe dashboard performance
4. Check Statistics panel updates accurately
5. Verify no data loss

**Expected Result:** ✅ Dashboard remains responsive, all signals logged

### Scenario 5: End-to-End Integration

**Goal:** Test complete system flow

**Steps:**
1. Run tests (all pass)
2. Start dashboard (no errors)
3. Simulate attack (signals appear)
4. Check API endpoints respond
5. Verify JSON responses are valid
6. Clear signals and reset

**Expected Result:** ✅ All components work together seamlessly

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'psutil'"

**Cause:** Dependencies not installed

**Solution:**
```bash
python tools/run.py install
# OR
pip install -r requirements.txt
```

### Issue: "Port 5000 already in use"

**Cause:** Another application using port 5000

**Solution:**
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process (Windows)
taskkill /PID <PID> /F

# Or use different port
# Edit tools/dashboard.py line 196:
# start_dashboard(port=5001)
```

### Issue: "Failed to import from core"

**Cause:** Working directory not set correctly

**Solution:**
```bash
# Ensure you're in project root
cd \workspace\usb_hid_attack_detection

# Then run commands
python tests/test_detection_system.py
python tools/dashboard.py
```

### Issue: Dashboard won't load at localhost:5000

**Cause:** Flask not started properly

**Solution:**
1. Check console for errors
2. Verify Flask installed:
   ```bash
   pip show Flask
   ```
3. Check if port is accessible:
   ```bash
   netstat -ano | findstr LISTENING | findstr 5000
   ```
4. Try different port:
   ```bash
   # Edit tools/dashboard.py
   # Change: start_dashboard(port=5001)
   ```

### Issue: Tests fail with "AttributeError"

**Cause:** Core modules missing attributes

**Solution:**
1. Verify core files aren't corrupted:
   ```bash
   python -c "from core import detection_engine; print('OK')"
   ```
2. Check Python version (3.9+ required)
3. Reinstall dependencies:
   ```bash
   pip install --force-reinstall -r requirements.txt
   ```

### Issue: "permission denied" error

**Cause:** File permissions on Linux/macOS

**Solution:**
```bash
chmod +x tools/run.py
chmod +x tests/test_detection_system.py
```

### Issue: Virtual environment not activating

**Windows:**
```bash
.venv\Scripts\activate.bat
# OR
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

---

## 📞 Support & Resources

### Key Files for Reference:
- **Architecture**: `ARCHITECTURE.md`
- **Project Structure**: `PROJECT_STRUCTURE.md`
- **Dashboard Details**: `TESTING_AND_DASHBOARD_GUIDE.md`
- **Solution Overview**: `IMPLEMENTATION_SUMMARY.md`

### Common Commands:

```bash
# Run all tests
python tests/test_detection_system.py

# Start dashboard
python tools/dashboard.py

# Using runner script
python tools/run.py test        # Run tests
python tools/run.py dashboard   # Start dashboard
python tools/run.py all         # Tests then dashboard
python tools/run.py install     # Install dependencies

# Individual test
python -m unittest tests.test_detection_system.TestDetectionEngine

# Verbose test output
python -m unittest tests.test_detection_system -v

# Check health
curl http://localhost:5000/api/health
```

---

## ✅ Verification Checklist

- [ ] Python 3.9+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] All 19 tests pass
- [ ] Dashboard starts without errors
- [ ] Dashboard loads at http://localhost:5000
- [ ] API endpoints respond with JSON
- [ ] Real-time updates work (2-second refresh)
- [ ] Test signal injection works
- [ ] Attack simulation creates signals
- [ ] Statistics update accurately

---

## 🎓 Quick Reference

| Task | Command | Time |
|------|---------|------|
| Install deps | `python tools/run.py install` | 1-2 min |
| Run tests | `python tests/test_detection_system.py` | ~100ms |
| Start dashboard | `python tools/dashboard.py` | instant |
| Run all | `python tools/run.py all` | ~2 sec + dashboard |
| Test single | `python -m unittest tests.test_detection_system.TestDetectionEngine.test_engine_initialization` | ~50ms |

---

**Last Updated**: April 6, 2026  
**Version**: 1.0  
**Status**: Complete & Ready for Production

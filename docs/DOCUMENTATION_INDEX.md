# 📑 File and Folder Organization Guide

This document explains the organization of all files and folders in the USB HID Attack Detection System project.

Current scope includes Raspberry Pi Pico Rubber Ducky style attack defense via
USB fingerprinting + behavior correlation.

## 📂 Root Directory Files

### Getting Started
| File | Purpose |
|------|---------|
| **OVERVIEW_GUIDE.md** | Quick overview and feature list (START HERE!) |
| **SETUP_AND_RUN.md** | ⭐ **COMPLETE SETUP GUIDE** - 200+ lines with every step explained |
| **DOCUMENTATION_INDEX.md** | This file - explains project organization |

### Additional Documentation
| File | Purpose |
|------|---------|
| **ARCHITECTURE.md** | System design, components, and flow diagrams |
| **PROJECT_STRUCTURE.md** | Detailed file organization |
| **QUICKSTART.md** | Quick start guide |
| **IMPLEMENTATION_SUMMARY.md** | Solution overview and features |
| **TESTING_AND_DASHBOARD_GUIDE.md** | Detailed test suite and dashboard documentation |

### Project Files
| File | Purpose |
|------|---------|
| **main.py** | Main detection system entry point |
| **requirements.txt** | Python package dependencies |
| **.gitignore** | Git ignore rules |

---

## 📁 Folder Structure

### `core/` - Core System Components
The heart of the detection system. Contains all detection logic.

```
core/
├── __init__.py                  # Module initialization
├── config.py                    # Configuration constants and settings
├── logger.py                    # Structured logging system
├── detection_engine.py          # Signal correlation & attack detection (KEY)
├── keystroke_analyzer.py        # Keystroke pattern analysis
├── process_monitor.py           # Process tracking and baseline
├── response_engine.py           # Response actions on detected attacks
├── usb_monitor.py               # USB device monitoring
└── simulation.py                # Attack simulation for testing
```

**Key Files:**
- **detection_engine.py** - Correlates signals to detect attacks
- **keystroke_analyzer.py** - Analyzes typing patterns
- **process_monitor.py** - Tracks suspicious processes  
- **usb_monitor.py** - Monitors USB device connections and tags Pico-like fingerprints

---

### `tests/` - Test Suite
19 comprehensive tests covering all components.

```
tests/
├── __init__.py                            # Module initialization
└── test_detection_system.py               # MAIN TEST FILE
    ├── TestDetectionEngine (5 tests)      # Detection engine tests
    ├── TestKeystrokeAnalyzer (4 tests)   # Keystroke analyzer tests
    ├── TestProcessMonitor (3 tests)       # Process monitor tests
    ├── TestResponseEngine (2 tests)       # Response engine tests
    ├── TestIntegration (2 tests)          # Full system integration tests
    └── TestResultsExportation (1 test)    # JSON export tests
```

**Run Tests:**
```bash
python tests/test_detection_system.py
```

**Expected Output:**
```
Tests run: 19
Successes: 19
Failures: 0
```

---

### `tools/` - Utility Scripts
Command-line tools for running the system.

```
tools/
├── run.py                       # MAIN RUNNER SCRIPT
│   ├── test command             # Run all tests
│   ├── dashboard command        # Start dashboard
│   ├── all command              # Tests + dashboard
│   └── install command          # Install dependencies
│
└── dashboard.py                 # Flask web dashboard
    ├── @app.route('/')          # Main dashboard page
    ├── @app.route('/api/...')   # API endpoints (7 total)
    └── start_dashboard()        # Server startup
```

**Quick Commands:**
```bash
python tools/run.py test           # Run tests
python tools/run.py dashboard      # Start dashboard
python tools/run.py all            # Tests then dashboard
python tools/run.py install        # Install deps
```

---

### `templates/` - Web Interface
HTML templates for the web dashboard.

```
templates/
└── dashboard.html               # Main dashboard UI (single page HTML)
    ├── <head>                   # CSS styling (embedded)
    ├── <body>                   # Dashboard layout
    └── <script>                 # JavaScript functionality
```

**Features:**
- Status bar with metrics
- Signals monitor panel
- Statistics panel
- Interactive buttons
- 2-second auto-refresh

---

### `logs/` - Event Logs
System event logging directory.

```
logs/
├── events.log                   # Main event log file
└── .gitkeep                     # Ensures folder exists in git
```

**Log Format:**
```
2026-04-06 00:08:58,867 - INFO - core.logger - Initializing USB HID Attack Detection System...
2026-04-06 00:08:58,870 - WARNING - core.usb_monitor - WMI not available - USB monitoring will use fallback method
```

---

## 📊 File Count Summary

```
Total Files: ~35
├── Python Files: 15 (core modules + tests + tools)
├── Documentation: 8
├── Config Files: 1 (requirements.txt)
├── Web Templates: 1
└── Other: 10+ (logs, git files, cache)
```

---

## 🗺️ Important File Locations

### Starting Point
```
OVERVIEW_GUIDE.md                           # Start here for overview
SETUP_AND_RUN.md                        # Complete setup instructions
```

### Test Execution
```
tests/test_detection_system.py          # Run tests from here
```

### Dashboard Launch
```
tools/dashboard.py                      # Web dashboard server
tools/templates/dashboard.html          # Dashboard UI
```

### System Configuration
```
core/config.py                          # Configuration constants
core/logger.py                          # Logging configuration
```

---

## 🔄 Typical File Access Pattern

### For Testing:
```
1. Run: python tests/test_detection_system.py
2. Imports: core/* modules
3. Output: Test results to console + logs/events.log
```

### For Dashboard:
```
1. Run: python tools/dashboard.py
2. Imports: core/* modules
3. Serves: templates/dashboard.html
4. Uses: core/detection_engine.py (main logic)
5. Output: logs/events.log
```

### For Main System:
```
1. Run: python main.py
2. Imports: core/* modules
3. Uses: All core components
4. Output: logs/events.log
```

---

## 📝 Documentation Files Quick Reference

| File | Read Time | Content |
|------|-----------|---------|
| **OVERVIEW_GUIDE.md** | 5 min | Overview, features, quick start |
| **SETUP_AND_RUN.md** | 20 min | ⭐ Complete setup guide (MUST READ) |
| **ARCHITECTURE.md** | 10 min | System design, diagrams |
| **PROJECT_STRUCTURE.md** | 5 min | File organization details |
| **TESTING_AND_DASHBOARD_GUIDE.md** | 15 min | Test & dashboard details |
| **IMPLEMENTATION_SUMMARY.md** | 5 min | Solution overview |
| **QUICKSTART.md** | 3 min | Quick start guide |
| **DOCUMENTATION_INDEX.md** | 5 min | This file |

**Recommended Reading Order:**
1. OVERVIEW_GUIDE.md (overview)
2. SETUP_AND_RUN.md (setup instructions)
3. ARCHITECTURE.md (system design)
4. TESTING_AND_DASHBOARD_GUIDE.md (detailed docs)

---

## 🔧 How to Navigate

### I want to...

**...understand the project quickly**
→ Read [OVERVIEW_GUIDE.md](OVERVIEW_GUIDE.md)

**...install and run the system**
→ Read [SETUP_AND_RUN.md](SETUP_AND_RUN.md) - Complete step-by-step guide

**...run the tests**
→ Execute: `python tests/test_detection_system.py`

**...start the dashboard**
→ Execute: `python tools/dashboard.py` then open http://localhost:5000

**...understand the system architecture**
→ Read [ARCHITECTURE.md](ARCHITECTURE.md)

**...learn how to use the API**
→ See [SETUP_AND_RUN.md](SETUP_AND_RUN.md) API Reference section

**...troubleshoot issues**
→ See [SETUP_AND_RUN.md](SETUP_AND_RUN.md) Troubleshooting section

**...see test details**
→ Read [TESTING_AND_DASHBOARD_GUIDE.md](TESTING_AND_DASHBOARD_GUIDE.md)

---

## 📋 Checklist for First-Time Users

- [ ] Read [OVERVIEW_GUIDE.md](OVERVIEW_GUIDE.md) (5 minutes)
- [ ] Read [SETUP_AND_RUN.md](SETUP_AND_RUN.md) (20 minutes) ⭐ IMPORTANT
- [ ] Run `python tools/run.py install` (2 minutes)
- [ ] Run `python tests/test_detection_system.py` (verify setup)
- [ ] Run `python tools/dashboard.py` (launch dashboard)
- [ ] Open http://localhost:5000 in browser
- [ ] Click "Simulate Attack" button (test functionality)
- [ ] Check [SETUP_AND_RUN.md](SETUP_AND_RUN.md) if any issues

---

## 🎯 Key Takeaways

1. **All Documentation**: See [SETUP_AND_RUN.md](SETUP_AND_RUN.md) first
2. **Test Location**: `tests/test_detection_system.py` (19 tests)
3. **Dashboard Location**: `tools/dashboard.py` (web UI)
4. **Core Logic**: `core/` folder (8 modules)
5. **Configuration**: `core/config.py`
6. **Logs**: `logs/events.log`

---

## 🚀 Getting Started

```bash
# Step 1: Install
python tools/run.py install

# Step 2: Test
python tests/test_detection_system.py

# Step 3: Dashboard
python tools/dashboard.py

# Then open: http://localhost:5000
```

---

**For complete setup instructions, refer to:** [SETUP_AND_RUN.md](SETUP_AND_RUN.md)

**Version:** 1.0  
**Last Updated:** April 6, 2026

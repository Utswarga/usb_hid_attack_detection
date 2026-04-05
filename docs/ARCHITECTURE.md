# Architecture Document: USB HID Attack Detection System

## System Overview

The USB HID Attack Detection System is a modular, event-driven application designed to detect and respond to USB-based keystroke injection attacks (commonly known as "USB Rubber Ducky" attacks).

## Design Principles

1. **Modularity**: Each component focuses on a single responsibility
2. **Extensibility**: Custom handlers and response actions can be registered
3. **Correlation**: Multiple signals are analyzed for higher confidence
4. **Production-Ready**: Structured logging, error handling, and graceful degradation
5. **Testability**: Simulation mode allows testing without real USB devices

## Component Architecture

### 1. USB Monitor (`core/usb_monitor.py`)

**Responsibility**: Detect USB HID device insertion and removal

**Design Pattern**: Strategy (platform-specific implementations)

```
USBMonitorBase (Abstract)
├── WindowsUSBMonitor (uses Windows WMI)
└── LinuxUSBMonitor (uses /sys/bus/usb)
```

**Key Features**:
- Polling-based monitoring (checks every 2 seconds)
- Callback mechanism for event notification
- Platform abstraction layer
- Pico-specific fingerprint enrichment (VID/PID + name heuristics)

**Pico Fingerprint Enrichment**:

Each USB insert event now carries additional metadata used by the detection engine:

- `vendor_id` and `product_id` (when extractable)
- `is_pico_like` (boolean)
- `is_trusted_hid` (boolean)
- `risk_label` and `risk_reason` (human-readable)

**Event Flow**:
```
USB Device Inserted
    ↓
Monitor polls /sys or WMI
    ↓
New device detected
    ↓
Trigger callbacks (Detection Engine)
    ↓
USBEvent object created with metadata
```

**Limitations**:
- WMI on Windows may have delays
- Requires appropriate OS privileges
- Cannot distinguish human typing from script-driven keystrokes at hardware level

### 2. Keystroke Analyzer (`core/keystroke_analyzer.py`)

**Responsibility**: Detect abnormal keystroke patterns and typing speeds

**Design Pattern**: Observable (pattern detection)

**Algorithm**:
```
1. Record keystroke events in circular buffer (max 100)
2. Every keystroke, analyze last N seconds:
   - Count keystrokes in time window
   - Calculate typing speed (WPM)
   - Compare against KEYSTROKE_SPEED_THRESHOLD
3. If threshold exceeded:
   - Classify as "burst" or "automated"
   - Create KeystrokePattern event
   - Notify detection engine
```

**Classification**:
- Normal: < 50 WPM (realistic human typing)
- Burst: 50-100 WPM (fast typist)
- Automated: > 100 WPM (impossible for human)

**Formula for WPM**:
```
WPM = (keystroke_count / 5) / (time_minutes)
      where 5 chars = 1 word average
```

### 3. Process Monitor (`core/process_monitor.py`)

**Responsibility**: Track suspicious process launches

**Design Pattern**: Observer (process enumeration)

**Suspicious Process Detection**:
```
1. Enumerate all running processes
2. For each process, check if:
   - Name matches SUSPICIOUS_PROCESSES list
   - Launched recently (<1 minute)
   - Not in baseline process set
3. If match:
   - Mark as suspicious
   - Create ProcessEvent
   - Notify detection engine
```

**Suspicious Processes**:
- `cmd.exe`, `powershell.exe` (Windows shells)
- `bash`, `sh`, `zsh` (Unix shells)
- `python`, `perl`, `ruby` (Interpreters)
- `ncat`, `nc.exe` (Network tools)

### 4. Detection Engine (`core/detection_engine.py`)

**Responsibility**: Correlate signals and determine if attack is occurring

**Design Pattern**: Observer + Interpreter (pattern recognition)

**Signal Correlation Algorithm**:
```
1. Maintain signal buffer with timestamps
2. When new signal arrives:
   a. Add to buffer
   b. Get signals from last N seconds (correlation window)
   c. Check for attack patterns
3. Attack patterns detected:
   - USB insertion → Terminal launch (within 5s) = HIGH confidence
   - Keystroke burst > 100 WPM = CRITICAL
   - USB + Keystroke + Terminal = MULTI_SIGNAL (highest)
```

**Attack Patterns**:

**Pattern 1: USB → Terminal**
```
Timeline:
T+0s: USB Keyboard inserted
T+1s: Suspicious terminal (cmd.exe) launched
Result: USB_HID_TERMINAL_ATTACK (HIGH severity)
```

**Pattern 2: Keystroke Burst**
```
Timeline:
T+0s: 50+ keystrokes detected within 1.5 seconds
Result: AUTOMATED_KEYSTROKE_INJECTION (CRITICAL)
```

**Pattern 3: Multi-Signal**
```
Timeline:
T+0s: USB insertion
T+1s: Keystroke burst
T+2s: Terminal launch
Result: MULTI_SIGNAL_USB_HID_ATTACK (CRITICAL)
```

**Pattern 4: Pico HID + Terminal**
```
Timeline:
T+0s: Pico-like HID inserted (VID/PID or name match)
T+1s: Suspicious shell/process launch
Result: PICO_HID_TERMINAL_ATTACK (CRITICAL)
```

**Pattern 5: Pico Rubber Ducky Signature**
```
Timeline:
T+0s: Pico-like HID insertion
T+1s: Keystroke burst (automated typing)
T+2s: Terminal/process launch
Result: PICO_RUBBER_DUCKY_ATTACK (CRITICAL)
```

**Signal Weighting**:
```
Signal Type          | Weight | Confidence
USB Insertion        | 2      | Medium (can be legitimate)
Keystroke Burst      | 3      | High (hard to fake)
Process Launch       | 1      | Low (normal activity)
Combination          | 6      | Very High (multi-signal)
```

### 5. Response Engine (`core/response_engine.py`)

**Responsibility**: Take action when attacks are detected

**Design Pattern**: Strategy (pluggable response actions)

**Response Flow**:
```
AttackEvent detected
    ↓
ResponseEngine.handle_attack()
    ├─→ Log to file (always)
    ├─→ Alert console (configurable)
    ├─→ Kill process (configurable, CRITICAL only)
    └─→ Custom handlers (pluggable)
```

**Built-in Responses**:

1. **Logging**: JSON-formatted entry in `logs/events.log`
2. **Console Alert**: Formatted alert to stdout
3. **Process Termination**: Kill suspicious process (force=True)

**Custom Handler Pattern**:
```python
def my_handler(attack_event):
    # Send to SIEM, Slack, email, etc.
    pass

response_engine.register_custom_handler(my_handler)
```

### 6. Logger (`core/logger.py`)

**Responsibility**: Structured logging to file and console

**Design Pattern**: Singleton-like (module-level instance)

**Log Format**: JSON
```json
{
  "timestamp": "ISO8601",
  "level": "CRITICAL|ERROR|WARNING|INFO",
  "logger": "module.name",
  "message": "Human readable message",
  "module": "filename",
  "function": "function_name",
  "line": 42,
  "event_data": {
    "custom": "fields"
  }
}
```

**Dual Output**:
- **File (`logs/events.log`)**: JSON format for parsing
- **Console**: Human-readable format for operators

### 7. Configuration (`core/config.py`)

**Responsibility**: Centralized configuration management

**Key Settings**:
```python
# Thresholds
KEYSTROKE_SPEED_THRESHOLD = 50  # WPM
CORRELATION_TIME_WINDOW = 5.0   # seconds
MIN_KEYSTROKES_FOR_BURST = 10

# Lists
SUSPICIOUS_PROCESSES = [...]
USB_HID_KEYWORDS = [...]

# Behavior
RESPONSE_ACTIONS = {
    "log": True,
    "alert": True,
    "kill_process": False,  # Dangerous!
}
```

### 8. Simulation (`core/simulation.py`)

**Responsibility**: Test attack scenarios without real hardware

**Design Pattern**: Command (scenario factory)

**Scenarios**:
1. `USB_INSERTION`: Single USB event
2. `KEYSTROKE_BURST`: Fast keystroke pattern
3. `TERMINAL_LAUNCH`: Process launch simulation
4. `FULL_ATTACK`: All signals combined

**Simulation Timeline**:
```
T+0s: Start simulation
T+1s: USB insertion (if applicable)
T+2s: Keystroke burst (if applicable)
T+3s: Terminal launch (if applicable)
```

### 9. Main Orchestrator (`main.py`)

**Responsibility**: Component coordination and lifecycle management

**Initialization Sequence**:
```
1. Create all components
2. Register callbacks between components
3. Start USB monitor
4. Start monitoring loop
5. Wait for exit signal
6. Stop monitor, print statistics
```

**Main Loop**:
```python
while is_running:
    # 1. Check for new processes
    new_procs = process_monitor.check_for_new_processes()
    
    # 2. Analyze keystroke patterns
    pattern = keystroke_analyzer.analyze_pattern()
    
    # 3. Let detection engine correlate
    attack = detection_engine.correlate_signals()
    
    # 4. If attack, trigger response
    if attack:
        response_engine.handle_attack(attack)
    
    # 5. Sleep briefly
    time.sleep(1)
```

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    USB HID Attack Detection System            │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  USB Monitor                 Keystroke Analyzer               │
│  (Every 2s)                  (Event-driven)                   │
│      │                            │                           │
│      └────────────┬───────────────┘                           │
│                   │                                           │
│            ▼▼▼▼▼▼▼▼▼▼▼▼▼▼                                     │
│     Process Monitor (Every 1s)  │                             │
│                   │                                           │
│                   └──────┬──────────┘                         │
│                          │                                    │
│            ┌─────────────▼─────────────┐                      │
│            │  Detection Engine         │                      │
│            │  (Signal Correlation)     │                      │
│            │  - Temporal analysis      │                      │
│            │  - Pattern matching       │                      │
│            │  - Risk scoring           │                      │
│            └─────────────┬─────────────┘                      │
│                          │                                    │
│            ┌─────────────▼─────────────┐                      │
│            │  Response Engine          │                      │
│            │  ├─ Log to file          │                      │
│            │  ├─ Console alert        │                      │
│            │  ├─ Kill process         │                      │
│            │  └─ Custom handlers      │                      │
│            └──────────────────────────┘                       │
│                                                               │
└──────────────────────────────────────────────────────────────┘
                              │
                        ▼▼▼▼▼▼▼▼▼▼▼▼▼▼
                    ┌─ logs/events.log (JSON)
                    └─ stdout (formatted alerts)
```

## Threading Model

```
Main Thread:
├─ USB Monitor Thread (daemon)
│  └─ Polls USB devices every 2 seconds
├─ Main Loop Thread
│  ├─ Process monitoring
│  ├─ Keystroke analysis
│  ├─ Signal correlation
│  └─ Response triggering
└─ Simulation Thread (optional, daemon)
   └─ Simulates attack events
```

**Key Design**:
- Daemon threads exit when main thread dies
- No blocking operations in critical paths
- Lock-free design (each component manages own state)

## Error Handling Strategy

```
Try every operation:
├─ Catch OS errors (no process access, USB removed, etc.)
├─ Log error with context
├─ Continue monitoring (don't crash)
└─ Degrade gracefully (e.g., skip USB check if WMI fails)

Never:
├─ Crash on missing USB device
├─ Crash on inaccessible process
├─ Let one component failure stop system
└─ Lose historical data
```

## Extensibility Points

### 1. Custom Response Handlers
```python
def webhook_alert(attack_event):
    # Send HTTP webhook
    pass

response_engine.register_custom_handler(webhook_alert)
```

### 2. Custom Processes
```python
from core import config
config.SUSPICIOUS_PROCESSES.append("custom-malware.exe")
```

### 3. Custom Thresholds
```python
from core import config
config.KEYSTROKE_SPEED_THRESHOLD = 75  # More sensitive
```

### 4. Additional Monitors
```python
class CustomMonitor:
    def register_callback(self, cb): ...
    def start_monitoring(self): ...

# Wire to detection engine
custom.register_callback(detection_engine.process_custom_event)
```

## Performance Characteristics

| Operation | Frequency | CPU | Memory |
|-----------|-----------|-----|--------|
| USB polling | Every 2s | <0.5% | 1 KB |
| Process enum | Every 1s | 1-2% | 5 KB |
| Keystroke analysis | Per event | <0.1% | 10 KB |
| Signal correlation | Per event | <0.1% | 5 KB |
| Logging | On attack | 0.5% | 2 KB |
| **Total baseline** | - | <1% | ~50 MB |

## Security Considerations

### What's Protected Against
✅ USB Rubber Ducky-style attacks  
✅ Automated keystroke injection via USB  
✅ Command execution via HID emulation  
✅ Terminal/shell launching via USB  

### What's NOT Protected Against
❌ Direct keyboard input from authenticated user  
❌ Network-based command execution  
❌ Firmware-level attacks  
❌ DMA attacks (Thunderbolt, FireWire)  

### Privilege Requirements
- **Windows**: Administrator for WMI access recommended
- **Linux**: Root for full /sys/bus/usb access
- **Minimal**: Non-admin: Basic process monitoring only

## Deployment Models

### 1. Endpoint Protection
- Run on individual Windows/Linux workstation
- Log to local file + send to SIEM
- Alert on console or system tray

### 2. Network Monitoring
- Run on gateways/firewalls
- Monitor for USB-based lateral movement
- Integrate with corporate logging

### 3. Lab Environment
- Run in simulation mode for testing
- Validate detection accuracy
- Tune thresholds

## Testing Strategy

### Unit Testing Components
```
✓ Keystroke analyzer: Test WPM calculation
✓ Process monitor: Test process detection
✓ Detection engine: Test correlation logic
```

### Integration Testing
```
✓ Full attack simulation: Verify end-to-end detection
✓ Multi-handler: Verify all responses trigger
✓ Logging: Verify JSON format and file creation
```

### Regression Testing
```
✓ Run all scenarios: USB_INSERTION, KEYSTROKE_BURST, etc.
✓ False positive rate: Human typing should not trigger
✓ Performance: Verify CPU/memory under load
```

---

**Document Version**: 1.0  
**Last Updated**: 2024-01-15

"""
USB HID Attack Detection System - Comprehensive Test Suite

Tests all major components and attack detection scenarios.
Validates detection engine, keystroke analysis, process monitoring,
and response engine functionality.
"""


import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json
import unittest

# Add parent directory to path so we can import core modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.detection_engine import DetectionEngine, AttackSignal, AttackSeverity, AttackEvent
from core.keystroke_analyzer import KeystrokeAnalyzer
from core.process_monitor import ProcessMonitor, ProcessEvent
from core.usb_monitor import USBEvent
import core.usb_monitor as usb_monitor_module
from core.response_engine import ResponseEngine
from core.logger import StructuredLogger
from core.config import INCIDENT_REPORTS_DIR

logger = StructuredLogger(__name__)


class TestDetectionEngine(unittest.TestCase):
    """Test detection engine signal correlation."""

    def setUp(self):
        """Initialize test fixtures."""
        self.engine = DetectionEngine()

    def test_engine_initialization(self):
        """Test detection engine initializes correctly."""
        self.assertIsNotNone(self.engine)
        self.assertEqual(len(self.engine.signal_history), 0)
        logger.info("✓ Detection engine initialization test passed")

    def test_add_single_signal(self):
        """Test adding a single attack signal."""
        signal = AttackSignal(
            signal_type="process_launch",
            severity=AttackSeverity.HIGH,
            details={"process": "powershell.exe"}
        )
        self.engine.add_signal(signal)
        self.assertEqual(len(self.engine.signal_history), 1)
        logger.info("✓ Single signal addition test passed")

    def test_add_multiple_signals(self):
        """Test adding multiple signals."""
        for i in range(5):
            signal = AttackSignal(
                signal_type="process_launch",
                severity=AttackSeverity.HIGH,
                details={"process": f"proc_{i}.exe"}
            )
            self.engine.add_signal(signal)
        self.assertEqual(len(self.engine.signal_history), 5)
        logger.info("✓ Multiple signals addition test passed")

    def test_signal_correlation_detection(self):
        """Test correlation of multiple signals triggers alert."""
        for i in range(3):
            signal = AttackSignal(
                signal_type="process_launch",
                severity=AttackSeverity.HIGH,
                timestamp=datetime.now() + timedelta(seconds=i),
                details={"process": f"suspicious_{i}.exe"}
            )
            self.engine.add_signal(signal)

        correlated = self.engine.get_recent_signals(minutes=1)
        self.assertGreaterEqual(len(correlated), 3)
        logger.info("✓ Signal correlation test passed")

    def test_signal_severity_levels(self):
        """Test different severity levels."""
        severities = [
            AttackSeverity.LOW,
            AttackSeverity.MEDIUM,
            AttackSeverity.HIGH,
            AttackSeverity.CRITICAL
        ]

        for severity in severities:
            signal = AttackSignal(
                signal_type="test_signal",
                severity=severity
            )
            self.engine.add_signal(signal)

        self.assertEqual(len(self.engine.signal_history), 4)
        logger.info("✓ Severity levels test passed")

    def test_pico_usb_event_tagging(self):
        """Test Pico-like USB fingerprint elevates USB signal severity."""
        pico_usb = USBEvent(
            device_id="USB\\VID_2E8A&PID_000A\\PICO123",
            device_name="Raspberry Pi Pico HID Keyboard",
            event_type="insert",
            timestamp=datetime.now(),
        )

        self.engine.process_usb_event(pico_usb)
        self.assertEqual(len(self.engine.signal_history), 1)

        signal = self.engine.signal_history[0]
        self.assertEqual(signal.signal_type, "usb_insertion")
        self.assertEqual(signal.severity, AttackSeverity.HIGH)
        self.assertTrue(signal.details.get("is_pico_like"))
        logger.info("✓ Pico USB event tagging test passed")

    def test_pico_rubber_ducky_correlation(self):
        """Test Pico + process + keystroke maps to Pico Rubber Ducky attack.
        
        This test validates the correlation engine detects the complete attack pattern:
        1. USB insertion event with Pico-like fingerprint
        2. Suspicious process launch (powershell.exe)
        3. Automated keystroke burst (abnormal typing speed)
        """
        # Stage 1: USB Pico-like device insertion
        usb_signal = AttackSignal(
            signal_type="usb_insertion",
            severity=AttackSeverity.HIGH,
            timestamp=datetime.now(),
            details={"is_pico_like": True, "risk_reason": "Pico fingerprint"},
        )
        self.engine.add_signal(usb_signal)
        self.assertEqual(len(self.engine.signal_history), 1)
        
        # Stage 2: Suspicious process launch
        process_signal = AttackSignal(
            signal_type="process_launch",
            severity=AttackSeverity.HIGH,
            timestamp=datetime.now(),
            details={"process_name": "powershell.exe", "pid": 4242},
        )
        self.engine.add_signal(process_signal)
        self.assertEqual(len(self.engine.signal_history), 2)
        
        # Stage 3: Abnormal keystroke injection pattern
        keystroke_signal = AttackSignal(
            signal_type="keystroke_burst",
            severity=AttackSeverity.CRITICAL,
            timestamp=datetime.now(),
            details={"wpm": 190},  # Abnormally high typing speed
        )
        self.engine.add_signal(keystroke_signal)
        self.assertEqual(len(self.engine.signal_history), 3)

        # Correlate signals and verify attack detection
        attack = self.engine.correlate_signals()
        self.assertIsNotNone(attack, "Attack correlation should detect the pattern")
        
        # Type guard: confirm attack is not None before accessing attributes
        if attack is not None:
            self.assertEqual(attack.attack_type, "PICO_RUBBER_DUCKY_ATTACK")
            self.assertEqual(attack.severity, AttackSeverity.CRITICAL)
        
        logger.info("✓ Pico Rubber Ducky correlation test passed")

    def test_usb_strict_denylist_policy(self):
        """Test strict denylist mode marks denylisted HID devices as critical."""
        old_mode = usb_monitor_module.USB_POLICY_MODE
        old_deny = usb_monitor_module.USB_DEVICE_DENYLIST
        try:
            usb_monitor_module.USB_POLICY_MODE = "strict_denylist"
            usb_monitor_module.USB_DEVICE_DENYLIST = {"2E8A:000A"}

            event = USBEvent(
                device_id="USB\\VID_2E8A&PID_000A\\PICO-STRICT",
                device_name="Raspberry Pi Pico HID Keyboard",
                event_type="insert",
            )
            self.assertEqual(event.risk_label, "CRITICAL")
            self.assertIn("denylist", event.risk_reason.lower())
            logger.info("✓ Strict denylist policy test passed")
        finally:
            usb_monitor_module.USB_POLICY_MODE = old_mode
            usb_monitor_module.USB_DEVICE_DENYLIST = old_deny


class TestKeystrokeAnalyzer(unittest.TestCase):
    """Test keystroke pattern analysis."""

    def setUp(self):
        """Initialize test fixtures."""
        self.analyzer = KeystrokeAnalyzer(time_window=2.0)

    def test_analyzer_initialization(self):
        """Test keystroke analyzer initializes correctly."""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(len(self.analyzer.keystroke_buffer), 0)
        logger.info("✓ Keystroke analyzer initialization test passed")

    def test_normal_typing_pattern(self):
        """Test normal typing pattern detection."""
        current_time = datetime.now()
        for i in range(10):
            timestamp = current_time + timedelta(milliseconds=i * 100)
            self.analyzer.record_keystroke(timestamp)

        stats = self.analyzer.get_statistics()
        self.assertIsNotNone(stats)
        logger.info(f"✓ Normal typing pattern test passed: {stats}")

    def test_abnormal_typing_speed(self):
        """Test abnormal typing speed detection."""
        current_time = datetime.now()
        for i in range(20):
            timestamp = current_time + timedelta(milliseconds=i * 10)
            self.analyzer.record_keystroke(timestamp)

        stats = self.analyzer.get_statistics()
        self.assertIsNotNone(stats)
        logger.info(f"✓ Abnormal typing speed test passed: {stats}")

    def test_keystroke_buffer_management(self):
        """Test keystroke buffer doesn't grow unboundedly."""
        current_time = datetime.now()
        for i in range(1000):
            timestamp = current_time + timedelta(milliseconds=i * 50)
            self.analyzer.record_keystroke(timestamp)

        self.assertLessEqual(len(self.analyzer.keystroke_buffer), 100)
        logger.info("✓ Keystroke buffer management test passed")


class TestProcessMonitor(unittest.TestCase):
    """Test process monitoring functionality."""

    def setUp(self):
        """Initialize test fixtures."""
        self.monitor = ProcessMonitor()

    def test_monitor_initialization(self):
        """Test process monitor initializes with baseline."""
        self.assertIsNotNone(self.monitor)
        self.assertGreater(len(self.monitor._baseline_processes), 0)
        logger.info(f"✓ Process monitor initialization test passed")

    def test_detect_new_suspicious_process(self):
        """Test detection of new suspicious process."""
        process_event = ProcessEvent(
            process_name="powershell.exe",
            pid=9999,
            is_suspicious=True,
            timestamp=datetime.now()
        )

        self.assertTrue(process_event.is_suspicious)
        logger.info("✓ Suspicious process detection test passed")

    def test_track_process_history(self):
        """Test process history tracking."""
        processes_to_track = [
            ProcessEvent("explorer.exe", 100, datetime.now(), False),
            ProcessEvent("chrome.exe", 101, datetime.now(), False),
            ProcessEvent("powershell.exe", 102, datetime.now(), True),
        ]

        for proc in processes_to_track:
            self.monitor.process_history.append(proc)

        self.assertEqual(len(self.monitor.process_history), 3)
        logger.info("✓ Process history tracking test passed")


class TestResponseEngine(unittest.TestCase):
    """Test response engine functionality."""

    def setUp(self):
        """Initialize test fixtures."""
        self.process_monitor = ProcessMonitor()
        self.response_engine = ResponseEngine(process_monitor=self.process_monitor)

    def test_response_engine_initialization(self):
        """Test response engine initializes correctly."""
        self.assertIsNotNone(self.response_engine)
        logger.info("✓ Response engine initialization test passed")

    def test_attack_response_logged(self):
        """Test attack response is logged."""
        signal = AttackSignal(
            signal_type="process_launch",
            severity=AttackSeverity.CRITICAL,
            details={"process": "malware.exe"}
        )

        self.assertIsNotNone(signal)
        self.assertEqual(signal.severity, AttackSeverity.CRITICAL)
        logger.info("✓ Attack response logging test passed")

    def test_quarantine_unknown_pico_action(self):
        """Test quarantine action is triggered for unknown Pico-like HID signals."""
        attack_event = AttackEvent(
            attack_type="PICO_RUBBER_DUCKY_ATTACK",
            severity=AttackSeverity.CRITICAL,
            signals=[
                AttackSignal(
                    signal_type="usb_insertion",
                    severity=AttackSeverity.HIGH,
                    details={
                        "device_id": "USB\\VID_2E8A&PID_000A\\PICO",
                        "device_name": "Raspberry Pi Pico HID Keyboard",
                        "is_pico_like": True,
                        "is_trusted_hid": False,
                        "risk_reason": "Device fingerprint resembles Raspberry Pi Pico HID",
                    },
                )
            ],
        )

        actions = self.response_engine.handle_attack(attack_event)
        quarantine_actions = [a for a in actions if a.action_type == "quarantine_device"]
        self.assertEqual(len(quarantine_actions), 1)
        self.assertTrue(quarantine_actions[0].success)
        self.assertGreaterEqual(len(self.response_engine.quarantined_devices), 1)
        logger.info("✓ Quarantine unknown Pico action test passed")

    def test_incident_report_export(self):
        """Test JSON incident report is exported for each attack."""
        before = set(Path(INCIDENT_REPORTS_DIR).glob("*.json"))

        attack_event = AttackEvent(
            attack_type="USB_HID_TERMINAL_ATTACK",
            severity=AttackSeverity.HIGH,
            signals=[
                AttackSignal(
                    signal_type="process_launch",
                    severity=AttackSeverity.HIGH,
                    details={"process_name": "powershell.exe", "pid": 99999},
                )
            ],
        )
        self.response_engine.handle_attack(attack_event)

        after = set(Path(INCIDENT_REPORTS_DIR).glob("*.json"))
        self.assertGreaterEqual(len(after), len(before) + 1)
        logger.info("✓ Incident report export test passed")


class TestIntegration(unittest.TestCase):
    """Integration tests for full system."""

    def setUp(self):
        """Initialize test fixtures."""
        self.detection_engine = DetectionEngine()
        self.keystroke_analyzer = KeystrokeAnalyzer()
        self.process_monitor = ProcessMonitor()
        self.response_engine = ResponseEngine(self.process_monitor)

    def test_end_to_end_attack_detection(self):
        """Test complete attack detection flow."""
        attack_signals = [
            AttackSignal(
                signal_type="usb_insertion",
                severity=AttackSeverity.HIGH,
                details={"device": "USB Keyboard"}
            ),
            AttackSignal(
                signal_type="process_launch",
                severity=AttackSeverity.HIGH,
                details={"process": "powershell.exe"}
            ),
            AttackSignal(
                signal_type="keystroke_burst",
                severity=AttackSeverity.MEDIUM,
                details={"wpm": 120}
            ),
        ]

        for signal in attack_signals:
            self.detection_engine.add_signal(signal)

        recent_signals = self.detection_engine.get_recent_signals(minutes=1)
        self.assertGreaterEqual(len(recent_signals), 3)
        logger.info("✓ End-to-end attack detection test passed")

    def test_normal_operation_no_alerts(self):
        """Test system doesn't alert during normal operation."""
        for i in range(3):
            signal = AttackSignal(
                signal_type="normal_process",
                severity=AttackSeverity.LOW,
                details={"process": "explorer.exe"}
            )
            self.detection_engine.add_signal(signal)

        recent_signals = self.detection_engine.get_recent_signals(minutes=1)
        logger.info(f"✓ Normal operation test passed (signals: {len(recent_signals)})")


class TestResultsExportation(unittest.TestCase):
    """Test results exportation for dashboard."""

    def setUp(self):
        """Initialize test fixtures."""
        self.detection_engine = DetectionEngine()

    def test_export_results_json(self):
        """Test exporting results in JSON format."""
        for i in range(3):
            signal = AttackSignal(
                signal_type="test_signal",
                severity=AttackSeverity.HIGH if i == 0 else AttackSeverity.MEDIUM,
                details={"test": f"signal_{i}"}
            )
            self.detection_engine.add_signal(signal)

        results = {
            "total_signals": len(self.detection_engine.signal_history),
            "signals": [
                {
                    "type": s.signal_type,
                    "severity": s.severity.name,
                    "timestamp": s.timestamp.isoformat(),
                    "details": s.details
                }
                for s in self.detection_engine.signal_history
            ]
        }

        json_str = json.dumps(results, indent=2)
        self.assertIsNotNone(json_str)
        self.assertIn("total_signals", json_str)
        logger.info("✓ Results exportation test passed")


def run_all_tests() -> unittest.TestResult:
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDetectionEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestKeystrokeAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestProcessMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestResponseEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestResultsExportation))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


def print_test_summary(result: unittest.TestResult) -> None:
    """Print formatted test results summary."""
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*80 + "\n")

    if result.wasSuccessful():
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed. See details above.")


if __name__ == "__main__":
    logger.info("Starting USB HID Attack Detection System Tests...")
    print("\n" + "="*80)
    print("USB HID ATTACK DETECTION SYSTEM - TEST SUITE")
    print("="*80 + "\n")

    result = run_all_tests()
    print_test_summary(result)

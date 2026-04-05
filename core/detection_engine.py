"""
Detection engine that correlates multiple signals to detect attacks.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum

from core.logger import StructuredLogger
from core.usb_monitor import USBEvent
from core.keystroke_analyzer import KeystrokePattern
from core.process_monitor import ProcessEvent
from core.config import CORRELATION_TIME_WINDOW

logger = StructuredLogger(__name__)


class AttackSeverity(Enum):
    """Attack severity levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class AttackSignal:
    """Represents a single attack signal."""

    def __init__(
        self,
        signal_type: str,  # "usb_insertion", "keystroke_burst", "process_launch"
        severity: AttackSeverity,
        timestamp: datetime = None,
        details: Dict[str, Any] = None,
    ):
        """
        Initialize attack signal.

        Args:
            signal_type: Type of signal
            severity: Severity level
            timestamp: When signal was detected
            details: Additional signal details
        """
        self.signal_type = signal_type
        self.severity = severity
        self.timestamp = timestamp or datetime.now()
        self.details = details or {}

    def __repr__(self) -> str:
        return (
            f"AttackSignal(type={self.signal_type}, severity={self.severity.name}, "
            f"ts={self.timestamp})"
        )


class AttackEvent:
    """Represents a detected attack."""

    def __init__(
        self,
        attack_type: str,
        severity: AttackSeverity,
        signals: List[AttackSignal],
        timestamp: datetime = None,
    ):
        """
        Initialize attack event.

        Args:
            attack_type: Type of attack detected
            severity: Attack severity level
            signals: List of correlated signals
            timestamp: When attack was detected
        """
        self.attack_type = attack_type
        self.severity = severity
        self.signals = signals
        self.timestamp = timestamp or datetime.now()
        self.id = f"attack_{self.timestamp.timestamp()}_{id(self)}"

    def __repr__(self) -> str:
        return (
            f"AttackEvent(type={self.attack_type}, severity={self.severity.name}, "
            f"signals={len(self.signals)}, ts={self.timestamp})"
        )


class DetectionEngine:
    """Correlates multiple signals to detect USB HID attacks."""

    def __init__(self, correlation_window: float = CORRELATION_TIME_WINDOW):
        """
        Initialize detection engine.

        Args:
            correlation_window: Time window (seconds) for signal correlation
        """
        self.correlation_window = correlation_window
        self.signal_history: List[AttackSignal] = []
        self.attack_history: List[AttackEvent] = []
        logger.info(
            f"Detection engine initialized (correlation window: {correlation_window}s)"
        )

    def add_signal(self, signal: AttackSignal) -> None:
        """
        Add a signal to be correlated.

        Args:
            signal: AttackSignal to add
        """
        self.signal_history.append(signal)
        logger.info(f"Signal added: {signal}")

    def process_usb_event(self, usb_event: USBEvent) -> None:
        """
        Process a USB device event.

        Args:
            usb_event: The USB event to process
        """
        if usb_event.event_type == "insert":
            usb_severity = AttackSeverity.MEDIUM
            if getattr(usb_event, "is_pico_like", False):
                usb_severity = AttackSeverity.HIGH

            signal = AttackSignal(
                signal_type="usb_insertion",
                severity=usb_severity,
                timestamp=usb_event.timestamp,
                details={
                    "device_id": usb_event.device_id,
                    "device_name": usb_event.device_name,
                    "vendor_id": getattr(usb_event, "vendor_id", None),
                    "product_id": getattr(usb_event, "product_id", None),
                    "is_pico_like": getattr(usb_event, "is_pico_like", False),
                    "is_trusted_hid": getattr(usb_event, "is_trusted_hid", False),
                    "device_risk": getattr(usb_event, "risk_label", "UNKNOWN"),
                    "risk_reason": getattr(usb_event, "risk_reason", "N/A"),
                },
            )
            self.add_signal(signal)

    def process_keystroke_pattern(self, pattern: KeystrokePattern) -> None:
        """
        Process a detected keystroke pattern.

        Args:
            pattern: The keystroke pattern to process
        """
        severity_map = {
            "normal": AttackSeverity.LOW,
            "burst": AttackSeverity.MEDIUM,
            "automated": AttackSeverity.CRITICAL,
        }

        signal = AttackSignal(
            signal_type="keystroke_burst",
            severity=severity_map.get(pattern.pattern_type, AttackSeverity.LOW),
            timestamp=pattern.timestamp,
            details={
                "pattern_type": pattern.pattern_type,
                "wpm": round(pattern.wpm, 2),
                "keystroke_count": pattern.keystroke_count,
            },
        )
        self.add_signal(signal)

    def process_process_event(
        self, process_event: ProcessEvent, is_after_usb: bool = False
    ) -> None:
        """
        Process a process launch event.

        Args:
            process_event: The process event to process
            is_after_usb: Whether this process launched shortly after USB insertion
        """
        if process_event.is_suspicious:
            severity = AttackSeverity.HIGH if is_after_usb else AttackSeverity.MEDIUM

            signal = AttackSignal(
                signal_type="process_launch",
                severity=severity,
                timestamp=process_event.timestamp,
                details={
                    "process_name": process_event.process_name,
                    "pid": process_event.pid,
                    "after_usb": is_after_usb,
                },
            )
            self.add_signal(signal)

    def correlate_signals(self) -> Optional[AttackEvent]:
        """
        Correlate recent signals to detect attacks.

        Returns:
            AttackEvent if an attack is detected, None otherwise
        """
        now = datetime.now()
        # Only correlate very recent signals to reduce stale/false correlations.
        window_start = now - timedelta(seconds=self.correlation_window)

        # Get signals within correlation window
        recent_signals = [
            s for s in self.signal_history if s.timestamp >= window_start
        ]

        if len(recent_signals) < 2:
            return None

        # Check for common attack patterns
        has_usb = any(s.signal_type == "usb_insertion" for s in recent_signals)
        has_process = any(
            s.signal_type == "process_launch" for s in recent_signals
        )
        has_keystroke = any(
            s.signal_type == "keystroke_burst" for s in recent_signals
        )
        has_pico_like_usb = any(
            s.signal_type == "usb_insertion"
            and s.details.get("is_pico_like", False)
            for s in recent_signals
        )

        # Default to no attack; patterns below can elevate type/severity.
        attack_detected = False
        attack_type = ""
        attack_severity = AttackSeverity.LOW

        # Pattern 1: USB insertion immediately followed by terminal launch
        if has_usb and has_process:
            attack_detected = True
            attack_type = "USB_HID_TERMINAL_ATTACK"
            attack_severity = AttackSeverity.HIGH
            logger.critical(
                "ATTACK PATTERN DETECTED: USB device + suspicious process",
                event_data={
                    "pattern": "usb_terminal",
                    "signal_count": len(recent_signals),
                },
            )

        # Pattern 1b: Pico-like HID insertion with fast process launch is treated
        # as very high confidence for Rubber Ducky style behavior.
        if has_pico_like_usb and has_process:
            attack_detected = True
            attack_type = "PICO_HID_TERMINAL_ATTACK"
            attack_severity = AttackSeverity.CRITICAL
            logger.critical(
                "CRITICAL ATTACK PATTERN: Pico-like HID + suspicious process",
                event_data={
                    "pattern": "pico_hid_terminal",
                    "signal_count": len(recent_signals),
                },
            )

        # Pattern 2: Abnormal keystroke patterns
        if has_keystroke:
            keystroke_signal = next(
                s for s in recent_signals if s.signal_type == "keystroke_burst"
            )
            if keystroke_signal.severity == AttackSeverity.CRITICAL:
                attack_detected = True
                attack_type = "AUTOMATED_KEYSTROKE_INJECTION"
                attack_severity = AttackSeverity.CRITICAL
                logger.critical(
                    "ATTACK PATTERN DETECTED: Automated keystroke injection",
                    event_data=keystroke_signal.details,
                )

        # Pattern 3 is the strongest signal combination and intentionally overrides
        # previous pattern assignments when all three signal types are present.
        if has_usb and has_keystroke and has_process:
            attack_detected = True
            attack_type = "MULTI_SIGNAL_USB_HID_ATTACK"
            attack_severity = AttackSeverity.CRITICAL
            logger.critical(
                "CRITICAL ATTACK PATTERN: Multi-signal USB HID attack",
                event_data={
                    "signals": [str(s) for s in recent_signals],
                },
            )

        # Pattern 4: Pico-like USB + keystroke burst + process launch is a topic-
        # specific signature for Raspberry Pi Pico Rubber Ducky workflows.
        if has_pico_like_usb and has_keystroke and has_process:
            attack_detected = True
            attack_type = "PICO_RUBBER_DUCKY_ATTACK"
            attack_severity = AttackSeverity.CRITICAL
            logger.critical(
                "CRITICAL ATTACK PATTERN: Pico Rubber Ducky signature detected",
                event_data={
                    "pattern": "pico_rubber_ducky",
                    "signal_count": len(recent_signals),
                },
            )

        if attack_detected:
            attack_event = AttackEvent(
                attack_type=attack_type,
                severity=attack_severity,
                signals=recent_signals,
                timestamp=now,
            )
            self.attack_history.append(attack_event)
            return attack_event

        return None

    def get_recent_signals(
        self, minutes: int = 5
    ) -> List[AttackSignal]:
        """
        Get signals from the last N minutes.

        Args:
            minutes: Number of minutes to look back

        Returns:
            List of recent signals
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            s for s in self.signal_history
            if s.timestamp >= cutoff_time
        ]

    def get_recent_attacks(
        self, minutes: int = 10
    ) -> List[AttackEvent]:
        """
        Get detected attacks from the last N minutes.

        Args:
            minutes: Number of minutes to look back

        Returns:
            List of recent attacks
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            a for a in self.attack_history
            if a.timestamp >= cutoff_time
        ]

    def get_statistics(self) -> dict:
        """
        Get detection engine statistics.

        Returns:
            Dictionary with statistics
        """
        recent_attacks = self.get_recent_attacks()
        recent_signals = self.get_recent_signals()

        critical_attacks = [
            a for a in recent_attacks
            if a.severity == AttackSeverity.CRITICAL
        ]

        return {
            "total_signals_history": len(self.signal_history),
            "recent_signals": len(recent_signals),
            "total_attacks_detected": len(self.attack_history),
            "recent_attacks": len(recent_attacks),
            "critical_attacks": len(critical_attacks),
        }

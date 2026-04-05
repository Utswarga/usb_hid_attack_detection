"""
Response engine that takes action when attacks are detected.
"""

from typing import Callable, List
from datetime import datetime
import json
from pathlib import Path

from core.logger import StructuredLogger
from core.detection_engine import AttackEvent, AttackSeverity
from core.process_monitor import ProcessMonitor
from core.config import RESPONSE_ACTIONS, INCIDENT_REPORTS_DIR

logger = StructuredLogger(__name__)


class ResponseAction:
    """Represents a response action taken."""

    def __init__(
        self,
        action_type: str,
        attack_event: AttackEvent,
        success: bool,
        details: str = "",
    ):
        """
        Initialize response action.

        Args:
            action_type: Type of action taken
            attack_event: The attack that triggered the response
            success: Whether the action was successful
            details: Additional details about the action
        """
        self.action_type = action_type
        self.attack_event = attack_event
        self.success = success
        self.details = details
        self.timestamp = datetime.now()

    def __repr__(self) -> str:
        return (
            f"ResponseAction(type={self.action_type}, success={self.success}, "
            f"attack={self.attack_event.attack_type})"
        )

    def to_dict(self) -> dict:
        """Serialize action for incident report export."""
        return {
            "action_type": self.action_type,
            "success": self.success,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


class ResponseEngine:
    """Handles response actions to detected attacks."""

    def __init__(self, process_monitor: ProcessMonitor = None):
        """
        Initialize response engine.

        Args:
            process_monitor: ProcessMonitor instance for process termination
        """
        self.process_monitor = process_monitor
        self.response_history: List[ResponseAction] = []
        self.custom_handlers: List[Callable[[AttackEvent], None]] = []
        self.quarantined_devices: dict[str, dict] = {}
        logger.info("Response engine initialized")

    def register_custom_handler(
        self, handler: Callable[[AttackEvent], None]
    ) -> None:
        """
        Register a custom response handler.

        Args:
            handler: Function that accepts an AttackEvent
        """
        self.custom_handlers.append(handler)
        logger.info(f"Registered custom response handler: {handler.__name__}")

    def handle_attack(self, attack_event: AttackEvent) -> List[ResponseAction]:
        """
        Handle a detected attack with appropriate responses.

        Args:
            attack_event: The attack event to respond to

        Returns:
            List of actions taken
        """
        actions: List[ResponseAction] = []
        logger.critical(
            f"ATTACK RESPONSE INITIATED: {attack_event.attack_type}",
            event_data={
                "attack_type": attack_event.attack_type,
                "severity": attack_event.severity.name,
                "signal_count": len(attack_event.signals),
            },
        )

        # Always log
        if RESPONSE_ACTIONS.get("log", True):
            action = self._log_attack(attack_event)
            actions.append(action)

        # Alert on console
        if RESPONSE_ACTIONS.get("alert", True):
            action = self._alert_console(attack_event)
            actions.append(action)

        # Kill process for critical attacks if enabled
        if (
            RESPONSE_ACTIONS.get("kill_process", False)
            and attack_event.severity == AttackSeverity.CRITICAL
        ):
            action = self._kill_suspicious_processes(attack_event)
            actions.append(action)

        # Quarantine unknown Pico-like HID activity regardless of generic
        # kill_process mode. This is a topic-specific defensive action.
        if (
            RESPONSE_ACTIONS.get("quarantine_unknown_pico", True)
            and self._is_unknown_pico_attack(attack_event)
        ):
            action = self._quarantine_unknown_pico_device(attack_event)
            actions.append(action)

        # Call custom handlers
        for handler in self.custom_handlers:
            try:
                handler(attack_event)
            except Exception as e:
                logger.error(
                    f"Error in custom response handler {handler.__name__}: {e}",
                    event_data={"handler": handler.__name__, "error": str(e)},
                )

        # Record all actions
        for action in actions:
            self.response_history.append(action)

        if RESPONSE_ACTIONS.get("export_incident_report", True):
            self._export_incident_report(attack_event, actions)

        return actions

    def _is_unknown_pico_attack(self, attack_event: AttackEvent) -> bool:
        """Check if correlated signals indicate unknown Pico-like HID behavior."""
        for signal in attack_event.signals:
            if signal.signal_type != "usb_insertion":
                continue
            if signal.details.get("is_pico_like", False) and not signal.details.get("is_trusted_hid", False):
                return True
        return False

    def _quarantine_unknown_pico_device(self, attack_event: AttackEvent) -> ResponseAction:
        """Quarantine unknown Pico-like HID devices and related process signals."""
        pico_devices = []
        for signal in attack_event.signals:
            if signal.signal_type != "usb_insertion":
                continue
            if not signal.details.get("is_pico_like", False):
                continue

            device_id = signal.details.get("device_id") or "unknown_device"
            record = {
                "device_name": signal.details.get("device_name", "Unknown"),
                "vendor_id": signal.details.get("vendor_id"),
                "product_id": signal.details.get("product_id"),
                "risk_reason": signal.details.get("risk_reason", "Unknown Pico-like fingerprint"),
                "quarantined_at": datetime.now().isoformat(),
                "attack_id": attack_event.id,
            }
            self.quarantined_devices[device_id] = record
            pico_devices.append({"device_id": device_id, **record})

        # Best-effort process containment for suspicious process signals.
        terminated = 0
        if self.process_monitor:
            for signal in attack_event.signals:
                if signal.signal_type != "process_launch":
                    continue
                pid = signal.details.get("pid")
                if not pid:
                    continue
                if self.process_monitor.terminate_process(pid, force=True):
                    terminated += 1

        details = (
            f"Quarantined {len(pico_devices)} Pico-like device(s); "
            f"terminated {terminated} related process(es)."
        )
        logger.critical(
            "QUARANTINE ACTION EXECUTED",
            event_data={
                "attack_id": attack_event.id,
                "quarantined_devices": pico_devices,
                "terminated_processes": terminated,
            },
        )
        return ResponseAction(
            action_type="quarantine_device",
            attack_event=attack_event,
            success=True,
            details=details,
        )

    def _export_incident_report(
        self, attack_event: AttackEvent, actions: List[ResponseAction]
    ) -> None:
        """Write a JSON incident report file for each detected attack."""
        try:
            safe_attack_id = attack_event.id.replace(".", "_")
            report_path = Path(INCIDENT_REPORTS_DIR) / f"{safe_attack_id}.json"
            report = {
                "attack": {
                    "id": attack_event.id,
                    "type": attack_event.attack_type,
                    "severity": attack_event.severity.name,
                    "timestamp": attack_event.timestamp.isoformat(),
                },
                "signals": [
                    {
                        "type": s.signal_type,
                        "severity": s.severity.name,
                        "timestamp": s.timestamp.isoformat(),
                        "details": s.details,
                    }
                    for s in attack_event.signals
                ],
                "actions": [a.to_dict() for a in actions],
                "quarantine_state": self.quarantined_devices,
            }
            report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
            logger.info(
                f"Incident report exported: {report_path.name}",
                event_data={"attack_id": attack_event.id, "path": str(report_path)},
            )
        except Exception as e:
            logger.error(
                f"Failed to export incident report: {e}",
                event_data={"attack_id": attack_event.id, "error": str(e)},
            )

    def _log_attack(self, attack_event: AttackEvent) -> ResponseAction:
        """
        Log attack details to file.

        Args:
            attack_event: The attack event

        Returns:
            ResponseAction instance
        """
        try:
            logger.critical(
                f"ATTACK LOGGED: {attack_event.attack_type}",
                event_data={
                    "attack_id": attack_event.id,
                    "attack_type": attack_event.attack_type,
                    "severity": attack_event.severity.name,
                    "signal_count": len(attack_event.signals),
                    "signals": [
                        {
                            "type": s.signal_type,
                            "severity": s.severity.name,
                            "details": s.details,
                        }
                        for s in attack_event.signals
                    ],
                },
            )
            return ResponseAction(
                action_type="log",
                attack_event=attack_event,
                success=True,
                details="Attack logged to file",
            )
        except Exception as e:
            logger.error(f"Failed to log attack: {e}")
            return ResponseAction(
                action_type="log",
                attack_event=attack_event,
                success=False,
                details=f"Logging failed: {str(e)}",
            )

    def _alert_console(self, attack_event: AttackEvent) -> ResponseAction:
        """
        Print alert to console.

        Args:
            attack_event: The attack event

        Returns:
            ResponseAction instance
        """
        try:
            alert_message = self._format_alert(attack_event)
            print("\n" + "=" * 80)
            print(alert_message)
            print("=" * 80 + "\n")
            logger.critical(alert_message)
            return ResponseAction(
                action_type="console_alert",
                attack_event=attack_event,
                success=True,
                details="Alert printed to console",
            )
        except Exception as e:
            logger.error(f"Failed to print alert: {e}")
            return ResponseAction(
                action_type="console_alert",
                attack_event=attack_event,
                success=False,
                details=f"Alert failed: {str(e)}",
            )

    def _format_alert(self, attack_event: AttackEvent) -> str:
        """
        Format attack alert message.

        Args:
            attack_event: The attack event

        Returns:
            Formatted alert string
        """
        lines = [
            "🚨 USB HID ATTACK DETECTED 🚨",
            f"Attack Type: {attack_event.attack_type}",
            f"Severity: {attack_event.severity.name}",
            f"Time: {attack_event.timestamp.isoformat()}",
            f"Attack ID: {attack_event.id}",
            f"\nCorrelated Signals ({len(attack_event.signals)}):",
        ]

        for i, signal in enumerate(attack_event.signals, 1):
            lines.append(f"\n  Signal {i}:")
            lines.append(f"    Type: {signal.signal_type}")
            lines.append(f"    Severity: {signal.severity.name}")
            lines.append(f"    Time: {signal.timestamp.isoformat()}")
            if signal.details:
                lines.append(f"    Details: {signal.details}")

        lines.extend([
            "\n⚠️  IMMEDIATE ACTION REQUIRED",
            "Check system logs for detailed information.",
        ])

        return "\n".join(lines)

    def _kill_suspicious_processes(
        self, attack_event: AttackEvent
    ) -> ResponseAction:
        """
        Terminate suspicious processes related to the attack.

        Args:
            attack_event: The attack event

        Returns:
            ResponseAction instance
        """
        if not self.process_monitor:
            return ResponseAction(
                action_type="kill_process",
                attack_event=attack_event,
                success=False,
                details="No process monitor available",
            )

        killed_processes = []
        failed_processes = []

        for signal in attack_event.signals:
            if signal.signal_type == "process_launch" and "pid" in signal.details:
                pid = signal.details["pid"]
                process_name = signal.details.get("process_name", "unknown")

                if self.process_monitor.terminate_process(pid, force=True):
                    killed_processes.append(f"{process_name} ({pid})")
                else:
                    failed_processes.append(f"{process_name} ({pid})")

        success = len(failed_processes) == 0
        details = (
            f"Killed: {len(killed_processes)}, "
            f"Failed: {len(failed_processes)}"
        )

        if success:
            logger.warning(
                f"Suspended {len(killed_processes)} suspicious processes",
                event_data={
                    "processes": killed_processes,
                },
            )
        else:
            logger.error(
                f"Partial process termination: {details}",
                event_data={
                    "killed": killed_processes,
                    "failed": failed_processes,
                },
            )

        return ResponseAction(
            action_type="kill_process",
            attack_event=attack_event,
            success=success,
            details=details,
        )

    def get_response_history(self) -> List[ResponseAction]:
        """
        Get all response actions taken.

        Returns:
            List of response actions
        """
        return self.response_history.copy()

    def get_statistics(self) -> dict:
        """
        Get response engine statistics.

        Returns:
            Dictionary with statistics
        """
        successful_responses = [
            a for a in self.response_history if a.success
        ]
        failed_responses = [
            a for a in self.response_history if not a.success
        ]

        return {
            "total_responses": len(self.response_history),
            "successful_responses": len(successful_responses),
            "failed_responses": len(failed_responses),
            "custom_handlers_registered": len(self.custom_handlers),
        }

"""
USB device monitoring module for detecting new HID keyboard connections.
"""

import threading
import time
import importlib
import re
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Callable, Optional

from core.logger import StructuredLogger
from core.config import (
    USB_HID_KEYWORDS,
    PLATFORM,
    PICO_VENDOR_IDS,
    PICO_PRODUCT_IDS,
    PICO_NAME_KEYWORDS,
    TRUSTED_HID_NAME_KEYWORDS,
    USB_POLICY_MODE,
    USB_DEVICE_ALLOWLIST,
    USB_DEVICE_DENYLIST,
)

logger = StructuredLogger(__name__)


class USBEvent:
    """Represents a USB device event."""

    def __init__(
        self,
        device_id: str,
        device_name: str,
        event_type: str,  # "insert" or "remove"
        timestamp: datetime = None,
    ):
        """
        Initialize USB event.

        Args:
            device_id: Unique device identifier
            device_name: Human-readable device name
            event_type: Type of event ("insert" or "remove")
            timestamp: Event timestamp (defaults to current time)
        """
        self.device_id = device_id
        self.device_name = device_name
        self.event_type = event_type
        self.timestamp = timestamp or datetime.now()
        self.vendor_id, self.product_id = self._extract_vid_pid()
        self.is_hid = self._check_if_hid()
        self.is_pico_like = self._check_if_pico_like()
        self.is_trusted_hid = self._check_if_trusted_hid()
        self.risk_label, self.risk_reason = self._assess_risk()

    def _extract_vid_pid(self) -> tuple[Optional[str], Optional[str]]:
        """Extract USB VID/PID from device identifier strings when present."""
        if not self.device_id:
            return None, None

        value = self.device_id.upper()
        vid_match = re.search(r"VID[_:=]([0-9A-F]{4})", value)
        pid_match = re.search(r"PID[_:=]([0-9A-F]{4})", value)

        vid = vid_match.group(1) if vid_match else None
        pid = pid_match.group(1) if pid_match else None
        return vid, pid

    def _check_if_hid(self) -> bool:
        """Check if device appears to be HID keyboard."""
        device_lower = self.device_name.lower()
        return any(keyword in device_lower for keyword in USB_HID_KEYWORDS)

    def _check_if_pico_like(self) -> bool:
        """Identify Pico-like boards by USB IDs or common product name markers."""
        if self.vendor_id in PICO_VENDOR_IDS:
            return True
        if self.product_id in PICO_PRODUCT_IDS:
            return True

        name_lower = self.device_name.lower()
        return any(keyword in name_lower for keyword in PICO_NAME_KEYWORDS)

    def _check_if_trusted_hid(self) -> bool:
        """Check if device matches known trusted HID brands/models."""
        name_lower = self.device_name.lower()
        return any(keyword in name_lower for keyword in TRUSTED_HID_NAME_KEYWORDS)

    def _device_fingerprint(self) -> str:
        """Create normalized fingerprint string for list-based policy checks."""
        if self.vendor_id and self.product_id:
            return f"{self.vendor_id}:{self.product_id}"
        return self.device_name.lower()

    def _matches_rule_set(self, rules: set[str]) -> bool:
        """Check if device matches any fingerprint or name keyword in rules."""
        if not rules:
            return False

        fingerprint = self._device_fingerprint()
        name_lower = self.device_name.lower()
        for rule in rules:
            normalized = rule.upper() if ":" in rule else rule.lower()
            if ":" in rule and fingerprint.upper() == normalized:
                return True
            if ":" not in rule and normalized in name_lower:
                return True
        return False

    def _assess_risk(self) -> tuple[str, str]:
        """Classify device risk for downstream correlation and alert messaging."""
        if not self.is_hid:
            return "LOW", "Non-HID USB device"

        if USB_POLICY_MODE == "strict_denylist" and self._matches_rule_set(USB_DEVICE_DENYLIST):
            return "CRITICAL", "USB strict denylist match"

        if USB_POLICY_MODE == "strict_allowlist" and not self._matches_rule_set(USB_DEVICE_ALLOWLIST):
            return "CRITICAL", "USB strict allowlist violation"

        if self.is_pico_like:
            return "HIGH", "Device fingerprint resembles Raspberry Pi Pico HID"

        if self.is_trusted_hid:
            return "LOW", "Trusted HID keyboard fingerprint"

        return "MEDIUM", "Unrecognized HID keyboard device"

    def __repr__(self) -> str:
        return (
            f"USBEvent(id={self.device_id}, name={self.device_name}, "
            f"type={self.event_type}, hid={self.is_hid}, pico={self.is_pico_like}, "
            f"risk={self.risk_label}, ts={self.timestamp})"
        )


class USBMonitorBase(ABC):
    """Abstract base class for USB monitoring implementations."""

    def __init__(self):
        """Initialize USB monitor."""
        self.callbacks: List[Callable[[USBEvent], None]] = []
        self.is_running = False

    @abstractmethod
    def start_monitoring(self) -> None:
        """Start monitoring for USB events."""
        pass

    @abstractmethod
    def stop_monitoring(self) -> None:
        """Stop monitoring for USB events."""
        pass

    def register_callback(self, callback: Callable[[USBEvent], None]) -> None:
        """
        Register a callback function to handle USB events.

        Args:
            callback: Function that accepts USBEvent
        """
        self.callbacks.append(callback)
        logger.info(f"Registered USB event callback: {callback.__name__}")

    def _trigger_callbacks(self, event: USBEvent) -> None:
        """Trigger all registered callbacks with the event."""
        for callback in self.callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(
                    f"Error in USB event callback {callback.__name__}: {e}",
                    event_data={"device_id": event.device_id, "error": str(e)},
                )


class WindowsUSBMonitor(USBMonitorBase):
    """Windows implementation of USB monitoring using WMI."""

    def __init__(self):
        """Initialize Windows USB monitor."""
        super().__init__()
        self.monitor_thread: Optional[threading.Thread] = None
        self._last_devices = set()

        try:
            self.wmi = importlib.import_module("wmi")
            self.has_wmi = True
            logger.info("WMI available for USB monitoring")
        except ImportError:
            self.has_wmi = False
            logger.warning(
                "WMI not available - USB monitoring will use fallback method"
            )

    def start_monitoring(self) -> None:
        """Start monitoring USB devices."""
        if self.is_running:
            logger.warning("USB monitor already running")
            return

        self.is_running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, daemon=True
        )
        self.monitor_thread.start()
        logger.info("USB monitor started")

    def stop_monitoring(self) -> None:
        """Stop monitoring USB devices."""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logger.info("USB monitor stopped")

    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.is_running:
            try:
                self._check_devices()
                time.sleep(2)  # Check every 2 seconds
            except Exception as e:
                logger.error(f"Error in USB monitoring loop: {e}")
                time.sleep(5)  # Wait longer on error

    def _check_devices(self) -> None:
        """Check for new or removed USB devices."""
        current_devices = self._get_device_list()
        current_ids = {dev["id"] for dev in current_devices}
        last_ids = {dev["id"] for dev in self._last_devices} if self._last_devices else set()

        # Check for new devices (insertions)
        new_devices = current_ids - last_ids
        for device in current_devices:
            if device["id"] in new_devices:
                event = USBEvent(
                    device_id=device["id"],
                    device_name=device["name"],
                    event_type="insert",
                )
                if event.is_hid:
                    logger.info(
                        f"USB HID device detected: {device['name']}",
                        event_data={"device_id": device["id"]},
                    )
                    self._trigger_callbacks(event)

        # Check for removed devices
        removed_devices = last_ids - current_ids
        for device in self._last_devices or []:
            if device["id"] in removed_devices:
                event = USBEvent(
                    device_id=device["id"],
                    device_name=device["name"],
                    event_type="remove",
                )
                if event.is_hid:
                    logger.info(
                        f"USB HID device removed: {device['name']}",
                        event_data={"device_id": device["id"]},
                    )
                    self._trigger_callbacks(event)

        self._last_devices = current_devices

    def _get_device_list(self) -> List[dict]:
        """Get list of currently connected USB devices."""
        devices = []

        if self.has_wmi:
            try:
                c = self.wmi.WMI()
                # Query for USB devices
                for device in c.Win32_PnPEntity():
                    if device.PNPClass in ["Keyboard", "HIDClass", "USB"]:
                        devices.append(
                            {
                                "id": device.PNPDeviceID or device.Name or "unknown",
                                "name": device.Name or device.Description or "Unknown Device",
                            }
                        )
            except Exception as e:
                logger.warning(f"WMI query failed: {e}")
                return devices or self._get_device_list_fallback()
        else:
            devices = self._get_device_list_fallback()

        return devices

    def _get_device_list_fallback(self) -> List[dict]:
        """Fallback method to get device list using psutil."""
        try:
            import psutil

            devices = []
            # This is a basic fallback - won't capture actual USB HID devices
            # but provides a baseline
            for partition in psutil.disk_partitions():
                devices.append(
                    {
                        "id": partition.device,
                        "name": partition.device,
                    }
                )
            return devices
        except Exception as e:
            logger.warning(f"Fallback device detection failed: {e}")
            return []


class LinuxUSBMonitor(USBMonitorBase):
    """Linux implementation of USB monitoring using /sys/bus/usb."""

    def __init__(self):
        """Initialize Linux USB monitor."""
        super().__init__()
        self.monitor_thread: Optional[threading.Thread] = None
        self._last_devices = set()

    def start_monitoring(self) -> None:
        """Start monitoring USB devices."""
        if self.is_running:
            logger.warning("USB monitor already running")
            return

        self.is_running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, daemon=True
        )
        self.monitor_thread.start()
        logger.info("USB monitor started (Linux mode)")

    def stop_monitoring(self) -> None:
        """Stop monitoring USB devices."""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logger.info("USB monitor stopped")

    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.is_running:
            try:
                self._check_devices()
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error in USB monitoring loop: {e}")
                time.sleep(5)

    def _check_devices(self) -> None:
        """Check for new or removed USB devices via /sys/bus/usb."""
        import os
        
        current_devices = []
        usb_devices_path = "/sys/bus/usb/devices"

        if not os.path.exists(usb_devices_path):
            return

        for device_dir in os.listdir(usb_devices_path):
            device_path = os.path.join(usb_devices_path, device_dir)
            try:
                # Read device name
                name_file = os.path.join(device_path, "product")
                if os.path.exists(name_file):
                    with open(name_file, "r") as f:
                        device_name = f.read().strip()
                else:
                    device_name = device_dir

                current_devices.append({"id": device_dir, "name": device_name})
            except Exception as e:
                logger.warning(f"Failed to read device {device_dir}: {e}")

        current_ids = {dev["id"] for dev in current_devices}
        last_ids = {dev["id"] for dev in self._last_devices} if self._last_devices else set()

        # New devices
        for device in current_devices:
            if device["id"] in (current_ids - last_ids):
                event = USBEvent(
                    device_id=device["id"],
                    device_name=device["name"],
                    event_type="insert",
                )
                if event.is_hid:
                    logger.info(
                        f"USB HID device detected: {device['name']}",
                        event_data={"device_id": device["id"]},
                    )
                    self._trigger_callbacks(event)

        # Removed devices
        for device in self._last_devices or []:
            if device["id"] in (last_ids - current_ids):
                event = USBEvent(
                    device_id=device["id"],
                    device_name=device["name"],
                    event_type="remove",
                )
                if event.is_hid:
                    logger.info(
                        f"USB HID device removed: {device['name']}",
                        event_data={"device_id": device["id"]},
                    )
                    self._trigger_callbacks(event)

        self._last_devices = current_devices


def create_usb_monitor() -> USBMonitorBase:
    """
    Factory function to create appropriate USB monitor for the platform.

    Returns:
        USBMonitorBase: Platform-specific USB monitor instance
    """
    if PLATFORM == "windows":
        return WindowsUSBMonitor()
    else:
        return LinuxUSBMonitor()

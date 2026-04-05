"""
USB HID Attack Detection System - Core module.
"""

from core.config import *
from core.logger import StructuredLogger, logger
from core.usb_monitor import create_usb_monitor, USBEvent, USBMonitorBase
from core.keystroke_analyzer import KeystrokeAnalyzer, KeystrokePattern
from core.process_monitor import ProcessMonitor, ProcessEvent
from core.detection_engine import DetectionEngine, AttackEvent, AttackSeverity
from core.response_engine import ResponseEngine, ResponseAction
from core.simulation import AttackSimulator, SimulationScenario, SimulationConfigs

__all__ = [
    "logger",
    "StructuredLogger",
    "create_usb_monitor",
    "USBEvent",
    "KeystrokeAnalyzer",
    "KeystrokePattern",
    "ProcessMonitor",
    "ProcessEvent",
    "DetectionEngine",
    "AttackEvent",
    "AttackSeverity",
    "ResponseEngine",
    "ResponseAction",
    "AttackSimulator",
    "SimulationScenario",
    "SimulationConfigs",
]

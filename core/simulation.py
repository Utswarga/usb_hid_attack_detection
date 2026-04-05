"""
Simulation module for testing attack detection without actual USB/HID devices.
"""

import threading
import time
from datetime import datetime, timedelta
from random import randint, choice

from core.logger import StructuredLogger
from core.usb_monitor import USBEvent
from core.keystroke_analyzer import KeystrokeEvent
from core.process_monitor import ProcessEvent
from core.detection_engine import DetectionEngine

logger = StructuredLogger(__name__)


class SimulationScenario:
    """Represents a simulated attack scenario."""

    def __init__(
        self,
        name: str,
        description: str,
        duration_seconds: int = 10,
        attack_type: str = "USB_HID_TERMINAL_ATTACK",
    ):
        """
        Initialize simulation scenario.

        Args:
            name: Scenario name
            description: Scenario description
            duration_seconds: How long the scenario runs
            attack_type: Type of attack to simulate
        """
        self.name = name
        self.description = description
        self.duration_seconds = duration_seconds
        self.attack_type = attack_type
        self.events = []

    def __repr__(self) -> str:
        return f"SimulationScenario(name={self.name}, type={self.attack_type})"


class AttackSimulator:
    """Simulates USB HID attack scenarios for testing."""

    # Predefined scenarios
    SCENARIO_USB_INSERTION = SimulationScenario(
        name="USB_INSERTION",
        description="Simulate a USB keyboard insertion",
        duration_seconds=3,
        attack_type="USB_HID_TERMINAL_ATTACK",
    )

    SCENARIO_KEYSTROKE_BURST = SimulationScenario(
        name="KEYSTROKE_BURST",
        description="Simulate abnormally fast keystroke patterns",
        duration_seconds=8,
        attack_type="AUTOMATED_KEYSTROKE_INJECTION",
    )

    SCENARIO_TERMINAL_LAUNCH = SimulationScenario(
        name="TERMINAL_LAUNCH",
        description="Simulate terminal launch after USB insertion",
        duration_seconds=5,
        attack_type="USB_HID_TERMINAL_ATTACK",
    )

    SCENARIO_FULL_ATTACK = SimulationScenario(
        name="FULL_ATTACK",
        description="Simulate complete attack: USB + keystroke burst + terminal launch",
        duration_seconds=12,
        attack_type="MULTI_SIGNAL_USB_HID_ATTACK",
    )

    # Simulated device names
    FAKE_DEVICES = [
        "USB Keyboard Device",
        "Unknown HID Device",
        "Generic USB HID Keyboard",
        "USB Input Device",
    ]

    # Simulated terminal processes
    FAKE_TERMINALS = [
        "cmd.exe",
        "powershell.exe",
        "bash",
    ]

    def __init__(self, detection_engine: DetectionEngine):
        """
        Initialize attack simulator.

        Args:
            detection_engine: DetectionEngine instance to feed events
        """
        self.detection_engine = detection_engine
        self.simulation_thread: threading.Thread = None
        self.is_running = False
        logger.info("Attack simulator initialized")

    def simulate_scenario(
        self,
        scenario: SimulationScenario,
        callback_usb: callable = None,
        callback_keystrokes: callable = None,
        callback_process: callable = None,
    ) -> None:
        """
        Run a simulation scenario with callbacks.

        Args:
            scenario: SimulationScenario to simulate
            callback_usb: Callback for USB events
            callback_keystrokes: Callback for keystroke events
            callback_process: Callback for process events
        """
        logger.info(f"Starting simulation: {scenario.name}")
        logger.info(f"Description: {scenario.description}")
        logger.info(f"Duration: {scenario.duration_seconds} seconds")

        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=scenario.duration_seconds)

        # Common event timestamps
        usb_insertion_time = start_time + timedelta(seconds=1)
        keystroke_start_time = start_time + timedelta(seconds=2)
        process_launch_time = start_time + timedelta(seconds=3)

        # Simulate events based on scenario
        if scenario.attack_type == "USB_HID_TERMINAL_ATTACK":
            # Simulate USB insertion
            if callback_usb:
                usb_event = USBEvent(
                    device_id="USB_SIM_001",
                    device_name=choice(self.FAKE_DEVICES),
                    event_type="insert",
                    timestamp=usb_insertion_time,
                )
                callback_usb(usb_event)
                logger.info(f"Simulated USB insertion: {usb_event.device_name}")

            # Wait a bit
            time.sleep(1)

            # Simulate terminal launch shortly after
            if callback_process:
                process = ProcessEvent(
                    process_name=choice(self.FAKE_TERMINALS),
                    pid=randint(4000, 9999),
                    timestamp=process_launch_time,
                    is_suspicious=True,
                )
                callback_process(process)
                logger.info(f"Simulated process launch: {process.process_name}")

        elif scenario.attack_type == "AUTOMATED_KEYSTROKE_INJECTION":
            # Simulate rapid keystroke burst
            if callback_keystrokes:
                logger.info("Simulating keystroke burst...")
                num_keystrokes = 50  # Very fast typing
                for i in range(num_keystrokes):
                    keystroke_time = keystroke_start_time + timedelta(
                        milliseconds=i * 30
                    )  # ~33 keystrokes per second
                    callback_keystrokes(keystroke_time)
                    time.sleep(0.03)

                logger.info(f"Simulated {num_keystrokes} keystrokes in burst")

        elif scenario.attack_type == "MULTI_SIGNAL_USB_HID_ATTACK":
            # Full attack simulation
            if callback_usb:
                usb_event = USBEvent(
                    device_id="USB_SIM_FULL",
                    device_name=choice(self.FAKE_DEVICES),
                    event_type="insert",
                    timestamp=usb_insertion_time,
                )
                callback_usb(usb_event)
                logger.info(f"Simulated USB insertion: {usb_event.device_name}")

            time.sleep(0.5)

            if callback_keystrokes:
                logger.info("Simulating keystroke burst...")
                num_keystrokes = 60
                for i in range(num_keystrokes):
                    keystroke_time = keystroke_start_time + timedelta(
                        milliseconds=i * 25
                    )
                    callback_keystrokes(keystroke_time)
                    time.sleep(0.025)

            if callback_process:
                process = ProcessEvent(
                    process_name=choice(self.FAKE_TERMINALS),
                    pid=randint(4000, 9999),
                    timestamp=process_launch_time,
                    is_suspicious=True,
                )
                callback_process(process)
                logger.info(f"Simulated process launch: {process.process_name}")

        logger.info(f"Simulation completed: {scenario.name}")

    def run_scenario_async(
        self,
        scenario: SimulationScenario,
        callback_usb: callable = None,
        callback_keystrokes: callable = None,
        callback_process: callable = None,
    ) -> threading.Thread:
        """
        Run a scenario asynchronously in a background thread.

        Args:
            scenario: SimulationScenario to simulate
            callback_usb: Callback for USB events
            callback_keystrokes: Callback for keystroke events
            callback_process: Callback for process events

        Returns:
            Thread object (already started)
        """
        thread = threading.Thread(
            target=self.simulate_scenario,
            args=(scenario, callback_usb, callback_keystrokes, callback_process),
            daemon=True,
        )
        thread.start()
        return thread


class SimulationConfigs:
    """Collection of pre-configured simulation scenarios."""

    @staticmethod
    def get_all_scenarios() -> list:
        """Get all available scenarios."""
        return [
            AttackSimulator.SCENARIO_USB_INSERTION,
            AttackSimulator.SCENARIO_KEYSTROKE_BURST,
            AttackSimulator.SCENARIO_TERMINAL_LAUNCH,
            AttackSimulator.SCENARIO_FULL_ATTACK,
        ]

    @staticmethod
    def get_scenario_by_name(name: str) -> SimulationScenario:
        """Get scenario by name."""
        scenarios = SimulationConfigs.get_all_scenarios()
        for scenario in scenarios:
            if scenario.name == name:
                return scenario
        raise ValueError(f"Unknown scenario: {name}")

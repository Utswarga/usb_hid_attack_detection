"""
Main orchestrator for the USB HID Attack Detection System.
Coordinates all components and manages the detection lifecycle.
"""

import time
import threading
import argparse
from datetime import datetime
from typing import Optional

from core import (
    logger,
    create_usb_monitor,
    KeystrokeAnalyzer,
    ProcessMonitor,
    DetectionEngine,
    ResponseEngine,
    AttackSimulator,
    SimulationConfigs,
)
from core.config import SIMULATION_MODE


class DetectionSystem:
    """Main detection system orchestrator."""

    def __init__(self, enable_simulation: bool = False):
        """
        Initialize detection system.

        Args:
            enable_simulation: Enable simulation mode for testing
        """
        self.enable_simulation = enable_simulation
        self.is_running = False

        # Initialize components
        logger.info("Initializing USB HID Attack Detection System...")
        self.usb_monitor = create_usb_monitor()
        self.keystroke_analyzer = KeystrokeAnalyzer()
        self.process_monitor = ProcessMonitor()
        self.detection_engine = DetectionEngine()
        self.response_engine = ResponseEngine(process_monitor=self.process_monitor)
        self.simulator = AttackSimulator(self.detection_engine)

        # Register callbacks
        self._register_callbacks()

        logger.info("✓ Detection system initialized successfully")
        self._print_system_info()

    def _register_callbacks(self) -> None:
        """Register callbacks between components."""
        # USB events -> Detection engine
        self.usb_monitor.register_callback(
            self._handle_usb_event
        )

        # Process launch -> Detection engine
        # (handled in main loop)

        logger.info("✓ Component callbacks registered")

    def _handle_usb_event(self, usb_event) -> None:
        """
        Handle USB device event.

        Args:
            usb_event: USBEvent instance
        """
        logger.info(f"USB event: {usb_event}")
        self.detection_engine.process_usb_event(usb_event)
        self._try_correlate()

    def _handle_keystroke_pattern(self, pattern) -> None:
        """
        Handle keystroke pattern detection.

        Args:
            pattern: KeystrokePattern instance
        """
        logger.info(f"Keystroke pattern: {pattern}")
        self.detection_engine.process_keystroke_pattern(pattern)
        self._try_correlate()

    def _handle_process_event(self, process_event) -> None:
        """
        Handle process launch event.

        Args:
            process_event: ProcessEvent instance
        """
        logger.info(f"Process event: {process_event}")
        if process_event.is_suspicious:
            self.detection_engine.process_process_event(
                process_event, is_after_usb=True
            )
            self._try_correlate()

    def _try_correlate(self) -> None:
        """Try to correlate signals and detect attacks."""
        attack_event = self.detection_engine.correlate_signals()
        if attack_event:
            logger.critical(f"ATTACK DETECTED: {attack_event}")
            self.response_engine.handle_attack(attack_event)

    def _print_system_info(self) -> None:
        """Print system information."""
        print("\n" + "=" * 80)
        print("USB HID ATTACK DETECTION SYSTEM v1.0")
        print("=" * 80)
        print(f"Started at: {datetime.now().isoformat()}")
        print(f"Simulation mode: {'ENABLED' if self.enable_simulation else 'DISABLED'}")
        print(f"Logging to: logs/events.log")
        print("=" * 80 + "\n")

    def start(self) -> None:
        """Start the detection system."""
        if self.is_running:
            logger.warning("System already running")
            return

        self.is_running = True
        logger.info("Starting detection system...")

        # Start USB monitor
        self.usb_monitor.start_monitoring()

        # Run monitoring loop on a daemon thread so Ctrl+C can shut down cleanly.
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitor_thread.start()

        logger.info("✓ Detection system started")

    def stop(self) -> None:
        """Stop the detection system."""
        if not self.is_running:
            logger.warning("System not running")
            return

        self.is_running = False
        logger.info("Stopping detection system...")

        self.usb_monitor.stop_monitoring()
        self._print_statistics()
        logger.info("✓ Detection system stopped")

    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self.is_running:
            try:
                # 1) Collect process-launch signals from the OS.
                new_processes = self.process_monitor.check_for_new_processes()
                for process in new_processes:
                    self._handle_process_event(process)

                # 2) Analyze recent keystrokes and emit pattern signals.
                pattern = self.keystroke_analyzer.analyze_pattern()
                if pattern:
                    self._handle_keystroke_pattern(pattern)

                # 3) Sleep briefly to avoid a busy loop and reduce CPU usage.
                time.sleep(1)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)

    def run_simulation(self, scenario_name: str = "FULL_ATTACK") -> None:
        """
        Run a simulation scenario.

        Args:
            scenario_name: Name of scenario to simulate
        """
        logger.info(f"Running simulation scenario: {scenario_name}")

        try:
            scenario = SimulationConfigs.get_scenario_by_name(scenario_name)
        except ValueError as e:
            logger.error(f"Invalid scenario: {e}")
            print(f"\nAvailable scenarios:")
            for s in SimulationConfigs.get_all_scenarios():
                print(f"  - {s.name}: {s.description}")
            return

        self.simulator.run_scenario_async(
            scenario=scenario,
            callback_usb=self._handle_usb_event,
            callback_keystrokes=self.keystroke_analyzer.record_keystroke,
            callback_process=self._handle_process_event,
        )

    def _print_statistics(self) -> None:
        """Print monitoring statistics."""
        print("\n" + "=" * 80)
        print("DETECTION SYSTEM STATISTICS")
        print("=" * 80)

        usb_stats = {
            "status": "monitoring" if self.usb_monitor.is_running else "stopped"
        }
        keystroke_stats = self.keystroke_analyzer.get_statistics()
        process_stats = self.process_monitor.get_statistics()
        detection_stats = self.detection_engine.get_statistics()
        response_stats = self.response_engine.get_statistics()

        print(f"\nUSB Monitor: {usb_stats['status']}")
        print(f"\nKeystroke Analysis:")
        for key, value in keystroke_stats.items():
            print(f"  {key}: {value}")

        print(f"\nProcess Monitoring:")
        for key, value in process_stats.items():
            print(f"  {key}: {value}")

        print(f"\nDetection Engine:")
        for key, value in detection_stats.items():
            print(f"  {key}: {value}")

        print(f"\nResponse Engine:")
        for key, value in response_stats.items():
            print(f"  {key}: {value}")

        print("\n" + "=" * 80 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="USB HID Attack Detection System"
    )
    parser.add_argument(
        "--simulate",
        type=str,
        default=None,
        help="Run a simulation scenario (FULL_ATTACK, USB_INSERTION, etc.)",
    )
    parser.add_argument(
        "--list-scenarios",
        action="store_true",
        help="List available simulation scenarios",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Duration to run the system (seconds)",
    )

    args = parser.parse_args()

    # List scenarios if requested
    if args.list_scenarios:
        print("\nAvailable Simulation Scenarios:")
        print("=" * 80)
        for scenario in SimulationConfigs.get_all_scenarios():
            print(f"\n{scenario.name}")
            print(f"  Description: {scenario.description}")
            print(f"  Duration: {scenario.duration_seconds}s")
            print(f"  Attack Type: {scenario.attack_type}")
        print("\n" + "=" * 80 + "\n")
        return

    # Create and start system
    system = DetectionSystem(enable_simulation=args.simulate is not None)

    try:
        # Start monitoring
        system.start()

        # Run simulation if requested
        if args.simulate:
            logger.info(f"Simulation mode: {args.simulate}")
            system.run_simulation(args.simulate)
            # Give simulation time to complete
            time.sleep(args.simulate if args.simulate else args.duration + 5)
        else:
            # Run for specified duration
            logger.info(
                f"System running for {args.duration} seconds..."
            )
            try:
                time.sleep(args.duration)
            except KeyboardInterrupt:
                logger.info("Interrupted by user")

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        system.stop()


if __name__ == "__main__":
    main()

"""
Example usage of the USB HID Attack Detection System.

This script demonstrates:
1. Basic system initialization and monitoring
2. Custom response handlers
3. Simulation-based testing
4. Statistics collection
"""

import time
import argparse
from datetime import datetime

from core import (
    DetectionSystem,
    logger,
    SimulationConfigs,
)


def example_basic_monitoring():
    """Example 1: Basic monitoring for 30 seconds."""
    print("\n=== Example 1: Basic Monitoring ===\n")

    system = DetectionSystem()
    system.start()

    print("Monitoring active. Press Ctrl+C to stop...")
    try:
        time.sleep(30)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

    system.stop()


def example_custom_response_handler():
    """Example 2: Register custom response handler."""
    print("\n=== Example 2: Custom Response Handler ===\n")

    system = DetectionSystem()

    # Define custom response handler
    def send_to_email_alert(attack_event):
        """Send email alert on attack detection."""
        logger.info(
            f"[CUSTOM] Email alert would be sent for {attack_event.attack_type}",
            event_data={"attack_type": attack_event.attack_type},
        )
        # In production, integrate with email service
        # Example: requests.post("https://alert-service/send", ...)

    # Register handler
    system.response_engine.register_custom_handler(send_to_email_alert)

    system.start()

    # Run a simulation to trigger the custom handler
    print("Starting FULL_ATTACK simulation...")
    system.run_simulation("FULL_ATTACK")

    # Wait for simulation to complete
    time.sleep(15)

    system.stop()


def example_simulation_testing():
    """Example 3: Test multiple attack scenarios."""
    print("\n=== Example 3: Simulation Testing ===\n")

    system = DetectionSystem(enable_simulation=True)
    system.start()

    scenarios = ["USB_INSERTION", "KEYSTROKE_BURST", "FULL_ATTACK"]

    for scenario_name in scenarios:
        print(f"\n--- Testing {scenario_name} ---")
        system.run_simulation(scenario_name)
        time.sleep(15)  # Wait for each scenario

    system.stop()


def example_statistics_collection():
    """Example 4: Collect and display statistics."""
    print("\n=== Example 4: Statistics Collection ===\n")

    system = DetectionSystem()
    system.start()

    print("Collecting statistics for 20 seconds...")
    time.sleep(20)

    # Get statistics from all components
    print("\n--- Keystroke Analysis ---")
    ks_stats = system.keystroke_analyzer.get_statistics()
    for key, value in ks_stats.items():
        print(f"  {key}: {value}")

    print("\n--- Process Monitoring ---")
    pm_stats = system.process_monitor.get_statistics()
    for key, value in pm_stats.items():
        print(f"  {key}: {value}")

    print("\n--- Detection Engine ---")
    de_stats = system.detection_engine.get_statistics()
    for key, value in de_stats.items():
        print(f"  {key}: {value}")

    print("\n--- Response Engine ---")
    re_stats = system.response_engine.get_statistics()
    for key, value in re_stats.items():
        print(f"  {key}: {value}")

    system.stop()


def example_multiple_handlers():
    """Example 5: Multiple custom handlers (e.g., for different alert channels)."""
    print("\n=== Example 5: Multiple Custom Handlers ===\n")

    system = DetectionSystem()

    def slack_notification(attack_event):
        """Send Slack notification."""
        logger.info(f"[SLACK] Attack notification sent: {attack_event.attack_type}")

    def syslog_alert(attack_event):
        """Send to syslog."""
        logger.info(f"[SYSLOG] Attack logged: {attack_event.attack_type}")

    def webhook_alert(attack_event):
        """Send to webhook."""
        logger.info(f"[WEBHOOK] Attack reported: {attack_event.attack_type}")

    system.response_engine.register_custom_handler(slack_notification)
    system.response_engine.register_custom_handler(syslog_alert)
    system.response_engine.register_custom_handler(webhook_alert)

    system.start()

    print("Running FULL_ATTACK simulation with multiple handlers...\n")
    system.run_simulation("FULL_ATTACK")

    time.sleep(15)
    system.stop()


def example_continuous_monitoring():
    """Example 6: Continuous monitoring with periodic stats reporting."""
    print("\n=== Example 6: Continuous Monitoring ===\n")

    system = DetectionSystem()
    system.start()

    print("Monitoring with periodic stats (runs for 30 seconds)...\n")

    try:
        for i in range(3):
            time.sleep(10)
            print(f"\n--- Stats Update {i+1} ---")
            de_stats = system.detection_engine.get_statistics()
            re_stats = system.response_engine.get_statistics()
            print(f"Signals: {de_stats['total_signals_history']}")
            print(f"Attacks: {de_stats['total_attacks_detected']}")
            print(f"Responses: {re_stats['total_responses']}")

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

    system.stop()


def main():
    """Run selected examples."""
    parser = argparse.ArgumentParser(
        description="USB HID Attack Detection System - Examples"
    )
    parser.add_argument(
        "example",
        type=int,
        choices=[1, 2, 3, 4, 5, 6],
        help="Example to run (1-6)",
    )

    args = parser.parse_args()

    examples = {
        1: example_basic_monitoring,
        2: example_custom_response_handler,
        3: example_simulation_testing,
        4: example_statistics_collection,
        5: example_multiple_handlers,
        6: example_continuous_monitoring,
    }

    print("\n" + "=" * 80)
    print("USB HID ATTACK DETECTION SYSTEM - EXAMPLES")
    print("=" * 80)

    try:
        examples[args.example]()
    except Exception as e:
        logger.error(f"Example failed: {e}")
        raise

    print("\n" + "=" * 80)
    print("Example completed successfully!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

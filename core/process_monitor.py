"""
Process monitoring module for detecting suspicious process launches.
"""

import psutil
from datetime import datetime, timedelta
from typing import List, Optional, Set
from collections import deque

from core.logger import StructuredLogger
from core.config import SUSPICIOUS_PROCESSES

logger = StructuredLogger(__name__)


class ProcessEvent:
    """Represents a process launch event."""

    def __init__(
        self,
        process_name: str,
        pid: int,
        timestamp: datetime = None,
        is_suspicious: bool = False,
    ):
        """
        Initialize process event.

        Args:
            process_name: Name of the process
            pid: Process ID
            timestamp: When the process was launched
            is_suspicious: Whether this process is flagged as suspicious
        """
        self.process_name = process_name
        self.pid = pid
        self.timestamp = timestamp or datetime.now()
        self.is_suspicious = is_suspicious

    def __repr__(self) -> str:
        return (
            f"ProcessEvent(name={self.process_name}, pid={self.pid}, "
            f"suspicious={self.is_suspicious}, ts={self.timestamp})"
        )


class ProcessMonitor:
    """Monitors process launches for suspicious activity."""

    def __init__(self):
        """Initialize process monitor."""
        self.process_history: deque = deque(maxlen=200)
        self.tracked_pids: Set[int] = set()
        self._baseline_processes = self._get_current_processes()
        logger.info(
            f"Process monitor initialized with {len(self._baseline_processes)} "
            "baseline processes"
        )

    def _get_current_processes(self) -> Set[str]:
        """Get set of currently running processes."""
        try:
            processes = set()
            for proc in psutil.process_iter(["name"]):
                try:
                    processes.add(proc.info["name"].lower())
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return processes
        except Exception as e:
            logger.error(f"Error getting process list: {e}")
            return set()

    def check_for_new_processes(self) -> List[ProcessEvent]:
        """
        Check for newly launched processes.

        Returns:
            List of detected process events
        """
        # Refresh snapshot to reflect current system state for this polling cycle.
        current_processes = self._get_current_processes()
        new_processes = []

        try:
            for proc in psutil.process_iter(["pid", "name", "create_time"]):
                try:
                    process_name = proc.info["name"].lower()
                    pid = proc.info["pid"]

                    # Skip if we've already tracked this PID
                    if pid in self.tracked_pids:
                        continue

                    # Suspicious list check is substring-based to catch variants
                    # like powershell_ise.exe or renamed wrappers.
                    is_suspicious = any(
                        susp.lower() in process_name
                        for susp in SUSPICIOUS_PROCESSES
                    )

                    # Record either suspicious launches or non-baseline launches.
                    if is_suspicious or process_name not in self._baseline_processes:
                        event = ProcessEvent(
                            process_name=process_name,
                            pid=pid,
                            is_suspicious=is_suspicious,
                        )
                        new_processes.append(event)
                        self.tracked_pids.add(pid)
                        self.process_history.append(event)

                        if is_suspicious:
                            logger.warning(
                                f"Suspicious process detected: {process_name} (PID: {pid})",
                                event_data={
                                    "process_name": process_name,
                                    "pid": pid,
                                    "suspicious": True,
                                },
                            )

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

        except Exception as e:
            logger.error(f"Error checking for new processes: {e}")

        return new_processes

    def is_process_suspicious(self, process_name: str) -> bool:
        """
        Check if a process name is in the suspicious list.

        Args:
            process_name: Name of the process to check

        Returns:
            True if process is suspicious, False otherwise
        """
        process_lower = process_name.lower()
        return any(
            susp.lower() in process_lower for susp in SUSPICIOUS_PROCESSES
        )

    def get_suspicious_processes_since(
        self, time_delta: timedelta = None
    ) -> List[ProcessEvent]:
        """
        Get suspicious processes launched in the last N seconds/minutes.

        Args:
            time_delta: Time delta to look back (default: last 1 minute)

        Returns:
            List of suspicious process events
        """
        if time_delta is None:
            time_delta = timedelta(minutes=1)

        cutoff_time = datetime.now() - time_delta
        return [
            event
            for event in self.process_history
            if event.is_suspicious and event.timestamp >= cutoff_time
        ]

    def terminate_process(self, pid: int, force: bool = False) -> bool:
        """
        Attempt to terminate a suspicious process.

        Args:
            pid: Process ID to terminate
            force: Whether to force kill the process

        Returns:
            True if termination was successful, False otherwise
        """
        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
                logger.warning(
                    f"Forcefully killed process {proc.name()} (PID: {pid})",
                    event_data={"pid": pid, "process_name": proc.name()},
                )
            else:
                proc.terminate()
                logger.warning(
                    f"Terminated process {proc.name()} (PID: {pid})",
                    event_data={"pid": pid, "process_name": proc.name()},
                )
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:
            logger.error(
                f"Failed to terminate process {pid}: {e}",
                event_data={"pid": pid, "error": str(e)},
            )
            return False

    def get_process_info(self, pid: int) -> Optional[dict]:
        """
        Get information about a specific process.

        Args:
            pid: Process ID

        Returns:
            Dictionary with process information or None if not found
        """
        try:
            proc = psutil.Process(pid)
            return {
                "pid": pid,
                "name": proc.name(),
                "exe": proc.exe() if hasattr(proc, "exe") else "N/A",
                "cmdline": " ".join(proc.cmdline()) if hasattr(proc, "cmdline") else "N/A",
                "create_time": datetime.fromtimestamp(proc.create_time()),
                "status": proc.status(),
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.warning(f"Cannot get info for process {pid}: {e}")
            return None

    def get_statistics(self) -> dict:
        """
        Get statistics about process monitoring.

        Returns:
            Dictionary with process statistics
        """
        recent_suspicious = self.get_suspicious_processes_since()
        return {
            "total_tracked_pids": len(self.tracked_pids),
            "history_size": len(self.process_history),
            "suspicious_in_last_minute": len(recent_suspicious),
        }

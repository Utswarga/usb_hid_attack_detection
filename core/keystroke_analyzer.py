"""
Keystroke pattern analyzer for detecting abnormal typing speeds and patterns.
"""

import time
from collections import deque
from datetime import datetime, timedelta
from typing import List, Optional

from core.logger import StructuredLogger
from core.config import (
    KEYSTROKE_SPEED_THRESHOLD,
    KEYSTROKE_TIME_WINDOW,
    MIN_KEYSTROKES_FOR_BURST,
)

logger = StructuredLogger(__name__)


class KeystrokeEvent:
    """Represents a single keystroke event."""

    def __init__(self, timestamp: datetime = None, key_code: int = 0):
        """
        Initialize keystroke event.

        Args:
            timestamp: When the keystroke occurred
            key_code: Numeric code for the key pressed
        """
        self.timestamp = timestamp or datetime.now()
        self.key_code = key_code

    def __repr__(self) -> str:
        return f"KeystrokeEvent(timestamp={self.timestamp}, key_code={self.key_code})"


class KeystrokePattern:
    """Represents detected keystroke pattern."""

    def __init__(
        self,
        pattern_type: str,  # "normal", "burst", "automated"
        wpm: float,
        keystroke_count: int,
        timestamp: datetime = None,
    ):
        """
        Initialize keystroke pattern.

        Args:
            pattern_type: Type of pattern detected
            wpm: Words per minute typing speed
            keystroke_count: Number of keystrokes in the window
            timestamp: When pattern was detected
        """
        self.pattern_type = pattern_type
        self.wpm = wpm
        self.keystroke_count = keystroke_count
        self.timestamp = timestamp or datetime.now()
        self.severity = self._calculate_severity()

    def _calculate_severity(self) -> str:
        """Calculate severity level of the pattern."""
        if self.pattern_type == "automated":
            return "CRITICAL"
        elif self.pattern_type == "burst" and self.wpm > KEYSTROKE_SPEED_THRESHOLD * 1.5:
            return "HIGH"
        elif self.pattern_type == "burst":
            return "MEDIUM"
        else:
            return "LOW"

    def __repr__(self) -> str:
        return (
            f"KeystrokePattern(type={self.pattern_type}, wpm={self.wpm:.1f}, "
            f"keystrokes={self.keystroke_count}, severity={self.severity})"
        )


class KeystrokeAnalyzer:
    """Analyzes keystroke patterns for attacks."""

    def __init__(self, time_window: float = KEYSTROKE_TIME_WINDOW):
        """
        Initialize keystroke analyzer.

        Args:
            time_window: Time window (seconds) to analyze keystroke patterns
        """
        self.time_window = time_window
        self.keystroke_buffer: deque = deque(maxlen=100)
        self.pattern_history: List[KeystrokePattern] = []
        logger.info(f"Keystroke analyzer initialized (window: {time_window}s)")

    def record_keystroke(self, timestamp: datetime = None) -> None:
        """
        Record a keystroke event.

        Args:
            timestamp: When the keystroke occurred
        """
        if timestamp is None:
            timestamp = datetime.now()

        event = KeystrokeEvent(timestamp=timestamp)
        self.keystroke_buffer.append(event)

    def analyze_pattern(self) -> Optional[KeystrokePattern]:
        """
        Analyze current keystroke pattern.

        Returns:
            KeystrokePattern if a pattern is detected, None otherwise
        """
        if len(self.keystroke_buffer) < MIN_KEYSTROKES_FOR_BURST:
            return None

        now = datetime.now()
        window_start = now - timedelta(seconds=self.time_window)

        # Filter keystrokes within the window
        recent_keystrokes = [
            ks for ks in self.keystroke_buffer if ks.timestamp >= window_start
        ]

        if len(recent_keystrokes) < MIN_KEYSTROKES_FOR_BURST:
            return None

        # Calculate typing speed
        wpm = self._calculate_wpm(recent_keystrokes)
        keystroke_count = len(recent_keystrokes)

        # Determine pattern type
        pattern_type = "normal"
        if wpm > KEYSTROKE_SPEED_THRESHOLD:
            pattern_type = "burst"
        if wpm > KEYSTROKE_SPEED_THRESHOLD * 2:
            pattern_type = "automated"

        if pattern_type != "normal":
            pattern = KeystrokePattern(
                pattern_type=pattern_type,
                wpm=wpm,
                keystroke_count=keystroke_count,
                timestamp=now,
            )
            self.pattern_history.append(pattern)

            logger.warning(
                f"Abnormal keystroke pattern detected: {pattern}",
                event_data={
                    "pattern_type": pattern_type,
                    "wpm": round(wpm, 2),
                    "keystroke_count": keystroke_count,
                    "severity": pattern.severity,
                },
            )
            return pattern

        return None

    def _calculate_wpm(self, keystrokes: List[KeystrokeEvent]) -> float:
        """
        Calculate typing speed in words per minute.

        Args:
            keystrokes: List of keystroke events

        Returns:
            Typing speed in WPM (approximate)
        """
        if len(keystrokes) < 2:
            return 0.0

        first_keystroke = keystrokes[0]
        last_keystroke = keystrokes[-1]

        time_span_seconds = (
            last_keystroke.timestamp - first_keystroke.timestamp
        ).total_seconds()
        if time_span_seconds == 0:
            time_span_seconds = 0.1

        # Rough approximation: average word is 5 characters
        # so WPM = (keystroke_count / 5) / (time_in_minutes)
        keystroke_count = len(keystrokes)
        time_in_minutes = time_span_seconds / 60.0

        if time_in_minutes == 0:
            return keystroke_count * 60 / 1  # If < 1 second, extrapolate

        wpm = (keystroke_count / 5.0) / time_in_minutes
        return wpm

    def get_recent_patterns(
        self, minutes: int = 5
    ) -> List[KeystrokePattern]:
        """
        Get keystroke patterns from the last N minutes.

        Args:
            minutes: Number of minutes to look back

        Returns:
            List of detected patterns
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            p for p in self.pattern_history
            if p.timestamp >= cutoff_time
        ]

    def reset(self) -> None:
        """Reset the keystroke buffer."""
        self.keystroke_buffer.clear()
        logger.info("Keystroke buffer reset")

    def get_statistics(self) -> dict:
        """
        Get statistics about keystroke patterns.

        Returns:
            Dictionary with pattern statistics
        """
        recent_patterns = self.get_recent_patterns(minutes=5)
        abnormal_patterns = [
            p for p in recent_patterns if p.pattern_type != "normal"
        ]

        return {
            "total_recent_patterns": len(recent_patterns),
            "abnormal_patterns": len(abnormal_patterns),
            "average_wpm": (
                sum(p.wpm for p in recent_patterns) / len(recent_patterns)
                if recent_patterns
                else 0.0
            ),
            "max_wpm": max((p.wpm for p in recent_patterns), default=0.0),
            "buffer_size": len(self.keystroke_buffer),
        }

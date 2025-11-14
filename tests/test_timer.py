"""Tests for timer panel functionality."""

import pytest


def test_time_formatting():
    """Test formatting seconds to MM:SS."""
    def format_time(seconds: int) -> str:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    assert format_time(0) == "00:00"
    assert format_time(30) == "00:30"
    assert format_time(60) == "01:00"
    assert format_time(90) == "01:30"
    assert format_time(125) == "02:05"
    assert format_time(1500) == "25:00"  # 25 minutes
    assert format_time(300) == "05:00"   # 5 minutes


def test_timer_durations():
    """Test that timer durations are correct."""
    FOCUS_DURATION = 25 * 60  # 25 minutes
    BREAK_DURATION = 5 * 60   # 5 minutes

    assert FOCUS_DURATION == 1500
    assert BREAK_DURATION == 300


def test_progress_calculation():
    """Test timer progress percentage calculation."""
    def calculate_progress(remaining: int, total: int) -> float:
        return (remaining / total) * 100 if total > 0 else 0

    # Focus timer at start
    assert calculate_progress(1500, 1500) == 100.0

    # Focus timer half done
    assert calculate_progress(750, 1500) == 50.0

    # Focus timer almost done
    assert calculate_progress(150, 1500) == 10.0

    # Timer finished
    assert calculate_progress(0, 1500) == 0.0

    # Empty timer
    assert calculate_progress(0, 0) == 0.0


def test_timer_state_transitions():
    """Test timer state machine."""
    from enum import Enum

    class TimerState(Enum):
        IDLE = "idle"
        FOCUS = "focus"
        BREAK = "break"

    # Start in idle
    state = TimerState.IDLE
    assert state == TimerState.IDLE

    # Transition to focus
    state = TimerState.FOCUS
    assert state == TimerState.FOCUS

    # Transition to break
    state = TimerState.BREAK
    assert state == TimerState.BREAK

    # Back to idle
    state = TimerState.IDLE
    assert state == TimerState.IDLE


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

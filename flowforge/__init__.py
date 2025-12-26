"""
FlowForge - Event-driven workflow orchestration framework

Provides flexible connection, state management, and workflow orchestration capabilities.
"""

from flowforge.routine import Routine
from flowforge.slot import Slot
from flowforge.event import Event
from flowforge.connection import Connection
from flowforge.flow import Flow
from flowforge.job_state import JobState, ExecutionRecord
from flowforge.execution_tracker import ExecutionTracker
from flowforge.error_handler import ErrorHandler, ErrorStrategy

__all__ = [
    "Routine",
    "Slot",
    "Event",
    "Connection",
    "Flow",
    "JobState",
    "ExecutionRecord",
    "ExecutionTracker",
    "ErrorHandler",
    "ErrorStrategy",
]

__version__ = "0.1.0"


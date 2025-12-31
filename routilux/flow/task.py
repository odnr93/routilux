"""
Task-related classes for Flow execution.

Contains TaskPriority enum and SlotActivationTask dataclass.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from routilux.slot import Slot
    from routilux.connection import Connection


class TaskPriority(Enum):
    """Task priority for queue scheduling."""

    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class SlotActivationTask:
    """Slot activation task for queue-based execution.

    Each task is associated with a JobState to track execution state.
    This allows tasks executed in worker threads to access and update
    the correct JobState, even when running concurrently.
    """

    slot: "Slot"
    data: Dict[str, Any]
    connection: Optional["Connection"] = None
    priority: TaskPriority = TaskPriority.NORMAL
    retry_count: int = 0
    max_retries: int = 0
    created_at: Optional[datetime] = None
    job_state: Optional[Any] = None  # JobState for this execution

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def __lt__(self, other):
        """For priority queue sorting."""
        return self.priority.value < other.priority.value

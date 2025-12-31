"""
Event loop management utilities.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from routilux.flow.flow import Flow

logger = logging.getLogger(__name__)


def ensure_event_loop_running(flow: "Flow") -> bool:
    """Ensure event loop is running, restart if needed.

    This function checks if the event loop is running and restarts it if:
    - Event loop thread is not alive
    - There are tasks in the queue

    Args:
        flow: Flow object to check.

    Returns:
        True if event loop is running (or was restarted), False otherwise.
    """
    from routilux.flow.event_loop import start_event_loop

    queue_size = flow._task_queue.qsize()
    is_running = flow._execution_thread is not None and flow._execution_thread.is_alive()

    # If there are tasks but event loop is not running, restart it
    if queue_size > 0 and not is_running:
        logger.warning(
            f"Event loop stopped but {queue_size} tasks in queue. Restarting event loop."
        )
        start_event_loop(flow)
        return True

    return is_running

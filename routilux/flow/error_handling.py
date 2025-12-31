"""
Error handling logic for Flow execution.

Handles task errors and error handler resolution.
"""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from routilux.routine import Routine
    from routilux.flow.task import SlotActivationTask
    from routilux.error_handler import ErrorHandler
    from routilux.flow.flow import Flow


def get_error_handler_for_routine(
    routine: "Routine", routine_id: str, flow: "Flow"
) -> Optional["ErrorHandler"]:
    """Get error handler for a routine.

    Priority order:
    1. Routine-level error handler (if set)
    2. Flow-level error handler (if set)
    3. None (default STOP behavior)

    Args:
        routine: Routine object.
        routine_id: Routine ID.
        flow: Flow object.

    Returns:
        ErrorHandler instance or None.
    """
    if routine.get_error_handler() is not None:
        return routine.get_error_handler()

    return flow.error_handler


def handle_task_error(
    task: "SlotActivationTask",
    error: Exception,
    flow: "Flow",
) -> None:
    """Handle task execution error.

    Args:
        task: The task that failed.
        error: The exception that occurred.
        flow: Flow object.
    """
    routine = task.slot.routine
    routine_id = routine._id if routine else None

    error_handler = (
        get_error_handler_for_routine(routine, routine_id, flow) if routine_id and routine else None
    )

    if error_handler:
        should_retry = error_handler.handle_error(error, routine, routine_id, flow)

        if error_handler.strategy.value == "retry":
            if should_retry:
                max_retries = (
                    error_handler.max_retries if error_handler.max_retries > 0 else task.max_retries
                )
                if task.retry_count < max_retries:
                    from routilux.flow.task import SlotActivationTask

                    retry_task = SlotActivationTask(
                        slot=task.slot,
                        data=task.data,
                        connection=task.connection,
                        priority=task.priority,
                        retry_count=task.retry_count + 1,
                        max_retries=max_retries,
                        job_state=task.job_state,  # Preserve JobState in retry task
                    )
                    flow._enqueue_task(retry_task)
                    return
            # Max retries reached or non-retryable exception, fall through to default

        elif error_handler.strategy.value == "continue":
            # Errors are tracked in JobState execution history, not routine._stats
            # Get JobState from task (preferred) or thread-local storage (fallback)
            job_state = (
                task.job_state
                if task.job_state
                else getattr(flow._current_execution_job_state, "value", None)
            )
            if job_state and routine:
                # Find routine_id in flow
                routine_id = None
                for rid, r in flow.routines.items():
                    if r is routine:
                        routine_id = rid
                        break
                if routine_id:
                    # Record error in execution history
                    job_state.record_execution(
                        routine_id, "error", {"slot": task.slot.name, "error": str(error)}
                    )
            return

        elif error_handler.strategy.value == "skip":
            # Get JobState from task (preferred) or thread-local storage (fallback)
            job_state = (
                task.job_state
                if task.job_state
                else getattr(flow._current_execution_job_state, "value", None)
            )
            if job_state:
                job_state.update_routine_state(routine_id or "", {"status": "skipped"})
            return

    # Get JobState from task (preferred) or thread-local storage (fallback)
    job_state = (
        task.job_state
        if task.job_state
        else getattr(flow._current_execution_job_state, "value", None)
    )
    if job_state:
        job_state.status = "failed"
        job_state.update_routine_state(routine_id or "", {"status": "failed", "error": str(error)})

    flow._running = False

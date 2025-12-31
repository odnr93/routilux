Execution Completion API
========================

The execution completion functionality has been moved to ``JobState.wait_for_completion()``,
a static method of the ``JobState`` class. This provides better encapsulation and aligns
with the design where JobState manages execution state.

.. note::
   The completion API is now part of ``JobState``. See :doc:`../user_guide/job_state` for details.

JobState.wait_for_completion()
-------------------------------

The ``JobState.wait_for_completion()`` static method provides a robust, systematic way
to wait for flow execution to complete.

**Features:**

- **Completion Detection**: Checks if execution is complete by verifying:
  - Task queue is empty (no pending tasks)
  - No active tasks (all running tasks finished)
  - This works even if ``job_state.status`` is still ``"running"``
- **Stability Verification**: Performs multiple consecutive checks to avoid race conditions
  where tasks might be enqueued between checks
- **Timeout Safety**: The timeout parameter serves as a safety limit. If execution doesn't
  complete within the timeout, the function returns ``False`` and the caller should handle
  the timeout (e.g., force stop the event loop)
- **Long-running Tasks**: Supports long-running tasks (e.g., LLM calls) with configurable
  timeout
- **Event Loop Management**: Handles edge cases where event loop might exit prematurely
- **Progress Monitoring**: Optional progress callback for monitoring execution status

**Example:**

.. code-block:: python

   from routilux.job_state import JobState
   
   job_state = flow.execute(entry_routine_id="routine1")
   
   def progress_callback(queue_size, active_count, status):
       print(f"Queue: {queue_size}, Active: {active_count}, Status: {status}")
   
   completed = JobState.wait_for_completion(
       flow=flow,
       job_state=job_state,
       timeout=300.0,
       progress_callback=progress_callback
   )
   
   if completed:
       print("Execution completed successfully")
   else:
       print("Execution timed out")

**Internal Implementation:**

The ``JobState.wait_for_completion()`` method uses an internal ``_ExecutionCompletionChecker``
class to perform stability checks. This class is not part of the public API but is used
internally by the static method.

ensure_event_loop_running
--------------------------

The ``ensure_event_loop_running()`` function ensures the event loop is running,
restarting it if needed when there are tasks in the queue.

**Example:**

.. code-block:: python

   from routilux.flow.completion import ensure_event_loop_running
   
   # Check and restart event loop if needed
   if ensure_event_loop_running(flow):
       print("Event loop is running")

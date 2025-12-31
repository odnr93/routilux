JobState: Execution State Management
====================================

The ``JobState`` object is central to routilux's execution model. It represents the **execution state** of a single workflow execution, completely decoupled from the ``Flow`` (workflow definition).

Key Concepts
------------

**Flow vs JobState**:

- **Flow**: Static workflow definition (routines, connections, configuration)
- **JobState**: Dynamic execution state (execution history, routine states, status)

This separation allows:

- Multiple independent executions of the same flow
- Proper serialization and recovery
- Distributed execution across hosts
- Independent pause/resume/cancel operations

Creating JobState
-----------------

A ``JobState`` is automatically created when you call ``flow.execute()``:

.. code-block:: python
   :linenos:

   from routilux import Flow, Routine

   class Source(Routine):
       def __init__(self):
           super().__init__()
           self.trigger_slot = self.define_slot("trigger", handler=self.send)
           self.output_event = self.define_event("output", ["data"])
       
       def send(self, **kwargs):
           self.emit("output", data="test")

   flow = Flow(flow_id="my_flow")
   source = Source()
   source_id = flow.add_routine(source, "source")

   # Execute returns a JobState
   job_state = flow.execute(source_id)

   print(f"Job ID: {job_state.job_id}")
   print(f"Status: {job_state.status}")
   print(f"Flow ID: {job_state.flow_id}")

**Expected Output**:

::

   Job ID: 550e8400-e29b-41d4-a716-446655440000
   Status: completed
   Flow ID: my_flow

**Key Points**:

- Each ``execute()`` call creates a **new, independent** ``JobState``
- The ``JobState`` is returned to you - Flow does not manage it
- Multiple executions = multiple independent ``JobState`` objects

Multiple Independent Executions
--------------------------------

You can execute the same flow multiple times, each with its own ``JobState``:

.. code-block:: python
   :linenos:

   # Execute the same flow multiple times
   job_state1 = flow.execute(source_id, entry_params={"value": "A"})
   job_state2 = flow.execute(source_id, entry_params={"value": "B"})
   job_state3 = flow.execute(source_id, entry_params={"value": "C"})

   # Each execution has its own JobState
   assert job_state1.job_id != job_state2.job_id
   assert job_state2.job_id != job_state3.job_id
   assert job_state1 is not job_state2  # Different objects

   # Each has its own execution history
   print(f"Execution 1 history: {len(job_state1.execution_history)} records")
   print(f"Execution 2 history: {len(job_state2.execution_history)} records")
   print(f"Execution 3 history: {len(job_state3.execution_history)} records")

**Key Points**:

- Each execution is **completely independent**
- Execution history, routine states, and status are separate
- You can pause/resume/cancel each execution independently

JobState Properties
-------------------

The ``JobState`` object contains:

**Core Properties**:

- ``job_id``: Unique identifier for this execution
- ``flow_id``: Identifier of the flow that created this execution
- ``status``: Current execution status ("running", "completed", "failed", "paused", "cancelled")
- ``created_at``: Timestamp when execution started
- ``updated_at``: Timestamp of last update

**Execution Tracking**:

- ``execution_history``: List of ``ExecutionRecord`` objects (chronological log)
- ``routine_states``: Dictionary mapping routine_id to routine state
- ``current_routine_id``: Currently executing routine (if any)

**Metadata**:

- ``metadata``: Custom metadata dictionary
- ``checkpoint``: Checkpoint data for pause/resume

Accessing Execution History
---------------------------

The execution history provides a chronological log of all routine executions and event emissions:

.. code-block:: python
   :linenos:

   job_state = flow.execute(source_id)

   # Get all execution records
   all_records = job_state.execution_history
   print(f"Total records: {len(all_records)}")

   # Get records for a specific routine
   source_records = job_state.get_execution_history("source")
   print(f"Source records: {len(source_records)}")

   # Iterate through records
   for record in job_state.execution_history:
       print(f"{record.timestamp}: {record.routine_id} -> {record.event_name}")
       print(f"  Data: {record.data}")

**Expected Output**:

::

   Total records: 3
   Source records: 2
   2025-01-15T10:30:00: source -> start
     Data: {}
   2025-01-15T10:30:00.100: source -> output
     Data: {'data': 'test'}
   2025-01-15T10:30:00.200: source -> completed
     Data: {}

**Key Points**:

- Execution history is automatically recorded during execution
- Records include routine_id, event_name, data, and timestamp
- History is recorded in both main thread and worker threads

Accessing Routine States
------------------------

Routine states track the status and metadata of each routine during execution:

.. code-block:: python
   :linenos:

   job_state = flow.execute(source_id)

   # Get state for a specific routine
   source_state = job_state.get_routine_state("source")
   if source_state:
       print(f"Source status: {source_state.get('status')}")
       print(f"Source metadata: {source_state}")

   # Update routine state (typically done by error handlers)
   job_state.update_routine_state("source", {
       "status": "completed",
       "execution_time": 0.5,
       "custom_field": "value"
   })

   # Get updated state
   updated_state = job_state.get_routine_state("source")
   print(f"Updated state: {updated_state}")

**Key Points**:

- Routine states are updated automatically during execution
- Error handlers can update routine states
- You can add custom metadata to routine states

JobState Status
---------------

The ``status`` field tracks the current execution state:

**Status Values**:

- ``"running"``: Execution is in progress
- ``"completed"``: Execution completed successfully
- ``"failed"``: Execution failed (error occurred)
- ``"paused"``: Execution is paused (can be resumed)
- ``"cancelled"``: Execution was cancelled

**Status Transitions**:

.. code-block:: python
   :linenos:

   job_state = flow.execute(source_id)

   # Status starts as "running"
   print(f"Initial status: {job_state.status}")  # "running"

   # Wait for completion
   flow.wait_for_completion(timeout=5.0)

   # Status becomes "completed" or "failed"
   print(f"Final status: {job_state.status}")  # "completed" or "failed"

**Key Points**:

- Status is automatically updated during execution
- Status can be updated in both main thread and worker threads
- Status changes are thread-safe

Pause, Resume, and Cancel
-------------------------

You can control execution using the ``JobState``:

.. code-block:: python
   :linenos:

   # Execute
   job_state = flow.execute(source_id)

   # Pause execution (requires JobState)
   flow.pause(job_state, reason="Manual pause for inspection")

   # Check status
   assert job_state.status == "paused"

   # Resume execution (returns new JobState for resumed execution)
   resumed_job_state = flow.resume(job_state)

   # Wait for completion
   flow.wait_for_completion(timeout=5.0)
   assert resumed_job_state.status == "completed"

   # Cancel execution (if needed)
   another_job_state = flow.execute(source_id)
   flow.cancel(another_job_state, reason="No longer needed")
   assert another_job_state.status == "cancelled"

**Key Points**:

- ``pause()``, ``resume()``, and ``cancel()`` require the ``JobState`` as first argument
- Each execution can be paused/resumed/cancelled independently
- Flow does not manage these operations - you pass the ``JobState`` explicitly

Serialization and Persistence
------------------------------

``JobState`` can be serialized for persistence and recovery:

.. code-block:: python
   :linenos:

   import json

   # Execute and pause
   job_state = flow.execute(source_id)
   flow.pause(job_state, reason="Save for later")

   # Serialize JobState
   job_state_data = job_state.serialize()
   
   # Save to file
   with open("job_state.json", "w") as f:
       json.dump(job_state_data, f, indent=2)

   # Later: Load and deserialize
   with open("job_state.json", "r") as f:
       loaded_data = json.load(f)

   new_job_state = JobState()
   new_job_state.deserialize(loaded_data)

   # Resume execution
   resumed = flow.resume(new_job_state)

**Key Points**:

- ``JobState`` serialization is separate from ``Flow`` serialization
- Serialized ``JobState`` includes execution history, routine states, and status
- Deserialized ``JobState`` can be used to resume execution
- See :doc:`serialization` for cross-host scenarios

Thread Safety and Concurrent Execution
--------------------------------------

``JobState`` updates are thread-safe and work correctly in concurrent scenarios:

**Worker Thread Access**:

- ``JobState`` is passed to worker threads through ``SlotActivationTask``
- Worker threads can access and update ``JobState`` via thread-local storage
- All updates are synchronized and thread-safe

**Concurrent Executions**:

- Each execution has its own ``JobState``
- Concurrent executions in different threads are isolated
- No interference between executions

**Example**:

.. code-block:: python
   :linenos:

   import threading

   def run_execution(flow, entry_id, value):
       job_state = flow.execute(entry_id, entry_params={"value": value})
       return job_state

   # Run concurrent executions
   thread1 = threading.Thread(target=run_execution, args=(flow, source_id, "A"))
   thread2 = threading.Thread(target=run_execution, args=(flow, source_id, "B"))

   thread1.start()
   thread2.start()

   thread1.join()
   thread2.join()

   # Each thread has its own JobState
   # No interference between executions

**Key Points**:

- ``JobState`` is designed for concurrent execution
- Thread-local storage ensures correct ``JobState`` access in worker threads
- Each execution is isolated

Best Practices
--------------

**1. Store JobState for Recovery**:

.. code-block:: python
   :linenos:

   # Execute and store JobState
   job_state = flow.execute(source_id)
   
   # Save for recovery
   job_state_data = job_state.serialize()
   save_to_database(job_state_data)

**2. Use JobState for Status Monitoring**:

.. code-block:: python
   :linenos:

   job_state = flow.execute(source_id)
   
   # Monitor status
   while job_state.status == "running":
       time.sleep(0.1)
       # Status is updated automatically
   
   if job_state.status == "completed":
       print("Execution successful!")
   elif job_state.status == "failed":
       print("Execution failed!")

**3. Independent Execution Management**:

.. code-block:: python
   :linenos:

   # Execute multiple times
   executions = []
   for i in range(10):
       job_state = flow.execute(source_id, entry_params={"batch": i})
       executions.append(job_state)
   
   # Manage each independently
   for job_state in executions:
       if job_state.status == "paused":
           flow.resume(job_state)

**4. Cross-Host Execution**:

.. code-block:: python
   :linenos:

   # Host A: Execute and serialize
   job_state = flow.execute(source_id)
   flow.pause(job_state, reason="Transfer to Host B")
   
   flow_data = flow.serialize()
   job_state_data = job_state.serialize()
   
   # Send to Host B
   send_to_host_b(flow_data, job_state_data)
   
   # Host B: Deserialize and resume
   new_flow = Flow()
   new_flow.deserialize(flow_data)
   
   new_job_state = JobState()
   new_job_state.deserialize(job_state_data)
   
   resumed = new_flow.resume(new_job_state)

Common Pitfalls
---------------

**1. Assuming Flow Manages JobState**:

.. code-block:: python

   # Wrong: Flow doesn't have job_state
   flow.job_state.status  # AttributeError!

   # Correct: JobState is returned from execute()
   job_state = flow.execute(source_id)
   job_state.status  # OK

**2. Sharing JobState Between Executions**:

.. code-block:: python

   # Wrong: Reusing JobState from previous execution
   job_state1 = flow.execute(source_id)
   job_state2 = flow.execute(source_id)  # Different execution!
   # Don't use job_state1 for job_state2's operations

   # Correct: Use the JobState from the specific execution
   job_state = flow.execute(source_id)
   flow.pause(job_state, reason="pause this execution")

**3. Not Serializing JobState Separately**:

.. code-block:: python

   # Wrong: Flow serialization doesn't include JobState
   flow_data = flow.serialize()
   # job_state is NOT in flow_data!

   # Correct: Serialize separately
   flow_data = flow.serialize()
   job_state_data = job_state.serialize()
   # Save both for recovery

**4. Assuming JobState Persists Across Executions**:

.. code-block:: python

   # Wrong: Each execute() creates new JobState
   job_state1 = flow.execute(source_id)
   job_state2 = flow.execute(source_id)
   # job_state1 and job_state2 are different!

   # Correct: Store JobState if you need it
   job_state = flow.execute(source_id)
   save_job_state(job_state)

Related Topics
--------------

- :doc:`serialization` - Serialization and cross-host execution
- :doc:`state_management` - Pause, resume, and checkpoint management
- :doc:`flows` - Flow execution and management
- :doc:`error_handling` - Error handling and JobState updates


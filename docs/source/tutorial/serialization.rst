Serialization and Persistence
===============================

In this tutorial, you'll learn how to serialize and deserialize flows for
persistence, recovery, and distributed execution.

Learning Objectives
-------------------

By the end of this tutorial, you'll be able to:

- Serialize flows to JSON
- Deserialize flows from JSON
- Save and load JobState for recovery
- Understand serialization requirements
- Build persistent workflows

Step 1: Basic Flow Serialization
----------------------------------

You can serialize a flow to JSON for persistence. **Important**: By default,
``serialize()`` does NOT include execution state (job_state). This is the
recommended approach for proper execution recovery.

.. code-block:: python
   :linenos:

   from routilux import Flow, Routine
   import json

   class SimpleProcessor(Routine):
       def __init__(self):
           super().__init__()
           self.input_slot = self.define_slot("input", handler=self.process)
           self.output_event = self.define_event("output", ["result"])
       
       def process(self, data=None, **kwargs):
           data_value = data or kwargs.get("data", "")
           result = f"Processed: {data_value}"
           self.emit("output", result=result)

   class DataSource(Routine):
       def __init__(self):
           super().__init__()
           self.trigger_slot = self.define_slot("trigger", handler=self.send)
           self.output_event = self.define_event("output", ["data"])
       
       def send(self, **kwargs):
           self.emit("output", data="test")

   # Create and configure flow
   flow = Flow(flow_id="serializable_flow")
   
   source = DataSource()
   processor = SimpleProcessor()
   
   source_id = flow.add_routine(source, "source")
   processor_id = flow.add_routine(processor, "processor")
   
   flow.connect(source_id, "output", processor_id, "input")
   
   # Serialize flow (default: include_execution_state=False)
   # This only serializes flow structure, not execution state
   flow_data = flow.serialize()
   
   # Save to file
   with open("flow.json", "w") as f:
       json.dump(flow_data, f, indent=2)
   
   print("Flow serialized to flow.json")
   print(f"Flow ID: {flow_data['flow_id']}")
   print(f"Routines: {len(flow_data['routines'])}")
   print(f"Contains job_state: {'job_state' in flow_data}")

**Expected Output**:

.. code-block:: text

   Flow serialized to flow.json
   Flow ID: serializable_flow
   Routines: 2
   Contains job_state: False

**Key Points**:

- ``serialize()`` by default does NOT include execution state (recommended)
- Only serializes flow structure (routines, connections, configuration)
- Flow structure is preserved
- Execution state (JobState) should be serialized separately for recovery

Step 2: Deserializing Flows
----------------------------

Deserialize a flow from JSON. Since we serialized only the flow structure,
we can restore it and execute it:

.. code-block:: python
   :linenos:

   from routilux import Flow
   import json

   # Load from file
   with open("flow.json", "r") as f:
       flow_data = json.load(f)
   
   # Deserialize flow (create new instance and deserialize)
   restored_flow = Flow()
   restored_flow.deserialize(flow_data)
   
   print(f"Restored flow ID: {restored_flow.flow_id}")
   print(f"Routines: {len(restored_flow.routines)}")
   
   # Execute restored flow
   # Find entry routine ID (first routine in this case)
   entry_id = list(restored_flow.routines.keys())[0]
   job_state = restored_flow.execute(entry_id)
   
   print(f"Execution status: {job_state.status}")

**Expected Output**:

.. code-block:: text

   Restored flow ID: serializable_flow
   Routines: 2
   Execution status: completed

**Key Points**:

- ``Flow.deserialize()`` recreates flow from serialized data
- All routines and connections are restored
- Flow can be executed immediately after deserialization
- Routine instances are recreated (must have no-argument constructors)
- Note: This creates a NEW execution, not a continuation of a previous one

Step 3: Serialization Requirements
-----------------------------------

For serialization to work, routines must meet certain requirements:

.. code-block:: python
   :linenos:

   from routilux import Flow, Routine

   class ConfigurableProcessor(Routine):
       """Correct: Uses _config for configuration"""
       
       def __init__(self):
           super().__init__()
           self.input_slot = self.define_slot("input", handler=self.process)
           self.output_event = self.define_event("output", ["result"])
           # Configuration stored in _config (serializable)
           self.set_config(threshold=10, enabled=True)
       
       def process(self, data=None, **kwargs):
           threshold = self.get_config("threshold", default=5)
           enabled = self.get_config("enabled", default=False)
           
           if enabled:
               data_value = data or kwargs.get("data", 0)
               result = data_value * threshold
               self.emit("output", result=result)

   class BadProcessor(Routine):
       """Incorrect: Uses constructor parameters"""
       
       def __init__(self, threshold=10):  # ❌ Don't do this!
           super().__init__()
           self.threshold = threshold  # ❌ Not serializable!
           self.input_slot = self.define_slot("input", handler=self.process)
       
       def process(self, **kwargs):
           # This will break serialization
           pass

   flow = Flow(flow_id="config_flow")
   
   # Correct usage
   processor = ConfigurableProcessor()
   processor_id = flow.add_routine(processor, "processor")
   
   # Serialize (works correctly)
   flow_data = flow.serialize()
   print("Serialization successful")
   
   # Deserialize
   restored = Flow.deserialize(flow_data)
   print(f"Restored processor threshold: {restored.routines[processor_id].get_config('threshold')}")

**Expected Output**:

.. code-block:: text

   Serialization successful
   Restored processor threshold: 10

**Key Requirements**:

- Routines must have no-argument constructors (except ``self``)
- Configuration must be stored in ``_config`` dictionary
- Statistics are automatically serialized in ``_stats``
- Custom fields must be registered with ``add_serializable_fields()``
- Custom Routine classes must be registered with ``@register_serializable`` decorator
  (Routilux's built-in routines are already registered)

**Key Points**:

- Use ``set_config()`` and ``get_config()`` for configuration
- Don't use constructor parameters
- All configuration is automatically serialized

Step 4: Saving and Loading JobState
------------------------------------

You can save JobState for workflow recovery:

.. code-block:: python
   :linenos:

   from routilux import Flow, Routine, JobState

   class DataSource(Routine):
       def __init__(self):
           super().__init__()
           self.trigger_slot = self.define_slot("trigger", handler=self.send)
           self.output_event = self.define_event("output", ["data"])
       
       def send(self, **kwargs):
           self.emit("output", data="test_data")

   class Processor(Routine):
       def __init__(self):
           super().__init__()
           self.input_slot = self.define_slot("input", handler=self.process)
           self.output_event = self.define_event("output", ["result"])
       
       def process(self, data=None, **kwargs):
           data_value = data or kwargs.get("data", "")
           result = f"Processed: {data_value}"
           self.emit("output", result=result)

   flow = Flow(flow_id="recovery_flow")
   
   source = DataSource()
   processor = Processor()
   
   source_id = flow.add_routine(source, "source")
   processor_id = flow.add_routine(processor, "processor")
   
   flow.connect(source_id, "output", processor_id, "input")
   
   # Execute and save state
   job_state = flow.execute(source_id)
   
   # Save JobState
   job_state.save("workflow_state.json")
   print(f"JobState saved. Status: {job_state.status}")
   
   # Later, load and resume
   saved_state = JobState.load("workflow_state.json")
   print(f"Loaded JobState. Status: {saved_state.status}")
   print(f"Flow ID: {saved_state.flow_id}")

**Expected Output**:

.. code-block:: text

   JobState saved. Status: completed
   Loaded JobState. Status: completed
   Flow ID: recovery_flow

**Key Points**:

- ``save()`` saves JobState to a file
- ``JobState.load()`` loads saved state
- Can be used for workflow recovery
- State includes execution history and routine states

Step 5: Understanding Multiple Executions
-------------------------------------------

**Important**: Each ``execute()`` call creates an independent execution with
its own JobState. Multiple executions are tracked separately:

.. code-block:: python
   :linenos:

   from routilux import Flow, Routine

   class DataSource(Routine):
       def __init__(self):
           super().__init__()
           self.trigger_slot = self.define_slot("trigger", handler=self.send)
           self.output_event = self.define_event("output", ["data"])
       
       def send(self, value=None, **kwargs):
           value = value or kwargs.get("value", "default")
           self.emit("output", data=value)

   flow = Flow(flow_id="multi_execution_flow")
   source = DataSource()
   source_id = flow.add_routine(source, "source")
   
   # First execution
   job_state1 = flow.execute(source_id, entry_params={"value": "A"})
   print(f"Execution 1 - Job ID: {job_state1.job_id}, Status: {job_state1.status}")
   
   # Second execution (independent)
   job_state2 = flow.execute(source_id, entry_params={"value": "B"})
   print(f"Execution 2 - Job ID: {job_state2.job_id}, Status: {job_state2.status}")
   
   # Access all executions
   all_executions = flow.get_all_executions()
   print(f"Total executions tracked: {len(all_executions)}")
   
   # Access specific execution
   execution1 = flow.get_execution(job_state1.job_id)
   print(f"Retrieved execution 1: {execution1.job_id if execution1 else None}")

**Expected Output**:

.. code-block:: text

   Execution 1 - Job ID: <uuid1>, Status: completed
   Execution 2 - Job ID: <uuid2>, Status: completed
   Total executions tracked: 2
   Retrieved execution 1: <uuid1>

**Key Points**:

- Each ``execute()`` creates a new JobState with unique job_id
- Multiple executions are tracked in ``flow._active_executions``
- Use ``flow.get_execution(job_id)`` to retrieve specific execution
- Use ``flow.get_all_executions()`` to get all tracked executions
- ``flow.job_state`` only tracks the most recent execution (for backward compatibility)

Step 6: Complete Example - Cross-Host Execution Recovery
----------------------------------------------------------

Here's a complete example showing proper serialization for cross-host recovery:

.. code-block:: python
   :name: serialization_complete
   :linenos:

   from routilux import Flow, Routine, JobState
   import json
   import os

   class DataProcessor(Routine):
       def __init__(self):
           super().__init__()
           self.input_slot = self.define_slot("input", handler=self.process)
           self.output_event = self.define_event("output", ["result"])
           self.set_config(multiplier=2, prefix="Result")
       
       def process(self, data=None, **kwargs):
           data_value = data or kwargs.get("data", 0)
           multiplier = self.get_config("multiplier", default=1)
           prefix = self.get_config("prefix", default="")
           
           result = data_value * multiplier
           output = f"{prefix}: {result}" if prefix else str(result)
           
           self.emit("output", result=output)
           print(f"Processed {data_value} -> {output}")

   class DataSource(Routine):
       def __init__(self):
           super().__init__()
           self.trigger_slot = self.define_slot("trigger", handler=self.generate)
           self.output_event = self.define_event("output", ["data"])
       
       def generate(self, value=5, **kwargs):
           value = value or kwargs.get("value", 5)
           self.emit("output", data=value)

   def save_for_distribution():
       """Save workflow structure for distribution"""
       flow = Flow(flow_id="distributed_workflow")
       
       source = DataSource()
       processor = DataProcessor()
       
       source_id = flow.add_routine(source, "source")
       processor_id = flow.add_routine(processor, "processor")
       
       flow.connect(source_id, "output", processor_id, "input")
       
       # Serialize flow structure only (no execution state)
       flow_data = flow.serialize(include_execution_state=False)
       
       with open("workflow_structure.json", "w") as f:
           json.dump(flow_data, f, indent=2)
       
       print("Workflow structure saved to workflow_structure.json")
       return flow

   def execute_and_save_state():
       """Execute workflow and save execution state"""
       # Load workflow structure
       with open("workflow_structure.json", "r") as f:
           flow_data = json.load(f)
       
       flow = Flow()
       flow.deserialize(flow_data)
       
       # Execute
       entry_id = list(flow.routines.keys())[0]
       job_state = flow.execute(entry_id, entry_params={"value": 10})
       
       # Save execution state separately
       job_state_data = job_state.serialize()
       with open("execution_state.json", "w") as f:
           json.dump(job_state_data, f, indent=2)
       
       print(f"Execution state saved. Job ID: {job_state.job_id}")
       return job_state

   def restore_on_remote_host():
       """Simulate restoring on a remote host"""
       # Load workflow structure
       with open("workflow_structure.json", "r") as f:
           flow_data = json.load(f)
       
       # Load execution state
       with open("execution_state.json", "r") as f:
           job_state_data = json.load(f)
       
       # Restore flow
       flow = Flow()
       flow.deserialize(flow_data)
       
       # Restore execution state
       job_state = JobState()
       job_state.deserialize(job_state_data)
       
       print(f"Restored flow: {flow.flow_id}")
       print(f"Restored execution: {job_state.job_id}, Status: {job_state.status}")
       
       # Verify configuration
       processor_id = list(flow.routines.keys())[1]
       processor = flow.routines[processor_id]
       print(f"Processor config: multiplier={processor.get_config('multiplier')}")
       
       return flow, job_state

   def main():
       # Step 1: Save workflow structure
       save_for_distribution()
       
       # Step 2: Execute and save state
       job_state = execute_and_save_state()
       
       # Step 3: Simulate restoring on remote host
       restored_flow, restored_job_state = restore_on_remote_host()
       
       # Clean up
       for fname in ["workflow_structure.json", "execution_state.json"]:
           if os.path.exists(fname):
               os.remove(fname)

   if __name__ == "__main__":
       main()

**Expected Output**:

.. code-block:: text

   Workflow structure saved to workflow_structure.json
   Processed 10 -> Result: 20
   Execution state saved. Job ID: <job-id>
   Restored flow: distributed_workflow
   Restored execution: <job-id>, Status: completed
   Processor config: multiplier=2

**Key Points**:

- **Separate serialization**: Flow structure and execution state are separate
- **Distribution**: Send both files to remote host
- **Recovery**: Restore both on remote host
- **Resume**: If execution was paused, use ``flow.resume(job_state)`` to continue

Common Pitfalls
---------------

**Pitfall 1: Using constructor parameters**

.. code-block:: python
   :emphasize-lines: 2

   class BadRoutine(Routine):
       def __init__(self, config_value):  # ❌ Breaks serialization!
           super().__init__()
           self.config_value = config_value

**Solution**: Use ``_config`` dictionary: ``self.set_config(config_value=value)``

**Pitfall 2: Not registering custom fields**

.. code-block:: python
   :emphasize-lines: 4, 6

   class CustomRoutine(Routine):
       def __init__(self):
           super().__init__()
           self.custom_field = "value"  # Not serialized by default!
           # Need to register it
           self.add_serializable_fields(["custom_field"])

**Solution**: Register custom fields with ``add_serializable_fields()``

**Pitfall 3: Storing non-serializable objects**

.. code-block:: python
   :emphasize-lines: 3

   def __init__(self):
       super().__init__()
       self.file_handle = open("file.txt")  # Not serializable!

**Solution**: Don't store non-serializable objects. Recreate them when needed.

**Pitfall 4: Serializing Flow with execution state for distribution**

.. code-block:: python
   :emphasize-lines: 1

   flow_data = flow.serialize()  # Includes job_state by default if set
   # Sending this to another host will only include the last execution state!

**Solution**: Use ``flow.serialize(include_execution_state=False)`` for distribution.
Serialize JobState separately if you need to recover a specific execution.

**Pitfall 5: Expecting multiple execute() calls to share state**

.. code-block:: python
   :emphasize-lines: 2-3

   flow.execute(source1_id)  # Creates JobState 1
   flow.execute(source2_id)  # Creates JobState 2 (overwrites JobState 1)
   # Aggregator won't see both in the same execution!

**Solution**: Use a single ``execute()`` with multiple ``emit()`` calls, or use
the aggregation pattern (see :doc:`advanced_patterns`).

Best Practices
--------------

1. **Separate Flow and JobState serialization**:
   - Serialize Flow structure with ``flow.serialize()`` (does NOT include execution state)
   - Serialize JobState separately with ``job_state.serialize()``
   - This allows proper cross-host recovery

2. **Use _config for configuration**: All configuration should be in ``_config``
3. **No constructor parameters**: Routines must have no-argument constructors
4. **Register custom fields**: Use ``add_serializable_fields()`` for custom data
5. **Track multiple executions**: Use ``flow.get_execution(job_id)`` to access specific executions
6. **Clean up old executions**: Use ``flow.cleanup_completed_executions()`` to manage memory
7. **Test serialization**: Always test that your flows can be serialized/deserialized
8. **Version your workflows**: Include version info in flow_id or _config

Understanding Multiple Executions
-----------------------------------

**Key Design Principle**: Flow = Workflow Definition, JobState = Execution State

- **Flow**: Contains routines, connections, configuration (static structure)
- **JobState**: Contains execution state, history, pending tasks (dynamic state)
- **Multiple Executions**: Each ``execute()`` creates a new JobState with unique job_id
- **Complete Decoupling**: Flow does NOT manage JobState - they are completely separate
- **Recovery**: To recover execution, serialize both Flow and JobState separately

**Best Practice for Cross-Host Execution**:

1. **Serialize Flow structure** (no execution state - this is the default):
   .. code-block:: python

      flow_data = flow.serialize()
      # flow_data does NOT contain job_state

2. **Serialize JobState separately**:
   .. code-block:: python

      job_state_data = job_state.serialize()

3. **Send both to target host**

4. **Restore both on target host**:

   .. code-block:: python

      new_flow = Flow()
      new_flow.deserialize(flow_data)
      
      new_job_state = JobState()
      new_job_state.deserialize(job_state_data)
      
      # Resume if paused
      if new_job_state.status == "paused":
          new_flow.resume(new_job_state)

**Cross-Host Execution Example**:

See :doc:`../user_guide/serialization` for a complete cross-host execution example with network transfer and database storage patterns.

Next Steps
----------

Congratulations! You've completed the Routilux tutorial. You now understand:

- Creating routines and flows
- Connecting routines in various patterns
- Managing state and statistics
- Handling errors gracefully
- Executing workflows concurrently
- Using advanced patterns
- Serializing and persisting workflows

For more information, check out:

- :doc:`../user_guide/index` - Comprehensive user guide
- :doc:`../api_reference/index` - Complete API documentation
- :doc:`../examples/index` - Real-world examples

Happy coding with Routilux! 🚀


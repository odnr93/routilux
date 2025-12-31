State Management
=================

In this tutorial, you'll learn how to track execution state, statistics, and
monitor your workflows using Routilux's built-in state management features.

Learning Objectives
-------------------

By the end of this tutorial, you'll be able to:

- Track routine execution statistics
- Use the ``_stats`` dictionary for custom metrics
- Access JobState for execution tracking
- Use helper methods for state management
- Monitor workflow performance

Step 1: Basic Statistics Tracking
-----------------------------------

Every routine has a ``_stats`` dictionary for tracking execution metrics:

.. code-block:: python
   :linenos:

   from routilux import Flow, Routine

   class Counter(Routine):
       def __init__(self):
           super().__init__()
           self.input_slot = self.define_slot("input", handler=self.count)
       
       def count(self, value=None, **kwargs):
           # Track operations automatically
           self._track_operation("counting", success=True)
           
           # Use helper methods for stats
           self.increment_stat("total_count")
           self.set_stat("last_value", value or kwargs.get("value", "unknown"))
           
           # Direct access also works
           self._stats["custom_metric"] = self._stats.get("custom_metric", 0) + 1

   class DataSource(Routine):
       def __init__(self):
           super().__init__()
           self.trigger_slot = self.define_slot("trigger", handler=self.send)
           self.output_event = self.define_event("output", ["value"])
       
       def send(self, **kwargs):
           for i in range(3):
               self.emit("output", value=f"item_{i}")

   flow = Flow(flow_id="stats_flow")
   
   source = DataSource()
   counter = Counter()
   
   source_id = flow.add_routine(source, "source")
   counter_id = flow.add_routine(counter, "counter")
   
   flow.connect(source_id, "output", counter_id, "input")
   
   job_state = flow.execute(source_id)
   
   # Access statistics
   print(f"Counter stats: {counter.stats()}")
   print(f"Execution status: {job_state.status}")

**Expected Output**:

.. code-block:: text

   Counter stats: {'counting': {'success': 3, 'total': 3}, 'total_count': 3, 'last_value': 'item_2', 'custom_metric': 3}
   Execution status: completed

**Key Points**:

- ``_stats`` dictionary is automatically available in all routines
- ``_track_operation()`` tracks operation success/failure
- ``increment_stat()`` and ``set_stat()`` are convenient helpers
- ``stats()`` returns all statistics in a readable format

Step 2: Using Helper Methods
------------------------------

Routilux provides several helper methods for state management:

.. code-block:: python
   :linenos:

   from routilux import Flow, Routine

   class StatefulProcessor(Routine):
       def __init__(self):
           super().__init__()
           self.input_slot = self.define_slot("input", handler=self.process)
           self.output_event = self.define_event("output", ["result"])
           
           # Initialize stats
           self.set_stat("processed_count", 0)
           self.set_stat("error_count", 0)
       
       def process(self, data=None, **kwargs):
           data_value = data or kwargs.get("data", "")
           
           try:
               # Process data
               result = data_value.upper()
               
               # Track success
               self._track_operation("processing", success=True)
               self.increment_stat("processed_count")
               self.set_stat("last_processed", data_value)
               
               self.emit("output", result=result)
               
           except Exception as e:
               # Track failure
               self._track_operation("processing", success=False)
               self.increment_stat("error_count")
               self.set_stat("last_error", str(e))

   class DataSource(Routine):
       def __init__(self):
           super().__init__()
           self.trigger_slot = self.define_slot("trigger", handler=self.send)
           self.output_event = self.define_event("output", ["data"])
       
       def send(self, **kwargs):
           for item in ["hello", "world", "routilux"]:
               self.emit("output", data=item)

   flow = Flow(flow_id="helper_flow")
   
   source = DataSource()
   processor = StatefulProcessor()
   
   source_id = flow.add_routine(source, "source")
   processor_id = flow.add_routine(processor, "processor")
   
   flow.connect(source_id, "output", processor_id, "input")
   
   job_state = flow.execute(source_id)
   
   # Check stats
   stats = processor.stats()
   print(f"Processed: {processor.get_stat('processed_count', 0)}")
   print(f"Errors: {processor.get_stat('error_count', 0)}")
   print(f"Last processed: {processor.get_stat('last_processed', 'none')}")

**Expected Output**:

.. code-block:: text

   Processed: 3
   Errors: 0
   Last processed: routilux

**Available Helper Methods**:

- ``set_stat(key, value)``: Set a stat value
- ``get_stat(key, default=None)``: Get a stat value with default
- ``increment_stat(key, amount=1)``: Increment a numeric stat
- ``_track_operation(name, success=True)``: Track operation metrics
- ``stats()``: Get all statistics

**Key Points**:

- Initialize stats in ``__init__()`` if needed
- Use helper methods for type-safe operations
- ``get_stat()`` provides safe access with defaults

Step 3: Accessing JobState
---------------------------

JobState tracks overall execution state and history:

.. code-block:: python
   :linenos:

   from routilux import Flow, Routine

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

   flow = Flow(flow_id="jobstate_flow")
   
   source = DataSource()
   processor = SimpleProcessor()
   
   source_id = flow.add_routine(source, "source")
   processor_id = flow.add_routine(processor, "processor")
   
   flow.connect(source_id, "output", processor_id, "input")
   
   job_state = flow.execute(source_id)
   
   # Access JobState information
   print(f"Status: {job_state.status}")
   print(f"Flow ID: {job_state.flow_id}")
   print(f"Created at: {job_state.created_at}")
   
   # Get execution history
   history = job_state.get_execution_history()
   print(f"Execution records: {len(history)}")
   
   # Check routine states
   routine_states = job_state.get_routine_states()
   print(f"Routines executed: {len(routine_states)}")

**Expected Output**:

.. code-block:: text

   Status: completed
   Flow ID: jobstate_flow
   Created at: 2024-01-01 12:00:00
   Execution records: 2
   Routines executed: 2

**Key Points**:

- JobState tracks overall execution state
- ``status`` can be "completed", "failed", "cancelled", etc.
- Execution history records all routine executions
- Routine states track per-routine execution information

Step 4: Monitoring Performance
-------------------------------

You can track performance metrics using statistics:

.. code-block:: python
   :linenos:

   from routilux import Flow, Routine
   import time

   class TimedProcessor(Routine):
       def __init__(self):
           super().__init__()
           # Store configuration in _config (required for serialization)
           self.set_config(name="Processor")
           self.input_slot = self.define_slot("input", handler=self.process)
           self.output_event = self.define_event("output", ["result"])
           
           self.set_stat("total_time", 0.0)
           self.set_stat("call_count", 0)
       
       def process(self, data=None, **kwargs):
           data_value = data or kwargs.get("data", "")
           name = self.get_config("name", "Processor")
           
           # Measure processing time
           start_time = time.time()
           
           # Simulate processing
           time.sleep(0.1)
           result = f"{name}: {data_value.upper()}"
           
           elapsed = time.time() - start_time
           
           # Track performance
           self.increment_stat("call_count")
           self.set_stat("total_time", self.get_stat("total_time", 0.0) + elapsed)
           self.set_stat("last_processing_time", elapsed)
           
           self.emit("output", result=result)
       
       def get_average_time(self):
           count = self.get_stat("call_count", 0)
           total = self.get_stat("total_time", 0.0)
           return total / count if count > 0 else 0.0

   class DataSource(Routine):
       def __init__(self):
           super().__init__()
           self.trigger_slot = self.define_slot("trigger", handler=self.send)
           self.output_event = self.define_event("output", ["data"])
       
       def send(self, **kwargs):
           for item in ["a", "b", "c"]:
               self.emit("output", data=item)

   flow = Flow(flow_id="perf_flow")
   
   source = DataSource()
   processor = TimedProcessor()
   processor.set_config(name="Processor")
   
   source_id = flow.add_routine(source, "source")
   processor_id = flow.add_routine(processor, "processor")
   
   flow.connect(source_id, "output", processor_id, "input")
   
   job_state = flow.execute(source_id)
   
   # Check performance metrics
   print(f"Calls: {processor.get_stat('call_count', 0)}")
   print(f"Total time: {processor.get_stat('total_time', 0.0):.3f}s")
   print(f"Average time: {processor.get_average_time():.3f}s")
   print(f"Last time: {processor.get_stat('last_processing_time', 0.0):.3f}s")

**Expected Output**:

.. code-block:: text

   Calls: 3
   Total time: 0.301s
   Average time: 0.100s
   Last time: 0.100s

**Key Points**:

- Track timing information in your routines
- Calculate averages and totals for performance monitoring
- Use stats to identify bottlenecks
- Performance metrics help optimize workflows

Step 5: Complete Example - Stateful Workflow
---------------------------------------------

Here's a complete example combining state management features:

.. code-block:: python
   :name: state_management_complete
   :linenos:

   from routilux import Flow, Routine

   class DataSource(Routine):
       def __init__(self):
           super().__init__()
           self.trigger_slot = self.define_slot("trigger", handler=self.generate)
           self.output_event = self.define_event("output", ["data"])
       
       def generate(self, count=3, **kwargs):
           count = count or kwargs.get("count", 3)
           for i in range(count):
               self.emit("output", data=f"item_{i}")
               self.increment_stat("generated_count")

   class Validator(Routine):
       def __init__(self):
           super().__init__()
           self.input_slot = self.define_slot("input", handler=self.validate)
           self.output_event = self.define_event("output", ["data", "valid"])
           
           self.set_stat("valid_count", 0)
           self.set_stat("invalid_count", 0)
       
       def validate(self, data=None, **kwargs):
           data_value = data or kwargs.get("data", "")
           
           # Simple validation: must contain "item"
           is_valid = "item" in str(data_value)
           
           if is_valid:
               self.increment_stat("valid_count")
               self._track_operation("validation", success=True)
           else:
               self.increment_stat("invalid_count")
               self._track_operation("validation", success=False)
           
           self.emit("output", data=data_value, valid=is_valid)

   class Aggregator(Routine):
       def __init__(self):
           super().__init__()
           self.input_slot = self.define_slot("input", handler=self.aggregate)
           
           self.set_stat("total_received", 0)
           self.set_stat("total_valid", 0)
       
       def aggregate(self, data=None, valid=None, **kwargs):
           data_value = data or kwargs.get("data", "")
           is_valid = valid if valid is not None else kwargs.get("valid", False)
           
           self.increment_stat("total_received")
           if is_valid:
               self.increment_stat("total_valid")
           
           print(f"Aggregated: {data_value} (valid={is_valid})")

   def main():
       flow = Flow(flow_id="stateful_workflow")
       
       source = DataSource()
       validator = Validator()
       aggregator = Aggregator()
       
       source_id = flow.add_routine(source, "source")
       validator_id = flow.add_routine(validator, "validator")
       agg_id = flow.add_routine(aggregator, "aggregator")
       
       flow.connect(source_id, "output", validator_id, "input")
       flow.connect(validator_id, "output", agg_id, "input")
       
       job_state = flow.execute(source_id, entry_params={"count": 5})
       
       print("\n=== Statistics ===")
       print(f"Source generated: {source.get_stat('generated_count', 0)}")
       print(f"Validator - Valid: {validator.get_stat('valid_count', 0)}, "
             f"Invalid: {validator.get_stat('invalid_count', 0)}")
       print(f"Aggregator - Total: {aggregator.get_stat('total_received', 0)}, "
             f"Valid: {aggregator.get_stat('total_valid', 0)}")
       print(f"\nExecution status: {job_state.status}")

   if __name__ == "__main__":
       main()

**Expected Output**:

.. code-block:: text

   Aggregated: item_0 (valid=True)
   Aggregated: item_1 (valid=True)
   Aggregated: item_2 (valid=True)
   Aggregated: item_3 (valid=True)
   Aggregated: item_4 (valid=True)

   === Statistics ===
   Source generated: 5
   Validator - Valid: 5, Invalid: 0
   Aggregator - Total: 5, Valid: 5

   Execution status: completed

**Key Points**:

- Combine multiple state tracking techniques
- Track both success and failure metrics
- Use stats to understand workflow behavior
- State management helps with debugging and monitoring

Common Pitfalls
---------------

**Pitfall 1: Not initializing stats**

.. code-block:: python
   :emphasize-lines: 3

   def process(self, **kwargs):
       # Assumes stat exists
       self.increment_stat("count")  # May fail if not initialized

**Solution**: Initialize stats in ``__init__()`` or use ``get_stat()`` with defaults.

**Pitfall 2: Using wrong stat keys**

.. code-block:: python
   :emphasize-lines: 1, 4

   self.set_stat("processed_count", 0)  # Set as "processed_count"
   
   # Later...
   count = self.get_stat("process_count", 0)  # Wrong key! (missing 'ed')

**Solution**: Use consistent naming, or define constants for stat keys.

**Pitfall 3: Not tracking failures**

.. code-block:: python
   :emphasize-lines: 4

   try:
       result = process_data()
       self._track_operation("processing", success=True)
   except Exception:
       # Forgot to track failure!
       pass

**Solution**: Always track both success and failure cases.

Best Practices
--------------

1. **Initialize stats in __init__()**: Set default values for all stats you'll use
2. **Use helper methods**: Prefer ``set_stat()``, ``get_stat()``, ``increment_stat()``
3. **Track both success and failure**: Use ``_track_operation()`` for both cases
4. **Use descriptive stat names**: Make it clear what each stat represents
5. **Check stats regularly**: Monitor stats to understand workflow behavior
6. **Document stat meanings**: Comment what each stat tracks

Next Steps
----------

Now that you understand state management, let's move on to :doc:`error_handling`
to learn how to build resilient workflows that handle errors gracefully.


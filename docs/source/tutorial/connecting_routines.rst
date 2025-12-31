Connecting Routines
====================

In this tutorial, you'll learn about different connection patterns in Routilux,
including one-to-many, many-to-one, and complex branching patterns. You'll also
understand how the event queue architecture works.

Learning Objectives
-------------------

By the end of this tutorial, you'll be able to:

- Connect one event to multiple slots (fan-out)
- Connect multiple events to one slot (fan-in)
- Understand merge strategies for handling multiple inputs
- Understand the event queue execution model
- Build branching and converging workflows

Step 1: One-to-Many Connections (Fan-Out)
------------------------------------------

A single event can be connected to multiple slots. This is useful when you want
to send the same data to multiple processors:

.. code-block:: python
   :linenos:

   from routilux import Flow, Routine

   class DataSource(Routine):
       def __init__(self):
           super().__init__()
           self.trigger_slot = self.define_slot("trigger", handler=self.generate)
           self.output_event = self.define_event("output", ["data"])
       
       def generate(self, value=None, **kwargs):
           value = value or kwargs.get("value", "test")
           self.emit("output", data=value)

   class ProcessorA(Routine):
       def __init__(self):
           super().__init__()
           self.input_slot = self.define_slot("input", handler=self.process)
       
       def process(self, data=None, **kwargs):
           data_value = data or kwargs.get("data", "")
           print(f"Processor A received: {data_value}")

   class ProcessorB(Routine):
       def __init__(self):
           super().__init__()
           self.input_slot = self.define_slot("input", handler=self.process)
       
       def process(self, data=None, **kwargs):
           data_value = data or kwargs.get("data", "")
           print(f"Processor B received: {data_value}")

   # Create flow
   flow = Flow(flow_id="fanout_flow")
   
   source = DataSource()
   processor_a = ProcessorA()
   processor_b = ProcessorB()
   
   source_id = flow.add_routine(source, "source")
   a_id = flow.add_routine(processor_a, "processor_a")
   b_id = flow.add_routine(processor_b, "processor_b")
   
   # Connect one event to multiple slots
   flow.connect(source_id, "output", a_id, "input")
   flow.connect(source_id, "output", b_id, "input")
   
   # Execute
   job_state = flow.execute(source_id, entry_params={"value": "Hello"})
   print(f"Status: {job_state.status}")

**Expected Output**:

.. code-block:: text

   Processor A received: Hello
   Processor B received: Hello
   Status: completed

**Key Points**:

- One event can connect to multiple slots
- All connected slots receive the same data
- Both processors execute (order may vary due to event queue)
- This pattern is called "fan-out"

Step 2: Many-to-One Connections (Fan-In)
------------------------------------------

Multiple events can connect to the same slot. This is useful for aggregating
data from multiple sources. By default, new data replaces old data, but you can
use merge strategies to control how data is combined:

.. code-block:: python
   :linenos:

   from routilux import Flow, Routine

   class SourceA(Routine):
       def __init__(self):
           super().__init__()
           self.trigger_slot = self.define_slot("trigger", handler=self.generate)
           self.output_event = self.define_event("output", ["data", "source"])
       
       def generate(self, **kwargs):
           self.emit("output", data="Data from A", source="A")

   class SourceB(Routine):
       def __init__(self):
           super().__init__()
           self.trigger_slot = self.define_slot("trigger", handler=self.generate)
           self.output_event = self.define_event("output", ["data", "source"])
       
       def generate(self, **kwargs):
           self.emit("output", data="Data from B", source="B")

   class Aggregator(Routine):
       def __init__(self):
           super().__init__()
           # Use "append" merge strategy to accumulate data
           self.input_slot = self.define_slot(
               "input",
               handler=self.aggregate,
               merge_strategy="append"  # Accumulates data in lists
           )
       
       def aggregate(self, data=None, source=None, **kwargs):
           # With append strategy, data and source are lists (accumulated values)
           data_value = data or kwargs.get("data", [])
           source_value = source or kwargs.get("source", [])
           # Convert to string for display (if it's a list, show the last item)
           if isinstance(data_value, list) and data_value:
               data_str = data_value[-1]
           else:
               data_str = data_value
           if isinstance(source_value, list) and source_value:
               source_str = source_value[-1]
           else:
               source_str = source_value
           print(f"Aggregator received: {data_str} from {source_str}")
           
           # Access accumulated data
           all_data = self.input_slot._data
           print(f"All accumulated data: {all_data}")

   # Create flow
   flow = Flow(flow_id="fanin_flow")
   
   source_a = SourceA()
   source_b = SourceB()
   aggregator = Aggregator()
   
   a_id = flow.add_routine(source_a, "source_a")
   b_id = flow.add_routine(source_b, "source_b")
   agg_id = flow.add_routine(aggregator, "aggregator")
   
   # Connect multiple events to one slot
   flow.connect(a_id, "output", agg_id, "input")
   flow.connect(b_id, "output", agg_id, "input")
   
   # Execute both sources (they run independently)
   job_state_a = flow.execute(a_id)
   job_state_b = flow.execute(b_id)
   
   print(f"Status A: {job_state_a.status}, Status B: {job_state_b.status}")

**Expected Output**:

.. code-block:: text

   Aggregator received: Data from A from A
   All accumulated data: {'data': ['Data from A'], 'source': ['A']}
   Aggregator received: Data from B from B
   All accumulated data: {'data': ['Data from A', 'Data from B'], 'source': ['A', 'B']}
   Status A: completed, Status B: completed

**Note**: With ``merge_strategy="append"``, the handler receives lists (accumulated values).
In the first call, ``data`` and ``source`` are lists with one element each. In the second
call, they contain both values. The example above shows how to extract the latest value
for display purposes.

**Important Note**: In the current event queue architecture, each ``execute()``
call creates an independent execution with its own JobState. The aggregator in
the example above receives data from both executions, but they are separate
executions. For true aggregation within a single execution, see the aggregation
pattern in :doc:`advanced_patterns`.

**Key Points**:

- Multiple events can connect to the same slot
- Use ``merge_strategy="append"`` to accumulate data in lists
- Default strategy is "override" (new data replaces old)
- Each ``execute()`` call is independent - slot data is NOT shared between executions

Step 3: Understanding Merge Strategies
---------------------------------------

Merge strategies control how data from multiple sources is combined in a slot:

.. code-block:: python
   :linenos:

   from routilux import Flow, Routine

   class Source1(Routine):
       def __init__(self):
           super().__init__()
           self.trigger_slot = self.define_slot("trigger", handler=self.send)
           self.output_event = self.define_event("output", ["value"])
       
       def send(self, **kwargs):
           self.emit("output", value=1)

   class Source2(Routine):
       def __init__(self):
           super().__init__()
           self.trigger_slot = self.define_slot("trigger", handler=self.send)
           self.output_event = self.define_event("output", ["value"])
       
       def send(self, **kwargs):
           self.emit("output", value=2)

   class Receiver(Routine):
       def __init__(self):
           super().__init__()
           # Store strategy in _config (required for serialization)
           self.set_config(strategy="override")
           self.input_slot = self.define_slot(
               "input",
               handler=self.receive,
               merge_strategy=self.get_config("strategy", "override")
           )
       
       def receive(self, value=None, **kwargs):
           val = value or kwargs.get("value", None)
           all_data = self.input_slot._data
           print(f"Received value: {val}, All data: {all_data}")

   # Test with "override" strategy (default)
   print("=== Override Strategy ===")
   flow1 = Flow(flow_id="override_flow")
   s1 = Source1()
   s2 = Source2()
   r1 = Receiver()
   r1.set_config(strategy="override")
   # Recreate slot with correct strategy
   r1.input_slot = r1.define_slot("input", handler=r1.receive, merge_strategy="override")
   
   s1_id = flow1.add_routine(s1, "source1")
   s2_id = flow1.add_routine(s2, "source2")
   r1_id = flow1.add_routine(r1, "receiver")
   
   flow1.connect(s1_id, "output", r1_id, "input")
   flow1.connect(s2_id, "output", r1_id, "input")
   
   flow1.execute(s1_id)
   flow1.execute(s2_id)

**Expected Output**:

.. code-block:: text

   === Override Strategy ===
   Received value: 1, All data: {'value': 1}
   Received value: 2, All data: {'value': 2}

**Available Merge Strategies**:

1. **"override"** (default): New data replaces old data
2. **"append"**: Values are appended to lists (useful for aggregation)
3. **Custom function**: Define your own merge logic

**Key Points**:

- "override" is the default and most common strategy
- "append" is useful when you need to collect multiple values
- Custom merge strategies allow complex data combination logic

Step 4: Complex Branching Patterns
-----------------------------------

You can create complex workflows with branching and converging paths:

.. code-block:: python
   :linenos:

   from routilux import Flow, Routine

   class DataSource(Routine):
       def __init__(self):
           super().__init__()
           self.trigger_slot = self.define_slot("trigger", handler=self.generate)
           self.output_event = self.define_event("output", ["data"])
       
       def generate(self, value=None, **kwargs):
           value = value or kwargs.get("value", "test")
           self.emit("output", data=value)

   class Processor1(Routine):
       def __init__(self):
           super().__init__()
           # Store name in _config (required for serialization)
           self.set_config(name="UPPER")
           self.input_slot = self.define_slot("input", handler=self.process)
           self.output_event = self.define_event("output", ["result"])
       
       def process(self, data=None, **kwargs):
           data_value = data or kwargs.get("data", "")
           name = self.get_config("name", "P1")
           result = f"{name}: {data_value.upper()}"
           self.emit("output", result=result)

   class Processor2(Routine):
       def __init__(self):
           super().__init__()
           # Store name in _config (required for serialization)
           self.set_config(name="lower")
           self.input_slot = self.define_slot("input", handler=self.process)
           self.output_event = self.define_event("output", ["result"])
       
       def process(self, data=None, **kwargs):
           data_value = data or kwargs.get("data", "")
           name = self.get_config("name", "P2")
           result = f"{name}: {data_value.lower()}"
           self.emit("output", result=result)

   class Aggregator(Routine):
       def __init__(self):
           super().__init__()
           self.input_slot = self.define_slot(
               "input",
               handler=self.aggregate,
               merge_strategy="append"
           )
       
       def aggregate(self, result=None, **kwargs):
           # With append strategy, result is a list
           result_value = result or kwargs.get("result", [])
           # Extract the latest result for display
           if isinstance(result_value, list):
               for r in result_value:
                   print(f"Aggregated: {r}")
           else:
               print(f"Aggregated: {result_value}")

   # Create flow with branching pattern
   flow = Flow(flow_id="branching_flow")
   
   source = DataSource()
   proc1 = Processor1()  # Name stored in _config
   proc2 = Processor2()  # Name stored in _config
   aggregator = Aggregator()
   
   source_id = flow.add_routine(source, "source")
   p1_id = flow.add_routine(proc1, "processor1")
   p2_id = flow.add_routine(proc2, "processor2")
   agg_id = flow.add_routine(aggregator, "aggregator")
   
   # Branch: source -> processor1 and processor2
   flow.connect(source_id, "output", p1_id, "input")
   flow.connect(source_id, "output", p2_id, "input")
   
   # Converge: processor1 and processor2 -> aggregator
   flow.connect(p1_id, "output", agg_id, "input")
   flow.connect(p2_id, "output", agg_id, "input")
   
   # Execute
   job_state = flow.execute(source_id, entry_params={"value": "Hello"})
   print(f"Status: {job_state.status}")

**Expected Output**:

.. code-block:: text

   Aggregated: UPPER: HELLO
   Aggregated: lower: hello
   Status: completed

**Key Points**:

- You can create complex branching and converging patterns
- Multiple processors can run in parallel (if using concurrent execution)
- Aggregators can collect results from multiple sources
- The event queue ensures all tasks are processed

Step 5: Understanding the Event Queue Architecture
----------------------------------------------------

Routilux uses an event queue pattern for execution. Understanding this helps
you write better workflows:

.. code-block:: python
   :linenos:

   from routilux import Flow, Routine
   import time

   class SlowProcessor(Routine):
       def __init__(self):
           super().__init__()
           # Store configuration in _config (required for serialization)
           self.set_config(name="Slow", delay=0.1)
           self.input_slot = self.define_slot("input", handler=self.process)
           self.output_event = self.define_event("output", ["result"])
       
       def process(self, data=None, **kwargs):
           data_value = data or kwargs.get("data", "")
           delay = self.get_config("delay", 0.1)
           name = self.get_config("name", "Slow")
           time.sleep(delay)  # Simulate slow processing
           result = f"{name} processed: {data_value}"
           print(f"[{time.time():.2f}] {result}")
           self.emit("output", result=result)

   class FastProcessor(Routine):
       def __init__(self):
           super().__init__()
           # Store configuration in _config (required for serialization)
           self.set_config(name="Fast")
           self.input_slot = self.define_slot("input", handler=self.process)
       
       def process(self, result=None, **kwargs):
           result_value = result or kwargs.get("result", "")
           name = self.get_config("name", "Fast")
           print(f"[{time.time():.2f}] {name} received: {result_value}")

   # Create flow
   flow = Flow(flow_id="queue_demo")
   
   slow = SlowProcessor()
   slow.set_config(name="Slow", delay=0.2)
   fast = FastProcessor()
   fast.set_config(name="Fast")
   
   slow_id = flow.add_routine(slow, "slow")
   fast_id = flow.add_routine(fast, "fast")
   
   flow.connect(slow_id, "output", fast_id, "input")
   
   # Execute
   print("Starting execution...")
   job_state = flow.execute(slow_id, entry_params={"data": "test"})
   print(f"Status: {job_state.status}")

**Expected Output** (timing may vary):

.. code-block:: text

   Starting execution...
   [1234567890.12] Slow processed: test
   [1234567890.32] Fast received: Slow processed: test
   Status: completed

**Key Points**:

- ``emit()`` is non-blocking - it returns immediately after enqueuing tasks
- Tasks are processed in queue order (fair scheduling)
- The event queue ensures all tasks complete before execution finishes
- This architecture supports both sequential and concurrent execution modes

Common Pitfalls
---------------

**Pitfall 1: Expecting data to be shared between execute() calls**

.. code-block:: python
   :emphasize-lines: 2-3

   # Wrong: Each execute() creates a new JobState
   flow.execute(source1_id)  # Creates JobState 1
   flow.execute(source2_id)  # Creates JobState 2
   # Aggregator won't see both messages in the same execution!

**Solution**: Use a single ``execute()`` with multiple ``emit()`` calls from
the same routine, or use the aggregation pattern (see :doc:`advanced_patterns`).

**Pitfall 2: Using wrong merge strategy**

.. code-block:: python
   :emphasize-lines: 2

   # Wrong: Using "override" when you need to accumulate
   self.input_slot = self.define_slot("input", handler=self.aggregate)
   # Later data will overwrite earlier data!

**Solution**: Use ``merge_strategy="append"`` when you need to collect multiple
values.

**Pitfall 3: Not understanding event queue order**

.. code-block:: python
   :emphasize-lines: 3

   # Don't assume depth-first execution order
   # Tasks are processed in queue order, not call-stack order
   self.emit("event1", data="A")
   self.emit("event2", data="B")
   # Order may vary depending on queue processing

**Solution**: Don't rely on execution order unless using sequential mode with
single worker. Use explicit synchronization if order matters.

Best Practices
--------------

1. **Use descriptive connection patterns**: Make your workflow structure clear
2. **Choose appropriate merge strategies**: "override" for replacement, "append" for accumulation
3. **Understand event queue behavior**: Tasks are processed fairly, not depth-first
4. **Test with different execution modes**: Sequential vs concurrent may behave differently
5. **Use aggregation patterns for collecting data**: See :doc:`advanced_patterns` for proper patterns

Next Steps
----------

Now that you understand connections, let's move on to :doc:`data_flow` to learn
about parameter mapping, data extraction, and how data flows through your
workflows.


Concurrent Execution
=====================

In this tutorial, you'll learn how to execute independent routines in parallel
using Routilux's concurrent execution mode for better performance.

Learning Objectives
-------------------

By the end of this tutorial, you'll be able to:

- Understand when to use concurrent execution
- Configure concurrent execution mode
- Handle thread-safe operations
- Use wait_for_completion() and shutdown()
- Build high-performance workflows

Step 1: Understanding Concurrent Execution
------------------------------------------

Concurrent execution allows independent routines to run in parallel, which is
especially useful for I/O-bound operations (network calls, file I/O, etc.):

.. code-block:: python
   :linenos:

   from routilux import Flow, Routine
   import time

   class SlowIOOperation(Routine):
       def __init__(self):
           super().__init__()
           # Store configuration in _config (required for serialization)
           self.set_config(name="Operation", delay=0.2)
           self.trigger_slot = self.define_slot("trigger", handler=self.operate)
           self.output_event = self.define_event("output", ["result"])
       
       def operate(self, **kwargs):
           # Simulate I/O operation (network call, file read, etc.)
           delay = self.get_config("delay", 0.2)
           name = self.get_config("name", "Operation")
           time.sleep(delay)
           result = f"{name} completed"
           print(f"[{time.time():.2f}] {result}")
           self.emit("output", result=result)

   # Sequential execution (default)
   print("=== Sequential Execution ===")
   flow_seq = Flow(flow_id="sequential", execution_strategy="sequential")
   
   op1 = SlowIOOperation()
   op1.set_config(name="Operation1", delay=0.2)
   op2 = SlowIOOperation()
   op2.set_config(name="Operation2", delay=0.2)
   op3 = SlowIOOperation()
   op3.set_config(name="Operation3", delay=0.2)
   
   op1_id = flow_seq.add_routine(op1, "op1")
   op2_id = flow_seq.add_routine(op2, "op2")
   op3_id = flow_seq.add_routine(op3, "op3")
   
   start = time.time()
   flow_seq.execute(op1_id)
   flow_seq.execute(op2_id)
   flow_seq.execute(op3_id)
   elapsed = time.time() - start
   print(f"Sequential time: {elapsed:.2f}s")

**Expected Output**:

.. code-block:: text

   === Sequential Execution ===
   [1234567890.12] Operation1 completed
   [1234567890.32] Operation2 completed
   [1234567890.52] Operation3 completed
   Sequential time: 0.60s

**Key Points**:

- Sequential mode executes one routine at a time
- Total time is sum of all operation times
- Suitable for CPU-bound or dependent operations

Step 2: Enabling Concurrent Execution
-------------------------------------

Enable concurrent execution by setting the execution strategy:

.. code-block:: python
   :linenos:

   from routilux import Flow, Routine
   import time

   class SlowIOOperation(Routine):
       def __init__(self):
           super().__init__()
           # Store configuration in _config (required for serialization)
           self.set_config(name="Operation", delay=0.2)
           self.trigger_slot = self.define_slot("trigger", handler=self.operate)
           self.output_event = self.define_event("output", ["result"])
       
       def operate(self, **kwargs):
           delay = self.get_config("delay", 0.2)
           name = self.get_config("name", "Operation")
           time.sleep(delay)
           result = f"{name} completed"
           print(f"[{time.time():.2f}] {result}")
           self.emit("output", result=result)

   # Concurrent execution
   print("=== Concurrent Execution ===")
   flow_conc = Flow(
       flow_id="concurrent",
       execution_strategy="concurrent",
       max_workers=3  # Number of parallel workers
   )
   
   op1 = SlowIOOperation()
   op1.set_config(name="Operation1", delay=0.2)
   op2 = SlowIOOperation()
   op2.set_config(name="Operation2", delay=0.2)
   op3 = SlowIOOperation()
   op3.set_config(name="Operation3", delay=0.2)
   
   op1_id = flow_conc.add_routine(op1, "op1")
   op2_id = flow_conc.add_routine(op2, "op2")
   op3_id = flow_conc.add_routine(op3, "op3")
   
   start = time.time()
   flow_conc.execute(op1_id)
   flow_conc.execute(op2_id)
   flow_conc.execute(op3_id)
   
   # Wait for all concurrent tasks to complete
   flow_conc.wait_for_completion(timeout=5.0)
   elapsed = time.time() - start
   print(f"Concurrent time: {elapsed:.2f}s")
   
   # Always clean up
   flow_conc.shutdown(wait=True)

**Expected Output**:

.. code-block:: text

   === Concurrent Execution ===
   [1234567890.12] Operation1 completed
   [1234567890.12] Operation2 completed
   [1234567890.12] Operation3 completed
   Concurrent time: 0.22s

**Key Points**:

- Concurrent mode runs multiple routines in parallel
- Total time is approximately the longest operation time
- Use ``wait_for_completion()`` to wait for all tasks
- Always call ``shutdown()`` to clean up thread pool

Step 3: Concurrent Execution in a Flow
---------------------------------------

In a connected flow, independent routines can execute concurrently:

.. code-block:: python
   :linenos:

   from routilux import Flow, Routine
   import time

   class DataFetcher(Routine):
       def __init__(self):
           super().__init__()
           # Store configuration in _config (required for serialization)
           self.set_config(source_name="Source", delay=0.1)
           self.trigger_slot = self.define_slot("trigger", handler=self.fetch)
           self.output_event = self.define_event("output", ["data", "source"])
       
       def fetch(self, **kwargs):
           delay = self.get_config("delay", 0.1)
           source_name = self.get_config("source_name", "Source")
           time.sleep(delay)  # Simulate network delay
           data = f"Data from {source_name}"
           print(f"[{time.time():.2f}] Fetched: {data}")
           self.emit("output", data=data, source=source_name)

   class Aggregator(Routine):
       def __init__(self):
           super().__init__()
           self.input_slot = self.define_slot(
               "input",
               handler=self.aggregate,
               merge_strategy="append"
           )
       
       def aggregate(self, data=None, source=None, **kwargs):
           data_value = data or kwargs.get("data", "")
           source_value = source or kwargs.get("source", "")
           print(f"Aggregated: {data_value} from {source_value}")

   # Create concurrent flow
   flow = Flow(
       flow_id="concurrent_flow",
       execution_strategy="concurrent",
       max_workers=3
   )
   
   # Create multiple fetchers
   fetcher1 = DataFetcher()
   fetcher1.set_config(source_name="Source1", delay=0.1)
   fetcher2 = DataFetcher()
   fetcher2.set_config(source_name="Source2", delay=0.1)
   fetcher3 = DataFetcher()
   fetcher3.set_config(source_name="Source3", delay=0.1)
   aggregator = Aggregator()
   
   f1_id = flow.add_routine(fetcher1, "fetcher1")
   f2_id = flow.add_routine(fetcher2, "fetcher2")
   f3_id = flow.add_routine(fetcher3, "fetcher3")
   agg_id = flow.add_routine(aggregator, "aggregator")
   
   # Connect all fetchers to aggregator
   flow.connect(f1_id, "output", agg_id, "input")
   flow.connect(f2_id, "output", agg_id, "input")
   flow.connect(f3_id, "output", agg_id, "input")
   
   # Execute all fetchers (they run concurrently)
   start = time.time()
   flow.execute(f1_id)
   flow.execute(f2_id)
   flow.execute(f3_id)
   
   flow.wait_for_completion(timeout=5.0)
   elapsed = time.time() - start
   print(f"Total time: {elapsed:.2f}s")
   
   flow.shutdown(wait=True)

**Expected Output**:

.. code-block:: text

   [1234567890.12] Fetched: Data from Source1
   [1234567890.12] Fetched: Data from Source2
   [1234567890.12] Fetched: Data from Source3
   Aggregated: Data from Source1 from Source1
   Aggregated: Data from Source2 from Source2
   Aggregated: Data from Source3 from Source3
   Total time: 0.12s

**Key Points**:

- Independent routines in a flow can execute concurrently
- Dependencies are automatically handled (aggregator waits for fetchers)
- Use merge_strategy="append" to collect results from multiple sources
- Concurrent execution significantly improves performance for I/O-bound operations

Step 4: Thread Safety Considerations
-------------------------------------

When using concurrent execution, ensure thread-safe operations:

.. code-block:: python
   :linenos:

   from routilux import Flow, Routine
   import threading
   import time

   class ThreadSafeCounter(Routine):
       def __init__(self):
           super().__init__()
           self.input_slot = self.define_slot("input", handler=self.increment)
           self._lock = threading.Lock()  # Thread lock for safety
           self.set_stat("count", 0)
       
       def increment(self, **kwargs):
           # Thread-safe increment
           with self._lock:
               current = self.get_stat("count", 0)
               self.set_stat("count", current + 1)
               print(f"Count: {self.get_stat('count', 0)}")

   class DataSource(Routine):
       def __init__(self):
           super().__init__()
           # Store configuration in _config (required for serialization)
           self.set_config(name="Source")
           self.trigger_slot = self.define_slot("trigger", handler=self.send)
           self.output_event = self.define_event("output", ["data"])
       
       def send(self, **kwargs):
           name = self.get_config("name", "Source")
           time.sleep(0.05)  # Simulate processing
           self.emit("output", data=f"Data from {name}")

   flow = Flow(
       flow_id="threadsafe_flow",
       execution_strategy="concurrent",
       max_workers=5
   )
   
   counter = ThreadSafeCounter()
   counter_id = flow.add_routine(counter, "counter")
   
   # Create multiple sources
   sources = []
   source_ids = []
   for i in range(5):
       source = DataSource()
       source.set_config(name=f"Source{i}")
       sources.append(source)
       source_id = flow.add_routine(source, f"source{i}")
       source_ids.append(source_id)
       flow.connect(source_id, "output", counter_id, "input")
   
   # Execute all sources concurrently
   for source_id in source_ids:
       flow.execute(source_id)
   
   flow.wait_for_completion(timeout=5.0)
   print(f"Final count: {counter.get_stat('count', 0)}")
   
   flow.shutdown(wait=True)

**Expected Output**:

.. code-block:: text

   Count: 1
   Count: 2
   Count: 3
   Count: 4
   Count: 5
   Final count: 5

**Key Points**:

- Use locks (``threading.Lock()``) for shared state modifications
- Routilux's internal state management is thread-safe
- Be careful with shared resources (files, databases, etc.)
- Test concurrent workflows thoroughly

Step 5: Complete Example - Parallel Data Processing
-----------------------------------------------------

Here's a complete example of parallel data processing:

.. code-block:: python
   :name: concurrent_execution_complete
   :linenos:

   from routilux import Flow, Routine
   import time

   class DataFetcher(Routine):
       def __init__(self):
           super().__init__()
           # Store configuration in _config (required for serialization)
           self.set_config(source_id="F0", delay=0.1)
           self.trigger_slot = self.define_slot("trigger", handler=self.fetch)
           self.output_event = self.define_event("output", ["data", "source_id", "timestamp"])
       
       def fetch(self, **kwargs):
           delay = self.get_config("delay", 0.1)
           source_id = self.get_config("source_id", "F0")
           time.sleep(delay)
           timestamp = time.time()
           data = f"Data from source {source_id}"
           self.emit("output", data=data, source_id=source_id, timestamp=timestamp)

   class DataProcessor(Routine):
       def __init__(self):
           super().__init__()
           self.input_slot = self.define_slot("input", handler=self.process)
           self.output_event = self.define_event("output", ["processed", "source_id"])
       
       def process(self, data=None, source_id=None, timestamp=None, **kwargs):
           data_value = data or kwargs.get("data", "")
           source = source_id or kwargs.get("source_id", "unknown")
           
           # Process data
           processed = f"Processed: {data_value}"
           print(f"Processed data from source {source}")
           
           self.emit("output", processed=processed, source_id=source)

   class ResultCollector(Routine):
       def __init__(self):
           super().__init__()
           self.input_slot = self.define_slot(
               "input",
               handler=self.collect,
               merge_strategy="append"
           )
           self.set_stat("collected_count", 0)
       
       def collect(self, processed=None, source_id=None, **kwargs):
           processed_value = processed or kwargs.get("processed", "")
           source = source_id or kwargs.get("source_id", "unknown")
           
           self.increment_stat("collected_count")
           print(f"Collected: {processed_value} from {source}")

   def main():
       flow = Flow(
           flow_id="parallel_processing",
           execution_strategy="concurrent",
           max_workers=5
       )
       
       # Create multiple fetchers
       fetchers = []
       fetcher_ids = []
       for i in range(5):
           fetcher = DataFetcher()
           fetcher.set_config(source_id=f"F{i}", delay=0.1)
           fetchers.append(fetcher)
           fetcher_id = flow.add_routine(fetcher, f"fetcher{i}")
           fetcher_ids.append(fetcher_id)
       
       processor = DataProcessor()
       collector = ResultCollector()
       
       processor_id = flow.add_routine(processor, "processor")
       collector_id = flow.add_routine(collector, "collector")
       
       # Connect: fetchers -> processor -> collector
       for fetcher_id in fetcher_ids:
           flow.connect(fetcher_id, "output", processor_id, "input")
       
       flow.connect(processor_id, "output", collector_id, "input")
       
       # Execute all fetchers concurrently
       print("Starting parallel data fetching...")
       start = time.time()
       
       for fetcher_id in fetcher_ids:
           flow.execute(fetcher_id)
       
       flow.wait_for_completion(timeout=10.0)
       elapsed = time.time() - start
       
       print(f"\nCompleted in {elapsed:.2f}s")
       print(f"Collected {collector.get_stat('collected_count', 0)} results")
       
       flow.shutdown(wait=True)

   if __name__ == "__main__":
       main()

**Expected Output**:

.. code-block:: text

   Starting parallel data fetching...
   Processed data from source F0
   Processed data from source F1
   Processed data from source F2
   Processed data from source F3
   Processed data from source F4
   Collected: Processed: Data from source F0 from F0
   Collected: Processed: Data from source F1 from F1
   Collected: Processed: Data from source F2 from F2
   Collected: Processed: Data from source F3 from F3
   Collected: Processed: Data from source F4 from F4

   Completed in 0.15s
   Collected 5 results

**Key Points**:

- Concurrent execution significantly improves performance for I/O-bound operations
- Independent routines can run in parallel
- Always use ``wait_for_completion()`` and ``shutdown()``
- Use appropriate max_workers based on your workload

Common Pitfalls
---------------

**Pitfall 1: Forgetting to wait for completion**

.. code-block:: python
   :emphasize-lines: 3

   flow.execute(routine_id)
   # Missing wait_for_completion()!
   # Tasks may not be finished yet

**Solution**: Always call ``wait_for_completion()`` after executing concurrent flows.

**Pitfall 2: Not shutting down thread pool**

.. code-block:: python
   :emphasize-lines: 3

   flow.execute(routine_id)
   flow.wait_for_completion()
   # Missing shutdown()!
   # Thread pool resources not released

**Solution**: Always call ``shutdown(wait=True)`` to clean up resources.

**Pitfall 3: Using concurrent mode for CPU-bound operations**

.. code-block:: python
   :emphasize-lines: 2

   # CPU-bound operations don't benefit from concurrent mode
   # (Python's GIL limits true parallelism)
   flow = Flow(execution_strategy="concurrent")  # May not help

**Solution**: Use concurrent mode for I/O-bound operations, sequential for CPU-bound.

Best Practices
--------------

1. **Use concurrent mode for I/O-bound operations**: Network calls, file I/O, database queries
2. **Use sequential mode for CPU-bound operations**: Heavy computation, data processing
3. **Set appropriate max_workers**: Match your workload (typically 3-10)
4. **Always wait for completion**: Use ``wait_for_completion()`` after execution
5. **Always shutdown**: Call ``shutdown(wait=True)`` to clean up resources
6. **Ensure thread safety**: Use locks for shared state modifications
7. **Test thoroughly**: Concurrent execution can reveal race conditions

Next Steps
----------

Now that you understand concurrent execution, let's move on to :doc:`advanced_patterns`
to learn about aggregation patterns, conditional routing, and other advanced features.


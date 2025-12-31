Getting Started
================

In this first tutorial, you'll learn the basics of Routilux by creating a simple
routine and connecting it in a flow. By the end, you'll understand the core
concepts of routines, slots, events, and flows.

Learning Objectives
-------------------

By the end of this tutorial, you'll be able to:

- Create a custom routine with slots and events
- Define slot handlers to process incoming data
- Emit events to send data to other routines
- Create a flow and add routines to it
- Connect routines together
- Execute a flow and check results

Step 1: Understanding Routines, Slots, and Events
--------------------------------------------------

Routilux is built around three core concepts:

- **Routine**: A unit of work that processes data
- **Slot**: An input mechanism that receives data (think of it as a "receiver")
- **Event**: An output mechanism that sends data (think of it as a "sender")

Let's create a simple routine that receives data through a slot and emits it
through an event:

.. code-block:: python
   :linenos:

   from routilux import Routine

   class Greeter(Routine):
       """A simple routine that greets someone"""
       
       def __init__(self):
           super().__init__()
           # Define an input slot with a handler function
           self.input_slot = self.define_slot("input", handler=self.greet)
           # Define an output event
           self.output_event = self.define_event("output", ["message"])
       
       def greet(self, name=None, **kwargs):
           """Handle incoming data and emit a greeting"""
           # Extract the name from kwargs if not provided directly
           name = name or kwargs.get("name", "World")
           
           # Create a greeting message
           message = f"Hello, {name}!"
           
           # Emit the message through the output event
           # Flow is automatically detected from routine context
           self.emit("output", message=message)

**Key Points**:

- All routines inherit from ``Routine`` base class
- Slots are defined with ``define_slot()`` and require a handler function
- Events are defined with ``define_event()`` and specify parameter names
- The handler function receives data through keyword arguments
- ``emit()`` automatically detects the flow from routine context (no need to pass flow parameter)

Step 2: Creating Your First Flow
---------------------------------

A Flow is a container that manages multiple routines and their connections.
Let's create a flow and add our Greeter routine:

.. code-block:: python
   :linenos:

   from routilux import Flow

   # Create a flow
   flow = Flow(flow_id="greeting_flow")
   
   # Create a routine instance
   greeter = Greeter()
   
   # Add the routine to the flow
   greeter_id = flow.add_routine(greeter, "greeter")
   
   print(f"Added routine with ID: {greeter_id}")

**Expected Output**:

.. code-block:: text

   Added routine with ID: <some-uuid>

**Key Points**:

- Each flow has a unique ``flow_id`` (auto-generated if not provided)
- Routines are added to flows with ``add_routine()`` which returns a routine ID
- The routine ID is used to reference the routine when making connections

Step 3: Executing a Flow
-------------------------

To execute a flow, we need to call ``execute()`` on an entry routine. An entry
routine is one that has a slot we can trigger directly. Let's execute our flow:

.. code-block:: python
   :linenos:

   from routilux import Flow, Routine

   class Greeter(Routine):
       def __init__(self):
           super().__init__()
           # Use "trigger" as the slot name for entry routines
           self.trigger_slot = self.define_slot("trigger", handler=self.greet)
           self.output_event = self.define_event("output", ["message"])
       
       def greet(self, name=None, **kwargs):
           name = name or kwargs.get("name", "World")
           message = f"Hello, {name}!"
           self.emit("output", message=message)

   # Create and execute flow
   flow = Flow(flow_id="greeting_flow")
   greeter = Greeter()
   greeter_id = flow.add_routine(greeter, "greeter")
   
   # Execute the flow with entry parameters
   job_state = flow.execute(greeter_id, entry_params={"name": "Routilux"})
   
   # Check execution status
   print(f"Execution status: {job_state.status}")

**Expected Output**:

.. code-block:: text

   Execution status: completed

**Key Points**:

- ``execute()`` takes a routine ID and optional ``entry_params``
- Entry parameters are passed to the entry routine's slot handler
- ``execute()`` returns a ``JobState`` object that tracks execution status
- The status will be "completed" if execution succeeds

Step 4: Connecting Two Routines
---------------------------------

Now let's create two routines and connect them. The first routine will send data
to the second:

.. code-block:: python
   :linenos:

   from routilux import Flow, Routine

   class DataSource(Routine):
       """A routine that generates data"""
       
       def __init__(self):
           super().__init__()
           self.trigger_slot = self.define_slot("trigger", handler=self.generate)
           self.output_event = self.define_event("output", ["data"])
       
       def generate(self, value=None, **kwargs):
           value = value or kwargs.get("value", "default")
           self.emit("output", data=value)

   class DataProcessor(Routine):
       """A routine that processes data"""
       
       def __init__(self):
           super().__init__()
           self.input_slot = self.define_slot("input", handler=self.process)
           self.output_event = self.define_event("output", ["result"])
       
       def process(self, data=None, **kwargs):
           # Extract data from kwargs
           data_value = data or kwargs.get("data", "no data")
           result = f"Processed: {data_value}"
           self.emit("output", result=result)
           print(f"Processor received: {data_value}, produced: {result}")

   # Create flow
   flow = Flow(flow_id="data_flow")
   
   # Create routines
   source = DataSource()
   processor = DataProcessor()
   
   # Add to flow
   source_id = flow.add_routine(source, "source")
   processor_id = flow.add_routine(processor, "processor")
   
   # Connect: source's output event -> processor's input slot
   flow.connect(source_id, "output", processor_id, "input")
   
   # Execute from source
   job_state = flow.execute(source_id, entry_params={"value": "Hello"})
   
   print(f"Status: {job_state.status}")

**Expected Output**:

.. code-block:: text

   Processor received: Hello, produced: Processed: Hello
   Status: completed

**Key Points**:

- ``connect()`` links an event from one routine to a slot in another
- The connection format is: ``flow.connect(source_id, "event_name", target_id, "slot_name")``
- When the source emits an event, connected slots automatically receive the data
- Data flows automatically through connections

Step 5: Complete Example - A Simple Pipeline
----------------------------------------------

Let's create a complete example with three routines connected in a pipeline:

.. code-block:: python
   :name: getting_started_complete
   :linenos:

   from routilux import Flow, Routine

   class DataSource(Routine):
       """Generate data"""
       
       def __init__(self):
           super().__init__()
           self.trigger_slot = self.define_slot("trigger", handler=self.generate)
           self.output_event = self.define_event("output", ["data"])
       
       def generate(self, text=None, **kwargs):
           text = text or kwargs.get("text", "default")
           self.emit("output", data=text)

   class Transformer(Routine):
       """Transform data to uppercase"""
       
       def __init__(self):
           super().__init__()
           self.input_slot = self.define_slot("input", handler=self.transform)
           self.output_event = self.define_event("output", ["transformed"])
       
       def transform(self, data=None, **kwargs):
           data_value = data or kwargs.get("data", "")
           transformed = data_value.upper()
           self.emit("output", transformed=transformed)

   class Printer(Routine):
       """Print the final result"""
       
       def __init__(self):
           super().__init__()
           self.input_slot = self.define_slot("input", handler=self.print_result)
       
       def print_result(self, transformed=None, **kwargs):
           result = transformed or kwargs.get("transformed", "")
           print(f"Final result: {result}")

   def main():
       # Create flow
       flow = Flow(flow_id="pipeline")
       
       # Create routines
       source = DataSource()
       transformer = Transformer()
       printer = Printer()
       
       # Add to flow
       source_id = flow.add_routine(source, "source")
       transformer_id = flow.add_routine(transformer, "transformer")
       printer_id = flow.add_routine(printer, "printer")
       
       # Connect: source -> transformer -> printer
       flow.connect(source_id, "output", transformer_id, "input")
       flow.connect(transformer_id, "output", printer_id, "input")
       
       # Execute
       print("Executing pipeline...")
       job_state = flow.execute(source_id, entry_params={"text": "hello, routilux!"})
       
       print(f"Pipeline status: {job_state.status}")

   if __name__ == "__main__":
       main()

**Expected Output**:

.. code-block:: text

   Executing pipeline...
   Final result: HELLO, ROUTILUX!
   Pipeline status: completed

**Key Points**:

- Routines can be connected in chains (pipelines)
- Data flows automatically from one routine to the next
- Each routine processes data and passes it along
- The flow executes all connected routines automatically

Common Pitfalls
---------------

**Pitfall 1: Forgetting to call super().__init__()**

.. code-block:: python
   :emphasize-lines: 4

   class MyRoutine(Routine):
       def __init__(self):
           # Missing super().__init__()!
           self.input_slot = self.define_slot("input", handler=self.process)
           # This will fail because _slots and _events are not initialized

**Solution**: Always call ``super().__init__()`` first in your ``__init__`` method.

**Pitfall 2: Not defining events before emitting**

.. code-block:: python
   :emphasize-lines: 6

   class MyRoutine(Routine):
       def __init__(self):
           super().__init__()
           self.input_slot = self.define_slot("input", handler=self.process)
           # Forgot to define the event!
       
       def process(self, **kwargs):
           self.emit("output", data="value")  # Error: event not defined!

**Solution**: Always define events with ``define_event()`` before using them in ``emit()``.

**Pitfall 3: Wrong parameter names in emit()**

.. code-block:: python
   :emphasize-lines: 4, 7

   class MyRoutine(Routine):
       def __init__(self):
           super().__init__()
           self.output_event = self.define_event("output", ["message"])  # Defined as "message"
       
       def process(self, **kwargs):
           self.emit("output", msg="Hello")  # Wrong parameter name "msg"!

**Solution**: Use the exact parameter names specified in ``define_event()``. In this case, use ``message="Hello"``.

**Pitfall 4: Not handling data extraction properly**

.. code-block:: python
   :emphasize-lines: 1

   def process(self, data, **kwargs):
       # This assumes 'data' is always provided as a positional argument
       # But it might come as a keyword argument instead
       result = f"Processed: {data}"

**Solution**: Use the pattern ``data = data or kwargs.get("data", default_value)`` to handle both cases.

Best Practices
--------------

1. **Use descriptive names**: Choose clear names for routines, slots, and events
2. **Define events with parameter names**: Always specify parameter names in ``define_event()``
3. **Handle data extraction flexibly**: Use ``data or kwargs.get("data", default)`` pattern
4. **Use "trigger" for entry slots**: Convention for slots that start execution
5. **Print or log in handlers**: Helps with debugging during development
6. **Check job_state.status**: Always verify execution completed successfully

Next Steps
----------

Now that you understand the basics, let's move on to :doc:`connecting_routines`
to learn about more complex connection patterns, multiple connections, and
understanding the event queue architecture.


Quick Start Guide
=================

This guide will help you get started with flowforge quickly.

Basic Concepts
--------------

* **Routine**: A unit of work that can receive input through slots and emit output through events
* **Flow**: A manager that orchestrates multiple routines and their connections
* **Event**: An output mechanism that can be connected to slots
* **Slot**: An input mechanism that can receive data from events
* **Connection**: A link between an event and a slot

Creating Your First Routine
----------------------------

Let's create a simple routine that processes data:

.. code-block:: python

   from flowforge import Routine

   class DataProcessor(Routine):
       def __init__(self):
           super().__init__()
           # Define an input slot
           self.input_slot = self.define_slot("input", handler=self.process_data)
           # Define an output event
           self.output_event = self.define_event("output", ["result"])
       
       def process_data(self, data: str):
           # Process the data
           result = f"Processed: {data}"
           # Update statistics
           self._stats["processed_count"] = self._stats.get("processed_count", 0) + 1
           # Emit the result
           self.emit("output", result=result)

Creating a Flow
---------------

Now let's create a flow and connect routines:

.. code-block:: python

   from flowforge import Flow

   # Create a flow
   flow = Flow(flow_id="my_flow")
   
   # Create routine instances
   processor1 = DataProcessor()
   processor2 = DataProcessor()
   
   # Add routines to the flow
   id1 = flow.add_routine(processor1, "processor1")
   id2 = flow.add_routine(processor2, "processor2")
   
   # Connect processor1's output to processor2's input
   flow.connect(id1, "output", id2, "input")

Executing a Flow
----------------

Execute the flow with entry parameters:

.. code-block:: python

   # Execute the flow
   job_state = flow.execute(id1, entry_params={"data": "test"})
   
   # Check the status
   print(job_state.status)  # "completed"
   
   # Check statistics
   print(processor1.stats())  # {"processed_count": 1}

Next Steps
----------

* Read the :doc:`user_guide/index` for detailed usage
* Check out :doc:`examples/index` for more examples
* See :doc:`api_reference/index` for API documentation


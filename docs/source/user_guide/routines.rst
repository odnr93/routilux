Working with Routines
=====================

Routines are the core building blocks of flowforge. This guide explains how to create and use routines.

Creating a Routine
------------------

To create a routine, inherit from ``Routine2``:

.. code-block:: python

   from flowforge import Routine2

   class MyRoutine(Routine2):
       def __init__(self):
           super().__init__()
           # Define slots and events here

Defining Slots
--------------

Slots are input mechanisms for routines. Define a slot with a handler function:

.. code-block:: python

   def process_input(self, data):
       # Process the input data
       pass

   self.input_slot = self.define_slot("input", handler=process_input)

You can also specify a merge strategy for slots that receive data from multiple events:

.. code-block:: python

   self.input_slot = self.define_slot(
       "input",
       handler=process_input,
       merge_strategy="append"  # or "override", "merge"
   )

Defining Events
---------------

Events are output mechanisms for routines. Define an event with output parameters:

.. code-block:: python

   self.output_event = self.define_event("output", ["result", "status"])

Emitting Events
--------------

Emit events to trigger connected slots:

.. code-block:: python

   self.emit("output", result="success", status="completed")

When emitting, you can optionally pass a Flow instance for context:

.. code-block:: python

   self.emit("output", flow=current_flow, result="success")

Statistics
----------

Track routine statistics using the ``_stats`` dictionary:

.. code-block:: python

   self._stats["processed_count"] = self._stats.get("processed_count", 0) + 1

Retrieve statistics:

.. code-block:: python

   stats = routine.stats()
   print(stats)  # {"processed_count": 1, ...}

Getting Slots and Events
------------------------

Retrieve slots and events by name:

.. code-block:: python

   slot = routine.get_slot("input")
   event = routine.get_event("output")

Executing Routines
------------------

Routines are executed by calling them:

.. code-block:: python

   routine(data="test")

Or through a Flow's execute method (see :doc:`flows`).


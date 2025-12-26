Working with Connections
========================

Connections link events to slots, enabling data flow between routines.

Creating Connections
--------------------

Connections are typically created through Flow's connect method:

.. code-block:: python

   connection = flow.connect(
       source_routine_id="routine1",
       source_event="output",
       target_routine_id="routine2",
       target_slot="input"
   )

You can also create connections directly:

.. code-block:: python

   from flowforge import Connection

   connection = Connection(event, slot, param_mapping={"param1": "param2"})

Parameter Mapping
-----------------

Parameter mapping allows you to transform parameter names when data flows through a connection:

.. code-block:: python

   # Source event emits "source_param"
   event = routine1.define_event("output", ["source_param"])
   
   # Target slot expects "target_param"
   slot = routine2.define_slot("input", handler=lambda target_param: ...)
   
   # Map source_param to target_param
   connection = Connection(
       event, slot,
       param_mapping={"source_param": "target_param"}
   )

Activating Connections
---------------------

Connections are automatically activated when events are emitted. You can also activate them manually:

.. code-block:: python

   connection.activate({"data": "test"})

Disconnecting
-------------

Disconnect an event from a slot:

.. code-block:: python

   connection.disconnect()

Or disconnect through the event or slot:

.. code-block:: python

   event.disconnect(slot)
   slot.disconnect(event)


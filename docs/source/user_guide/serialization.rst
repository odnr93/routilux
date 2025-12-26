Serialization
=============

flowforge provides full serialization support for persistence and state recovery.

Serializing Objects
-------------------

All core classes support serialization:

.. code-block:: python

   # Serialize a flow
   data = flow.serialize()
   
   # Serialize a routine
   data = routine.serialize()
   
   # Serialize a job state
   data = job_state.serialize()

Deserializing Objects
---------------------

Deserialize objects:

.. code-block:: python

   # Deserialize a flow
   flow = Flow()
   flow.deserialize(data)
   
   # Deserialize a routine
   routine = Routine2()
   routine.deserialize(data)
   
   # Deserialize a job state
   job_state = JobState()
   job_state.deserialize(data)

Saving to JSON
--------------

Save serialized data to JSON:

.. code-block:: python

   import json
   
   data = flow.serialize()
   with open("flow.json", "w") as f:
       json.dump(data, f, indent=2)

Loading from JSON
-----------------

Load from JSON:

.. code-block:: python

   import json
   
   with open("flow.json", "r") as f:
       data = json.load(f)
   
   flow = Flow()
   flow.deserialize(data)

Serializable Fields
-------------------

Classes register fields for serialization:

.. code-block:: python

   self.add_serializable_fields(["field1", "field2", "field3"])

Only registered fields are serialized. Complex objects (lists, dicts, other Serializable objects) are automatically handled.


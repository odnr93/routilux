Working with Flows
==================

Flows orchestrate multiple routines and manage their execution. This guide explains how to create and use flows.

Creating a Flow
---------------

Create a flow with an optional flow ID:

.. code-block:: python

   from flowforge import Flow

   flow = Flow(flow_id="my_flow")
   # Or let it auto-generate an ID
   flow = Flow()

Adding Routines
---------------

Add routines to a flow:

.. code-block:: python

   routine = MyRoutine()
   routine_id = flow.add_routine(routine, routine_id="my_routine")
   # Or use the routine's auto-generated ID
   routine_id = flow.add_routine(routine)

Connecting Routines
-------------------

Connect routines by linking events to slots:

.. code-block:: python

   flow.connect(
       source_routine_id="routine1",
       source_event="output",
       target_routine_id="routine2",
       target_slot="input"
   )

You can also specify parameter mapping:

.. code-block:: python

   flow.connect(
       source_routine_id="routine1",
       source_event="output",
       target_routine_id="routine2",
       target_slot="input",
       param_mapping={"source_param": "target_param"}
   )

Executing Flows
---------------

Execute a flow starting from an entry routine:

.. code-block:: python

   job_state = flow.execute(
       entry_routine_id="routine1",
       entry_params={"data": "test"}
   )

The execute method returns a ``JobState`` object that tracks the execution status.

Pausing Execution
-----------------

Pause execution at any point:

.. code-block:: python

   flow.pause(reason="User requested pause", checkpoint={"step": 1})

Resuming Execution
------------------

Resume from a paused state:

.. code-block:: python

   flow.resume(job_state)

Cancelling Execution
--------------------

Cancel execution:

.. code-block:: python

   flow.cancel(reason="User cancelled")

Error Handling
--------------

Set an error handler for the flow:

.. code-block:: python

   from flowforge import ErrorHandler, ErrorStrategy

   error_handler = ErrorHandler(strategy=ErrorStrategy.RETRY, max_retries=3)
   flow.set_error_handler(error_handler)

See :doc:`error_handling` for more details.


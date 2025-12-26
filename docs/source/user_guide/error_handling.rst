Error Handling
==============

flowforge provides flexible error handling through the ErrorHandler class.

Error Strategies
----------------

Four error handling strategies are available:

* **STOP**: Stop execution immediately (default)
* **CONTINUE**: Continue execution despite errors
* **RETRY**: Retry the failed routine
* **SKIP**: Skip the failed routine and continue

Creating an Error Handler
-------------------------

Create an error handler with a strategy:

.. code-block:: python

   from flowforge import ErrorHandler, ErrorStrategy

   # Stop on error (default)
   error_handler = ErrorHandler(strategy=ErrorStrategy.STOP)
   
   # Continue on error
   error_handler = ErrorHandler(strategy=ErrorStrategy.CONTINUE)
   
   # Retry on error
   error_handler = ErrorHandler(
       strategy=ErrorStrategy.RETRY,
       max_retries=3,
       retry_delay=1.0,
       retry_backoff=2.0
   )
   
   # Skip on error
   error_handler = ErrorHandler(strategy=ErrorStrategy.SKIP)

Configuring Retry
-----------------

Configure retry behavior:

.. code-block:: python

   error_handler = ErrorHandler(
       strategy=ErrorStrategy.RETRY,
       max_retries=5,           # Maximum retry attempts
       retry_delay=0.5,         # Initial delay in seconds
       retry_backoff=2.0,       # Delay multiplier
       retryable_exceptions=(ValueError, TypeError)  # Retryable exception types
   )

Setting Error Handler
---------------------

Set the error handler for a flow:

.. code-block:: python

   flow.set_error_handler(error_handler)

Resetting Error Handler
-----------------------

Reset the retry count:

.. code-block:: python

   error_handler.reset()

Error Context
-------------

Error handlers receive context information:

.. code-block:: python

   def handle_error(self, error, routine, routine_id, flow, context=None):
       # error: The exception that occurred
       # routine: The routine that failed
       # routine_id: ID of the failed routine
       # flow: The flow containing the routine
       # context: Optional context dictionary
       pass


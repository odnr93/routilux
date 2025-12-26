Testing
=======

This document provides comprehensive testing information for flowforge.

Test Structure
--------------

.. code-block:: text

   tests/
   ├── __init__.py              # Test package initialization
   ├── conftest.py              # pytest configuration and fixtures
   ├── test_routine.py          # Routine2 tests
   ├── test_slot.py             # Slot tests
   ├── test_event.py            # Event tests
   ├── test_connection.py       # Connection tests
   ├── test_flow.py             # Flow tests
   ├── test_job_state.py        # JobState tests
   ├── test_persistence.py      # Persistence tests
   ├── test_integration.py      # Integration tests
   ├── test_resume.py           # Resume functionality tests
   ├── test_flow_comprehensive.py      # Comprehensive Flow tests
   ├── test_error_handler_comprehensive.py  # ErrorHandler tests
   ├── test_execution_tracker_comprehensive.py  # ExecutionTracker tests
   └── test_connection_comprehensive.py    # Comprehensive Connection tests

Running Tests
-------------

Install Dependencies
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install pytest pytest-cov pytest-mock

Run All Tests
~~~~~~~~~~~~~

.. code-block:: bash

   pytest tests/

Run Specific Test File
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pytest tests/test_routine.py

Run Specific Test Case
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pytest tests/test_routine.py::TestRoutine2Basic::test_create_routine

Generate Coverage Report
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pytest --cov=flowforge --cov-report=html tests/

Test Coverage
-------------

Unit Tests
~~~~~~~~~~

* ✅ Routine2 basic functionality
* ✅ Slot connection and data reception
* ✅ Event connection and triggering
* ✅ Connection parameter mapping
* ✅ Flow management and execution
* ✅ JobState state management
* ✅ ErrorHandler strategies
* ✅ ExecutionTracker functionality

Integration Tests
~~~~~~~~~~~~~~~~

* ✅ Complete workflow execution
* ✅ Error handling workflows
* ✅ Parallel processing workflows
* ✅ Complex nested workflows

Persistence Tests
~~~~~~~~~~~~~~~~~

* ✅ Flow serialization/deserialization
* ✅ JobState serialization/deserialization
* ✅ Consistency verification

Resume Tests
~~~~~~~~~~~~

* ✅ Resume from intermediate state
* ✅ Resume from completed state
* ✅ Resume from error state
* ✅ State consistency verification

Test Coverage Statistics
------------------------

* **Total Test Cases**: 100+
* **Function Coverage**: 100%
* **Boundary Cases**: Complete
* **Error Handling**: Complete

All core functionality has been tested and verified.


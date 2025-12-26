Introduction
============

flowforge is an improved Routine mechanism that provides more flexible connection, state management, and workflow orchestration capabilities.

Overview
--------

flowforge is designed to provide a powerful and flexible framework for building workflow-based applications. It introduces a clear separation between input slots and output events, enabling complex data flow patterns while maintaining simplicity and clarity.

Key Features
------------

* **Slots and Events Mechanism**: Clear distinction between input slots and output events
* **Many-to-Many Connections**: Flexible connection relationships between routines
* **State Management**: Unified ``stats()`` method for tracking routine state
* **Flow Manager**: Workflow orchestration, persistence, and recovery
* **JobState Management**: Execution state recording and recovery functionality
* **Error Handling**: Multiple error handling strategies (STOP, CONTINUE, RETRY, SKIP)
* **Execution Tracking**: Comprehensive execution tracking and performance monitoring
* **Serialization Support**: Full serialization/deserialization support for persistence

Architecture
------------

The framework consists of several core components:

* **Routine2**: Base class for all routines, providing slot and event definitions
* **Flow**: Manager for orchestrating multiple routines and their connections
* **Event**: Output mechanism for routines to emit data
* **Slot**: Input mechanism for routines to receive data
* **Connection**: Links events to slots with optional parameter mapping
* **JobState**: Tracks execution state and history
* **ErrorHandler**: Handles errors with configurable strategies
* **ExecutionTracker**: Monitors execution performance and event flow

Design Principles
-----------------

* **Separation of Concerns**: Clear separation between control (Flow) and data (JobState)
* **Flexibility**: Support for various workflow patterns (linear, branching, converging)
* **Persistence**: Full support for serialization and state recovery
* **Error Resilience**: Multiple error handling strategies for robust applications
* **Observability**: Comprehensive tracking and monitoring capabilities


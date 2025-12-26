# Examples

This directory contains practical examples demonstrating flowforge usage.

## Examples

### basic_example.py
A simple example demonstrating:
- Creating routines with slots and events
- Connecting routines in a flow
- Executing a flow
- Checking execution status

**Run:**
```bash
python examples/basic_example.py
```

### data_processing.py
A multi-stage data processing pipeline example demonstrating:
- Complex data flow with multiple stages
- Parameter mapping
- Statistics tracking

**Run:**
```bash
python examples/data_processing.py
```

### error_handling_example.py
Examples demonstrating different error handling strategies:
- RETRY strategy with retry configuration
- CONTINUE strategy for error logging
- SKIP strategy for fault tolerance

**Run:**
```bash
python examples/error_handling_example.py
```

### state_management_example.py
Examples demonstrating JobState and ExecutionTracker usage:
- JobState for execution tracking
- ExecutionTracker for performance monitoring
- State serialization and persistence

**Run:**
```bash
python examples/state_management_example.py
```

## Running Examples

All examples use FlowForge which is a standalone package. No additional dependencies are required.

```bash
# From project root
cd examples
python basic_example.py
```

## Requirements

Examples use only the standard library and flowforge. No additional dependencies are required beyond the core package.


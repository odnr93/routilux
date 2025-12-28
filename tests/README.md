# Core Tests

This directory contains tests for Routilux core functionality only.

## Test Structure

- **Core Tests**: Tests in `tests/` directory test only the core Routilux framework
  - Routine, Slot, Event, Connection classes
  - Flow orchestration and execution
  - Serialization and persistence
  - Error handling
  - Job state management
  - Execution tracking
  - Aggregation patterns

- **Builtin Routines Tests**: Tests for `builtin_routines` are located in their respective sub-packages:
  - `routilux/builtin_routines/text_processing/tests/`
  - `routilux/builtin_routines/utils/tests/`
  - `routilux/builtin_routines/data_processing/tests/`
  - `routilux/builtin_routines/control_flow/tests/`

## Running Tests

### Run Core Tests Only

```bash
# Run all core tests
pytest tests/

# Run specific test file
pytest tests/test_routine.py

# Run with coverage
pytest tests/ --cov=routilux --cov-report=html
```

### Run Builtin Routines Tests

Run all builtin_routines tests using pytest:

```bash
# Run all builtin_routines tests
pytest routilux/builtin_routines/ -v

# Run specific sub-package tests
pytest routilux/builtin_routines/text_processing/tests/ -v
pytest routilux/builtin_routines/utils/tests/ -v
pytest routilux/builtin_routines/data_processing/tests/ -v
pytest routilux/builtin_routines/control_flow/tests/ -v

# Run specific test file
pytest routilux/builtin_routines/text_processing/tests/test_text_processing.py -v
```

### Run All Tests

```bash
# Run both core and builtin_routines tests
pytest tests/ routilux/builtin_routines/ -v
```

## Test Organization

All tests use **pytest** framework. The `pytest.ini` configuration:
- Excludes `builtin_routines` from core test runs
- Configures coverage reporting
- Sets up test markers

## Notes

- Core tests should NOT import from `routilux.builtin_routines`
- Builtin routines tests are self-contained in their sub-packages
- Each builtin routine sub-package has its own `tests/` directory for portability

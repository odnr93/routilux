# AST Analyzer Tool

This tool analyzes the Routilux codebase's AST (Abstract Syntax Tree) and generates a compact API reference document optimized for LLM consumption.

## Usage

```bash
python tools/analyze_codebase_ast.py
```

The tool will:
1. Parse core Routilux Python files
2. Extract class definitions, methods, and functions
3. Extract type annotations, parameters, and docstrings
4. Generate a compact markdown document at `docs/source/api_reference_compact.md`

## Output Format

The generated document includes:
- Class definitions with base classes
- Method signatures with type annotations
- Function signatures with type annotations
- Brief docstrings (first line only for compactness)

## Core Files Analyzed

- `routilux/routine.py` - Routine base class
- `routilux/flow.py` - Flow manager
- `routilux/slot.py` - Slot class
- `routilux/event.py` - Event class
- `routilux/connection.py` - Connection class
- `routilux/error_handler.py` - ErrorHandler class
- `routilux/job_state.py` - JobState class
- `routilux/execution_tracker.py` - ExecutionTracker class
- `routilux/utils/serializable.py` - Serializable base class
- `routilux/serialization_utils.py` - Serialization utilities

## Purpose

This compact reference is designed for:
- LLM code generation assistants
- Quick API lookup
- Understanding the codebase structure
- Generating code that uses Routilux

The document is intentionally compact to fit within LLM context windows while providing essential API information.


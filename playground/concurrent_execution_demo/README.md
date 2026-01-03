# Concurrent Execution Demonstration

This demo showcases routilux's concurrent execution capabilities with thread pool management, complex workflows, and detailed monitoring.

## Overview

This demonstration shows:
1. **Complex Workflow**: A 5-stage pipeline with multiple routines
2. **Concurrent Execution**: 4 jobs executing simultaneously
3. **Thread Pool Management**: max_workers=2 limiting concurrent routine execution
4. **Detailed Monitoring**: Real-time tracking of all job states
5. **Data & Timestamp Tracking**: Each routine generates data with timestamps

## Architecture

### Workflow Structure

```
DataSource → DataProcessor → DataValidator → DataAggregator → DataReporter
```

Each routine:
- Generates data with timestamps
- Stores data in JobState.shared_data
- Logs actions to JobState.shared_log
- Updates routine state with timestamps

### Routines

1. **DataSourceRoutine**: Generates initial data with timestamp
2. **DataProcessorRoutine**: Processes data and adds processing timestamp
3. **DataValidatorRoutine**: Validates data and adds validation timestamp
4. **DataAggregatorRoutine**: Aggregates validated data with timestamp
5. **DataReporterRoutine**: Generates final report with timestamp

## Features Demonstrated

### 1. Concurrent Execution
- 4 jobs execute simultaneously
- Each job has its own JobState
- Independent execution tracking

### 2. Thread Pool Limiting
- max_workers=2 (less than number of jobs)
- At most 2 routines execute simultaneously
- Demonstrates resource management

### 3. Detailed Monitoring
- Real-time status updates
- Execution history tracking
- Shared data and log monitoring
- Routine state tracking

### 4. Data Flow Tracking
- Each routine generates data with timestamps
- Data flows through the pipeline
- Final aggregation and reporting

## Usage

### Run the Demo

```bash
cd /home/percy/works/mygithub/routilux
conda activate mbos
uv run python -m playground.concurrent_execution_demo.concurrent_demo
```

### Expected Output

The demo will:
1. Create a complex workflow with 5 routines
2. Start 4 concurrent jobs
3. Monitor execution with periodic status updates
4. Display detailed reports for each job
5. Show execution summary

### Output Format

- **Status Updates**: Periodic updates showing job status, history count, and log entries
- **Detailed Reports**: For each job:
  - Execution history with timestamps
  - Shared data with timestamps
  - Routine states
  - Final report summary
- **Execution Summary**: Total jobs, completion status, execution time

## Configuration

You can modify the demo configuration in `concurrent_demo.py`:

```python
num_jobs = 4          # Number of concurrent jobs
max_workers = 2       # Thread pool size (must be < num_jobs to see limiting)
```

## Key Concepts Demonstrated

### 1. Concurrent Execution Strategy
- Flow uses `execution_strategy="concurrent"`
- Thread pool executor manages parallel execution
- max_workers limits concurrent routines

### 2. JobState Isolation
- Each job has independent JobState
- Shared data and logs are per-job
- No cross-job data contamination

### 3. Execution Monitoring
- `JobState.wait_for_completion()` for proper completion detection
- Real-time status monitoring
- Detailed execution tracking

### 4. Data Generation and Tracking
- Each routine generates data with timestamps
- Data flows through event-slot connections
- Final aggregation collects all data

## Performance Observations

With max_workers=2 and 4 concurrent jobs:
- Jobs start almost simultaneously
- Execution is limited by thread pool size
- Total execution time reflects concurrent processing
- All jobs complete successfully

## Code Structure

```
concurrent_execution_demo/
├── __init__.py
├── data_generator_routines.py  # Routine implementations
├── concurrent_demo.py          # Main demonstration
└── README.md                   # This file
```

## Extending the Demo

You can extend this demo by:
1. Adding more routines to the workflow
2. Increasing the number of concurrent jobs
3. Adjusting thread pool size
4. Adding more complex data processing
5. Implementing error handling scenarios

## Notes

- Each routine simulates processing with delays (0.1-0.18s)
- Timestamps are generated at each stage
- All data is stored in JobState for isolation
- Execution history tracks all routine executions
- Shared logs track all actions


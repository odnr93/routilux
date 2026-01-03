"""
Data generator routines for concurrent execution demonstration.

Each routine generates data with timestamps to demonstrate parallel execution
and thread pool management.
"""

import time
import random
from datetime import datetime
from typing import Dict, Any
from routilux import Routine
from serilux import register_serializable


@register_serializable
class DataSourceRoutine(Routine):
    """Data source routine that generates initial data with timestamp."""
    
    def __init__(self, delay: float = 0.1):
        """Initialize data source routine.
        
        Args:
            delay: Simulated processing delay in seconds.
        """
        super().__init__()
        self.set_config(delay=delay)
        
        self.trigger_slot = self.define_slot("trigger", handler=self.generate_data)
        self.output_event = self.define_event("output", ["data", "timestamp", "source_id"])
    
    def generate_data(self, job_id: str = None, **kwargs):
        """Generate initial data with timestamp.
        
        Args:
            job_id: Job identifier.
            **kwargs: Additional parameters.
        """
        ctx = self.get_execution_context()
        if not ctx:
            return
        
        delay = self.get_config("delay", default=0.1)
        time.sleep(delay)  # Simulate processing time
        
        # Generate data with timestamp
        timestamp = datetime.now().isoformat()
        source_id = f"source_{random.randint(1000, 9999)}"
        data = {
            "job_id": job_id or ctx.job_state.job_id,
            "value": random.randint(1, 100),
            "source_id": source_id,
            "generated_at": timestamp,
        }
        
        # Store in shared data
        ctx.job_state.update_shared_data(f"source_data_{source_id}", data)
        ctx.job_state.append_to_shared_log({
            "action": "data_generated",
            "routine": "DataSourceRoutine",
            "source_id": source_id,
            "timestamp": timestamp,
        })
        
        # Update routine state
        ctx.job_state.update_routine_state(ctx.routine_id, {
            "status": "completed",
            "data_generated": True,
            "source_id": source_id,
            "timestamp": timestamp,
        })
        
        # Emit output
        self.emit("output", data=data, timestamp=timestamp, source_id=source_id)


@register_serializable
class DataProcessorRoutine(Routine):
    """Data processor routine that processes data and adds processing timestamp."""
    
    def __init__(self, delay: float = 0.15):
        """Initialize data processor routine.
        
        Args:
            delay: Simulated processing delay in seconds.
        """
        super().__init__()
        self.set_config(delay=delay)
        
        self.input_slot = self.define_slot("input", handler=self.process_data)
        self.output_event = self.define_event("output", ["processed_data", "timestamp", "processor_id"])
    
    def process_data(self, data: Dict[str, Any] = None, **kwargs):
        """Process incoming data and add processing timestamp.
        
        Args:
            data: Input data dictionary.
            **kwargs: Additional parameters.
        """
        ctx = self.get_execution_context()
        if not ctx:
            return
        
        # Merge data from kwargs if data is None
        if data is None:
            data = kwargs.get("data", {})
        
        delay = self.get_config("delay", default=0.15)
        time.sleep(delay)  # Simulate processing time
        
        # Process data and add timestamp
        timestamp = datetime.now().isoformat()
        processor_id = f"processor_{random.randint(1000, 9999)}"
        
        processed_data = {
            **data,
            "processed_at": timestamp,
            "processor_id": processor_id,
            "processed_value": data.get("value", 0) * 2,  # Example processing
        }
        
        # Store in shared data
        ctx.job_state.update_shared_data(f"processed_data_{processor_id}", processed_data)
        ctx.job_state.append_to_shared_log({
            "action": "data_processed",
            "routine": "DataProcessorRoutine",
            "processor_id": processor_id,
            "source_id": data.get("source_id", "unknown"),
            "timestamp": timestamp,
        })
        
        # Update routine state
        ctx.job_state.update_routine_state(ctx.routine_id, {
            "status": "completed",
            "data_processed": True,
            "processor_id": processor_id,
            "timestamp": timestamp,
        })
        
        # Emit output
        self.emit("output", processed_data=processed_data, timestamp=timestamp, processor_id=processor_id)


@register_serializable
class DataValidatorRoutine(Routine):
    """Data validator routine that validates data and adds validation timestamp."""
    
    def __init__(self, delay: float = 0.12):
        """Initialize data validator routine.
        
        Args:
            delay: Simulated processing delay in seconds.
        """
        super().__init__()
        self.set_config(delay=delay)
        
        self.input_slot = self.define_slot("input", handler=self.validate_data)
        self.output_event = self.define_event("output", ["validated_data", "timestamp", "validator_id"])
        self.error_event = self.define_event("error", ["error_data", "timestamp", "validator_id"])
    
    def validate_data(self, processed_data: Dict[str, Any] = None, **kwargs):
        """Validate processed data and add validation timestamp.
        
        Args:
            processed_data: Processed data dictionary.
            **kwargs: Additional parameters.
        """
        ctx = self.get_execution_context()
        if not ctx:
            return
        
        # Merge data from kwargs if processed_data is None
        if processed_data is None:
            processed_data = kwargs.get("processed_data", {})
        
        delay = self.get_config("delay", default=0.12)
        time.sleep(delay)  # Simulate processing time
        
        # Validate data and add timestamp
        timestamp = datetime.now().isoformat()
        validator_id = f"validator_{random.randint(1000, 9999)}"
        
        # Simple validation: check if processed_value exists and is positive
        is_valid = processed_data.get("processed_value", 0) > 0
        
        validated_data = {
            **processed_data,
            "validated_at": timestamp,
            "validator_id": validator_id,
            "is_valid": is_valid,
        }
        
        # Store in shared data
        ctx.job_state.update_shared_data(f"validated_data_{validator_id}", validated_data)
        ctx.job_state.append_to_shared_log({
            "action": "data_validated",
            "routine": "DataValidatorRoutine",
            "validator_id": validator_id,
            "is_valid": is_valid,
            "timestamp": timestamp,
        })
        
        # Update routine state
        ctx.job_state.update_routine_state(ctx.routine_id, {
            "status": "completed",
            "data_validated": True,
            "validator_id": validator_id,
            "is_valid": is_valid,
            "timestamp": timestamp,
        })
        
        # Emit output based on validation result
        if is_valid:
            self.emit("output", validated_data=validated_data, timestamp=timestamp, validator_id=validator_id)
        else:
            self.emit("error", error_data=validated_data, timestamp=timestamp, validator_id=validator_id)


@register_serializable
class DataAggregatorRoutine(Routine):
    """Data aggregator routine that aggregates validated data and adds aggregation timestamp."""
    
    def __init__(self, delay: float = 0.18):
        """Initialize data aggregator routine.
        
        Args:
            delay: Simulated processing delay in seconds.
        """
        super().__init__()
        self.set_config(delay=delay)
        
        self.input_slot = self.define_slot("input", handler=self.aggregate_data)
        self.output_event = self.define_event("output", ["aggregated_data", "timestamp", "aggregator_id"])
    
    def aggregate_data(self, validated_data: Dict[str, Any] = None, **kwargs):
        """Aggregate validated data and add aggregation timestamp.
        
        Args:
            validated_data: Validated data dictionary.
            **kwargs: Additional parameters.
        """
        ctx = self.get_execution_context()
        if not ctx:
            return
        
        # Merge data from kwargs if validated_data is None
        if validated_data is None:
            validated_data = kwargs.get("validated_data", {})
        
        delay = self.get_config("delay", default=0.18)
        time.sleep(delay)  # Simulate processing time
        
        # Aggregate data and add timestamp
        timestamp = datetime.now().isoformat()
        aggregator_id = f"aggregator_{random.randint(1000, 9999)}"
        
        # Get all validated data from shared_data
        all_validated = []
        for key, value in ctx.job_state.shared_data.items():
            if key.startswith("validated_data_"):
                all_validated.append(value)
        
        aggregated_data = {
            "aggregated_at": timestamp,
            "aggregator_id": aggregator_id,
            "total_items": len(all_validated),
            "items": all_validated,
            "final_value": sum(item.get("processed_value", 0) for item in all_validated),
        }
        
        # Store in shared data
        ctx.job_state.update_shared_data("final_aggregated_data", aggregated_data)
        ctx.job_state.append_to_shared_log({
            "action": "data_aggregated",
            "routine": "DataAggregatorRoutine",
            "aggregator_id": aggregator_id,
            "total_items": len(all_validated),
            "timestamp": timestamp,
        })
        
        # Update routine state
        ctx.job_state.update_routine_state(ctx.routine_id, {
            "status": "completed",
            "data_aggregated": True,
            "aggregator_id": aggregator_id,
            "total_items": len(all_validated),
            "timestamp": timestamp,
        })
        
        # Emit output
        self.emit("output", aggregated_data=aggregated_data, timestamp=timestamp, aggregator_id=aggregator_id)


@register_serializable
class DataReporterRoutine(Routine):
    """Data reporter routine that generates final report with timestamp."""
    
    def __init__(self, delay: float = 0.1):
        """Initialize data reporter routine.
        
        Args:
            delay: Simulated processing delay in seconds.
        """
        super().__init__()
        self.set_config(delay=delay)
        
        self.input_slot = self.define_slot("input", handler=self.generate_report)
        self.output_event = self.define_event("output", ["report", "timestamp", "reporter_id"])
    
    def generate_report(self, aggregated_data: Dict[str, Any] = None, **kwargs):
        """Generate final report with timestamp.
        
        Args:
            aggregated_data: Aggregated data dictionary.
            **kwargs: Additional parameters.
        """
        ctx = self.get_execution_context()
        if not ctx:
            return
        
        # Merge data from kwargs if aggregated_data is None
        if aggregated_data is None:
            aggregated_data = kwargs.get("aggregated_data", {})
        
        delay = self.get_config("delay", default=0.1)
        time.sleep(delay)  # Simulate processing time
        
        # Generate report with timestamp
        timestamp = datetime.now().isoformat()
        reporter_id = f"reporter_{random.randint(1000, 9999)}"
        
        report = {
            "report_id": reporter_id,
            "generated_at": timestamp,
            "job_id": ctx.job_state.job_id,
            "flow_id": ctx.job_state.flow_id,
            "summary": {
                "total_items": aggregated_data.get("total_items", 0),
                "final_value": aggregated_data.get("final_value", 0),
            },
            "execution_history": len(ctx.job_state.execution_history),
            "shared_log_entries": len(ctx.job_state.shared_log),
        }
        
        # Store in shared data
        ctx.job_state.update_shared_data("final_report", report)
        ctx.job_state.append_to_shared_log({
            "action": "report_generated",
            "routine": "DataReporterRoutine",
            "reporter_id": reporter_id,
            "timestamp": timestamp,
        })
        
        # Update routine state
        ctx.job_state.update_routine_state(ctx.routine_id, {
            "status": "completed",
            "report_generated": True,
            "reporter_id": reporter_id,
            "timestamp": timestamp,
        })
        
        # Emit output
        self.emit("output", report=report, timestamp=timestamp, reporter_id=reporter_id)


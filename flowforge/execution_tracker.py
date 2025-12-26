"""
执行跟踪器

用于跟踪 flow 的执行状态和性能。
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
from datetime import datetime
from flowforge.utils.serializable import register_serializable, Serializable


@register_serializable
class ExecutionTracker(Serializable):
    """
    执行跟踪器
    
    跟踪 flow 的执行状态、性能和事件流
    """
    
    def __init__(self, flow_id: str = ""):
        """
        初始化 ExecutionTracker
        
        Args:
            flow_id: Flow ID
        """
        super().__init__()
        self.flow_id: str = flow_id
        self.routine_executions: Dict[str, List[Dict[str, Any]]] = {}  # routine_id -> 执行记录列表
        self.event_flow: List[Dict[str, Any]] = []  # 事件流记录
        self.performance_metrics: Dict[str, Any] = {}  # 性能指标
        
        # 注册可序列化字段
        self.add_serializable_fields([
            "flow_id", "routine_executions", "event_flow", "performance_metrics"
        ])
    
    def record_routine_start(self, routine_id: str, params: Dict[str, Any] = None) -> None:
        """
        记录 routine 开始执行
        
        Args:
            routine_id: Routine ID
            params: 执行参数
        """
        if routine_id not in self.routine_executions:
            self.routine_executions[routine_id] = []
        
        execution = {
            "routine_id": routine_id,
            "start_time": datetime.now().isoformat(),
            "params": params or {},
            "status": "running"
        }
        self.routine_executions[routine_id].append(execution)
    
    def record_routine_end(
        self,
        routine_id: str,
        status: str = "completed",
        result: Any = None,
        error: Optional[str] = None
    ) -> None:
        """
        记录 routine 执行结束
        
        Args:
            routine_id: Routine ID
            status: 状态 ("completed", "failed")
            result: 执行结果
            error: 错误信息（如果有）
        """
        if routine_id not in self.routine_executions:
            return
        
        if not self.routine_executions[routine_id]:
            return
        
        execution = self.routine_executions[routine_id][-1]
        execution["end_time"] = datetime.now().isoformat()
        execution["status"] = status
        
        if result is not None:
            execution["result"] = result
        
        if error is not None:
            execution["error"] = error
        
        # 计算执行时间
        if "start_time" in execution and "end_time" in execution:
            start = datetime.fromisoformat(execution["start_time"])
            end = datetime.fromisoformat(execution["end_time"])
            execution["execution_time"] = (end - start).total_seconds()
    
    def record_event(
        self,
        source_routine_id: str,
        event_name: str,
        target_routine_id: Optional[str] = None,
        data: Dict[str, Any] = None
    ) -> None:
        """
        记录事件触发
        
        Args:
            source_routine_id: 源 Routine ID
            event_name: 事件名称
            target_routine_id: 目标 Routine ID（如果有）
            data: 传递的数据
        """
        event_record = {
            "timestamp": datetime.now().isoformat(),
            "source_routine_id": source_routine_id,
            "event_name": event_name,
            "target_routine_id": target_routine_id,
            "data": data or {}
        }
        self.event_flow.append(event_record)
    
    def get_routine_performance(self, routine_id: str) -> Optional[Dict[str, Any]]:
        """
        获取 routine 的性能指标
        
        Args:
            routine_id: Routine ID
        
        Returns:
            性能指标字典，如果不存在则返回 None
        """
        if routine_id not in self.routine_executions:
            return None
        
        executions = self.routine_executions[routine_id]
        if not executions:
            return None
        
        # 计算统计信息
        total_executions = len(executions)
        completed = sum(1 for e in executions if e.get("status") == "completed")
        failed = sum(1 for e in executions if e.get("status") == "failed")
        
        execution_times = [
            e.get("execution_time", 0)
            for e in executions
            if "execution_time" in e
        ]
        
        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0
        min_time = min(execution_times) if execution_times else 0
        max_time = max(execution_times) if execution_times else 0
        
        return {
            "total_executions": total_executions,
            "completed": completed,
            "failed": failed,
            "success_rate": completed / total_executions if total_executions > 0 else 0,
            "avg_execution_time": avg_time,
            "min_execution_time": min_time,
            "max_execution_time": max_time
        }
    
    def get_flow_performance(self) -> Dict[str, Any]:
        """
        获取整个 flow 的性能指标
        
        Returns:
            性能指标字典
        """
        total_routines = len(self.routine_executions)
        total_events = len(self.event_flow)
        
        all_execution_times = []
        for routine_id in self.routine_executions:
            perf = self.get_routine_performance(routine_id)
            if perf and perf.get("avg_execution_time"):
                all_execution_times.append(perf["avg_execution_time"])
        
        total_time = sum(all_execution_times)
        avg_time = total_time / len(all_execution_times) if all_execution_times else 0
        
        return {
            "total_routines": total_routines,
            "total_events": total_events,
            "total_execution_time": total_time,
            "avg_routine_time": avg_time
        }


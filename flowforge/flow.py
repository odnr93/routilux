"""
Flow 类

Flow 管理器，负责管理多个 Routine 节点和执行流程。
"""
from __future__ import annotations
import uuid
from typing import Dict, Optional, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from flowforge.routine import Routine2
    from flowforge.connection import Connection
    from flowforge.job_state import JobState
    from flowforge.event import Event
    from flowforge.slot import Slot
    from flowforge.execution_tracker import ExecutionTracker
    from flowforge.error_handler import ErrorHandler

from flowforge.utils.serializable import register_serializable, Serializable
from flowforge.serialization_utils import (
    get_routine_class_info,
    load_routine_class,
    serialize_callable,
    deserialize_callable
)


@register_serializable
class Flow(Serializable):
    """
    Flow 管理器
    
    负责：
    - 管理多个 Routine 节点
    - 管理节点之间的连接
    - 执行流程
    - 持久化和恢复
    """
    
    def __init__(self, flow_id: Optional[str] = None):
        """
        初始化 Flow
        
        Args:
            flow_id: Flow ID（如果为 None 则自动生成）
        """
        super().__init__()
        self.flow_id: str = flow_id or str(uuid.uuid4())
        self.routines: Dict[str, 'Routine2'] = {}  # routine_id -> Routine2
        self.connections: List['Connection'] = []  # 连接列表
        self.job_state: Optional['JobState'] = None  # 当前作业状态
        self._current_flow: Optional['Flow'] = None  # 当前执行的 flow（用于上下文）
        self.execution_tracker: Optional['ExecutionTracker'] = None  # 执行跟踪器
        self.error_handler: Optional['ErrorHandler'] = None  # 错误处理器
        self._paused: bool = False  # 是否暂停
        
        # 注册可序列化字段
        # 注意：routines 和 connections 的序列化需要特殊处理（在 serialize 方法中）
        self.add_serializable_fields([
            "flow_id", "routines", "connections", "job_state", "_paused"
        ])
        
        # 维护 event -> connection 的映射，用于快速查找
        # 注意：_event_slot_connections 不需要持久化，可以从 connections 重建
        self._event_slot_connections: Dict[tuple, 'Connection'] = {}  # (event, slot) -> Connection
    
    def __repr__(self) -> str:
        """返回对象的字符串表示"""
        return f"Flow[{self.flow_id}]"
    
    def _find_connection(self, event: 'Event', slot: 'Slot') -> Optional['Connection']:
        """
        查找 event 到 slot 的 Connection
        
        Args:
            event: Event 对象
            slot: Slot 对象
        
        Returns:
            Connection 对象，如果不存在则返回 None
        """
        key = (event, slot)
        return self._event_slot_connections.get(key)
    
    def add_routine(self, routine: 'Routine2', routine_id: Optional[str] = None) -> str:
        """
        添加一个 routine 到 flow
        
        Args:
            routine: Routine2 对象
            routine_id: Routine ID（如果为 None 则使用 routine._id）
        
        Returns:
            Routine ID
        
        Raises:
            ValueError: 如果 routine_id 已存在
        """
        rid = routine_id or routine._id
        if rid in self.routines:
            raise ValueError(f"Routine ID '{rid}' already exists in flow")
        
        self.routines[rid] = routine
        return rid
    
    def connect(
        self,
        source_routine_id: str,
        source_event: str,
        target_routine_id: str,
        target_slot: str,
        param_mapping: Optional[Dict[str, str]] = None
    ) -> 'Connection':
        """
        连接两个 routine
        
        Args:
            source_routine_id: 源 Routine ID
            source_event: 源 Event 名称
            target_routine_id: 目标 Routine ID
            target_slot: 目标 Slot 名称
            param_mapping: 参数映射字典
        
        Returns:
            Connection 对象
        
        Raises:
            ValueError: 如果 routine、event 或 slot 不存在
        """
        # 验证源 routine
        if source_routine_id not in self.routines:
            raise ValueError(f"Source routine '{source_routine_id}' not found in flow")
        
        source_routine = self.routines[source_routine_id]
        source_event_obj = source_routine.get_event(source_event)
        if source_event_obj is None:
            raise ValueError(f"Event '{source_event}' not found in routine '{source_routine_id}'")
        
        # 验证目标 routine
        if target_routine_id not in self.routines:
            raise ValueError(f"Target routine '{target_routine_id}' not found in flow")
        
        target_routine = self.routines[target_routine_id]
        target_slot_obj = target_routine.get_slot(target_slot)
        if target_slot_obj is None:
            raise ValueError(f"Slot '{target_slot}' not found in routine '{target_routine_id}'")
        
        # 创建连接
        from flowforge.connection import Connection
        connection = Connection(source_event_obj, target_slot_obj, param_mapping)
        self.connections.append(connection)
        
        # 维护映射关系
        key = (source_event_obj, target_slot_obj)
        self._event_slot_connections[key] = connection
        
        return connection
    
    def set_error_handler(self, error_handler: 'ErrorHandler') -> None:
        """
        设置错误处理器
        
        Args:
            error_handler: ErrorHandler 对象
        """
        self.error_handler = error_handler
    
    def pause(self, reason: str = "", checkpoint: Optional[Dict[str, Any]] = None) -> None:
        """
        暂停执行
        
        这是暂停执行的主要入口点。JobState 只负责状态记录，执行控制由 Flow 负责。
        
        Args:
            reason: 暂停原因
            checkpoint: 检查点数据（可选）
        
        Raises:
            ValueError: 如果没有正在执行的 job_state
        """
        if not self.job_state:
            raise ValueError("No active job_state to pause. Flow must be executing.")
        
        self.job_state._set_paused(reason=reason, checkpoint=checkpoint)
        self._paused = True
    
    def execute(
        self,
        entry_routine_id: str,
        entry_params: Optional[Dict[str, Any]] = None
    ) -> 'JobState':
        """
        执行 flow
        
        Args:
            entry_routine_id: 入口 Routine ID
            entry_params: 入口参数
        
        Returns:
            JobState 对象
        
        Raises:
            ValueError: 如果 entry_routine_id 不存在
        """
        if entry_routine_id not in self.routines:
            raise ValueError(f"Entry routine '{entry_routine_id}' not found in flow")
        
        # 创建 JobState
        from flowforge.job_state import JobState
        from flowforge.execution_tracker import ExecutionTracker
        
        job_state = JobState(self.flow_id)
        job_state.status = "running"
        job_state.current_routine_id = entry_routine_id
        self.job_state = job_state
        
        # 创建执行跟踪器
        self.execution_tracker = ExecutionTracker(self.flow_id)
        
        entry_params = entry_params or {}
        
        try:
            # 执行入口 routine（传递 flow 以便事件可以通过 Connection 传递）
            entry_routine = self.routines[entry_routine_id]
            
            # 设置 flow 上下文到所有 routines，让 emit 可以访问
            for routine in self.routines.values():
                routine._current_flow = self
            
            # 记录开始执行
            from datetime import datetime
            start_time = datetime.now()
            job_state.record_execution(entry_routine_id, "start", entry_params)
            self.execution_tracker.record_routine_start(entry_routine_id, entry_params)
            
            # 执行入口 routine
            entry_routine(**entry_params)
            
            # 计算执行时间
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # 更新状态
            job_state.update_routine_state(entry_routine_id, {
                "status": "completed",
                "stats": entry_routine.stats(),
                "execution_time": execution_time,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            })
            
            # 记录完成
            job_state.record_execution(entry_routine_id, "completed", {
                "execution_time": execution_time
            })
            self.execution_tracker.record_routine_end(entry_routine_id, "completed")
            
            job_state.status = "completed"
            
        except Exception as e:
            # 使用错误处理器处理错误
            if self.error_handler:
                should_continue = self.error_handler.handle_error(
                    e, entry_routine, entry_routine_id, self
                )
                
                # 如果是继续策略，标记为完成
                if self.error_handler.strategy.value == "continue":
                    job_state.status = "completed"
                    job_state.update_routine_state(entry_routine_id, {
                        "status": "error_continued",
                        "error": str(e),
                        "stats": entry_routine.stats()
                    })
                    return job_state
                
                # 如果是跳过策略，标记为完成
                if self.error_handler.strategy.value == "skip":
                    job_state.status = "completed"
                    return job_state
                
                # 如果是重试策略
                if should_continue and self.error_handler.strategy.value == "retry":
                    # 重试逻辑
                    retry_success = False
                    for attempt in range(self.error_handler.max_retries):
                        try:
                            entry_routine(**entry_params)
                            retry_success = True
                            break
                        except Exception as retry_error:
                            if attempt < self.error_handler.max_retries - 1:
                                continue
                            else:
                                e = retry_error
                                break
                    
                    if retry_success:
                        # 重试成功，继续正常流程
                        end_time = datetime.now()
                        execution_time = (end_time - start_time).total_seconds()
                        job_state.update_routine_state(entry_routine_id, {
                            "status": "completed",
                            "stats": entry_routine.stats(),
                            "execution_time": execution_time,
                            "retry_count": self.error_handler.retry_count
                        })
                        job_state.record_execution(entry_routine_id, "completed", {
                            "execution_time": execution_time,
                            "retried": True
                        })
                        if self.execution_tracker:
                            self.execution_tracker.record_routine_end(entry_routine_id, "completed")
                        job_state.status = "completed"
                        return job_state
                    # 重试失败，继续错误处理（会执行下面的默认错误处理）
            
            # 默认错误处理（如果没有错误处理器或策略是 STOP）
            from datetime import datetime
            error_time = datetime.now()
            job_state.status = "failed"
            job_state.update_routine_state(entry_routine_id, {
                "status": "failed",
                "error": str(e),
                "error_time": error_time.isoformat()
            })
            # 记录错误到执行历史
            job_state.record_execution(entry_routine_id, "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            if self.execution_tracker:
                self.execution_tracker.record_routine_end(
                    entry_routine_id, "failed", error=str(e)
                )
            import logging
            logging.exception(f"Error executing flow: {e}")
        
        return job_state
    
    def resume(self, job_state: Optional['JobState'] = None) -> 'JobState':
        """
        恢复执行（从暂停或保存的状态）
        
        这是恢复执行的主要入口点。JobState 只负责状态记录，执行控制由 Flow 负责。
        
        Args:
            job_state: 要恢复的 JobState（如果为 None 则使用当前的 job_state）
        
        Returns:
            更新后的 JobState
        
        Raises:
            ValueError: 如果 job_state 的 flow_id 不匹配或 routine 不存在
        """
        if job_state is None:
            job_state = self.job_state
        
        if job_state is None:
            raise ValueError("No JobState to resume")
        
        if job_state.flow_id != self.flow_id:
            raise ValueError(f"JobState flow_id '{job_state.flow_id}' does not match Flow flow_id '{self.flow_id}'")
        
        # 验证当前 routine 存在
        if job_state.current_routine_id and job_state.current_routine_id not in self.routines:
            raise ValueError(f"Current routine '{job_state.current_routine_id}' not found in flow")
        
        # 恢复状态（由 Flow 控制）
        job_state._set_running()
        self._paused = False
        self.job_state = job_state
        
        # 恢复 routine 状态
        for routine_id, routine_state in job_state.routine_states.items():
            if routine_id in self.routines:
                routine = self.routines[routine_id]
                # 恢复 routine 的状态
                if "stats" in routine_state:
                    routine._stats.update(routine_state["stats"])
        
        # 从当前 routine 继续执行
        if job_state.current_routine_id:
            try:
                routine = self.routines[job_state.current_routine_id]
                
                # 设置 flow 上下文
                for r in self.routines.values():
                    r._current_flow = self
                
                # 执行 routine
                routine()
                
                job_state.status = "completed"
                job_state.update_routine_state(job_state.current_routine_id, {
                    "status": "completed",
                    "stats": routine.stats()
                })
            except Exception as e:
                # 使用错误处理器
                if self.error_handler:
                    should_continue = self.error_handler.handle_error(
                        e, routine, job_state.current_routine_id, self
                    )
                    if not should_continue:
                        job_state.status = "failed"
                else:
                    job_state.status = "failed"
                
                job_state.update_routine_state(job_state.current_routine_id, {
                    "status": "failed",
                    "error": str(e)
                })
        
        return job_state
    
    def cancel(self, reason: str = "") -> None:
        """
        取消执行
        
        这是取消执行的主要入口点。JobState 只负责状态记录，执行控制由 Flow 负责。
        
        Args:
            reason: 取消原因
        
        Raises:
            ValueError: 如果没有正在执行的 job_state
        """
        if not self.job_state:
            raise ValueError("No active job_state to cancel. Flow must be executing.")
        
        self.job_state._set_cancelled(reason=reason)
        self._paused = False  # 取消时清除暂停标志
    
    def serialize(self) -> Dict[str, Any]:
        """
        序列化 Flow，包括所有 routines 和 connections
        
        Returns:
            序列化后的字典
        """
        # 先调用父类的 serialize，这会处理注册的字段
        # 但我们需要特殊处理 routines 和 connections
        data = {}
        
        # 序列化基本字段
        for field in self.fields_to_serialize:
            if field in ["routines", "connections"]:
                continue  # 这些字段需要特殊处理
            value = getattr(self, field, None)
            if isinstance(value, Serializable):
                data[field] = value.serialize()
            elif isinstance(value, list):
                data[field] = [
                    item.serialize() if isinstance(item, Serializable) else item
                    for item in value
                ]
            elif isinstance(value, dict):
                data[field] = {
                    k: v.serialize() if isinstance(v, Serializable) else v
                    for k, v in value.items()
                }
            else:
                data[field] = value
        
        # 添加类型信息
        data["_type"] = type(self).__name__
        
        # 序列化 routines（完整信息）
        routines_data = {}
        for routine_id, routine in self.routines.items():
            routine_data = routine.serialize()
            routine_data["routine_id"] = routine_id
            routines_data[routine_id] = routine_data
        
        data["routines"] = routines_data
        
        # 序列化 connections（需要保存 Flow 中的 routine_id，而不是 routine._id）
        connections_data = []
        for connection in self.connections:
            conn_data = connection.serialize()
            
            # 查找 Flow 中的 routine_id
            source_routine_id = None
            target_routine_id = None
            
            for rid, routine in self.routines.items():
                if routine == connection.source_event.routine:
                    source_routine_id = rid
                if routine == connection.target_slot.routine:
                    target_routine_id = rid
            
            # 使用 Flow 中的 routine_id 覆盖
            if source_routine_id:
                conn_data["_source_routine_id"] = source_routine_id
            if target_routine_id:
                conn_data["_target_routine_id"] = target_routine_id
            
            connections_data.append(conn_data)
        
        data["connections"] = connections_data
        
        return data
    
    def deserialize(self, data: Dict[str, Any]) -> None:
        """
        反序列化 Flow，恢复所有 routines 和 connections
        
        Args:
            data: 序列化数据
        """
        # 先反序列化基本字段（排除需要特殊处理的字段）
        basic_data = {k: v for k, v in data.items() if k not in ["routines", "connections", "job_state", "_type"]}
        
        # 处理 job_state（如果存在）
        if "job_state" in data and data["job_state"]:
            from flowforge.job_state import JobState
            from datetime import datetime
            
            job_state_data = data["job_state"].copy()
            
            # 处理 datetime
            if isinstance(job_state_data.get("created_at"), str):
                job_state_data["created_at"] = datetime.fromisoformat(job_state_data["created_at"])
            if isinstance(job_state_data.get("updated_at"), str):
                job_state_data["updated_at"] = datetime.fromisoformat(job_state_data["updated_at"])
            
            job_state = JobState()
            job_state.deserialize(job_state_data)
            basic_data["job_state"] = job_state
        
        # 调用父类的 deserialize 处理基本字段
        super().deserialize(basic_data)
        
        # 恢复 routines
        if "routines" in data:
            routines_data = data["routines"]
            self.routines = {}
            
            # 第一遍：创建所有 routine 实例
            for routine_id, routine_data in routines_data.items():
                class_info = routine_data.get("_class_info", {})
                routine_class = load_routine_class(class_info)
                
                if routine_class:
                    # 创建 routine 实例
                    routine = routine_class()
                    # 反序列化 routine（不包括 slots 和 events 的引用）
                    routine.deserialize(routine_data)
                    self.routines[routine_id] = routine
                else:
                    # 如果无法加载类，创建一个基本的 Routine2 实例
                    # 但仍然尝试恢复 slots 和 events
                    from flowforge.routine import Routine2
                    routine = Routine2()
                    routine._id = routine_data.get("_id", routine_id)
                    routine._stats = routine_data.get("_stats", {})
                    # 恢复 slots 和 events 的基本结构
                    if "_slots" in routine_data:
                        from flowforge.slot import Slot
                        for slot_name, slot_data in routine_data["_slots"].items():
                            slot = Slot()
                            slot.name = slot_data.get("name", slot_name)
                            slot._data = slot_data.get("_data", {})
                            slot.merge_strategy = slot_data.get("merge_strategy", "override")
                            slot.routine = routine
                            if "_handler_metadata" in slot_data:
                                slot._handler_metadata = slot_data["_handler_metadata"]
                            routine._slots[slot_name] = slot
                    if "_events" in routine_data:
                        from flowforge.event import Event
                        for event_name, event_data in routine_data["_events"].items():
                            event = Event()
                            event.deserialize(event_data)
                            event.routine = routine
                            routine._events[event_name] = event
                    self.routines[routine_id] = routine
            
            # 第二遍：恢复 slots 的 handler 和 merge_strategy
            for routine_id, routine_data in routines_data.items():
                routine = self.routines.get(routine_id)
                if not routine:
                    continue
                
                # 恢复 slots 的 handler
                if "_slots" in routine_data:
                    for slot_name, slot_data in routine_data["_slots"].items():
                        slot = routine._slots.get(slot_name)
                        if slot:
                            # 恢复 handler
                            if "_handler_metadata" in slot_data:
                                handler = deserialize_callable(
                                    slot_data["_handler_metadata"],
                                    {"routines": self.routines}
                                )
                                if handler:
                                    slot.handler = handler
                            
                            # 恢复 merge_strategy
                            if "_merge_strategy_metadata" in slot_data:
                                strategy = deserialize_callable(
                                    slot_data["_merge_strategy_metadata"],
                                    {"routines": self.routines}
                                )
                                if strategy:
                                    slot.merge_strategy = strategy
                            
                            # 清理临时数据
                            if hasattr(slot, "_serialized_data"):
                                delattr(slot, "_serialized_data")
        
        # 恢复 connections
        if "connections" in data:
            from flowforge.connection import Connection
            
            self.connections = []
            
            for conn_data in data["connections"]:
                connection = Connection()
                connection.deserialize(conn_data)
                
                # 重建引用关系
                source_routine_id = getattr(connection, "_source_routine_id", None)
                source_event_name = getattr(connection, "_source_event_name", None)
                target_routine_id = getattr(connection, "_target_routine_id", None)
                target_slot_name = getattr(connection, "_target_slot_name", None)
                
                if source_routine_id and source_event_name:
                    source_routine = self.routines.get(source_routine_id)
                    if source_routine:
                        source_event = source_routine.get_event(source_event_name)
                        if source_event:
                            connection.source_event = source_event
                
                if target_routine_id and target_slot_name:
                    target_routine = self.routines.get(target_routine_id)
                    if target_routine:
                        target_slot = target_routine.get_slot(target_slot_name)
                        if target_slot:
                            connection.target_slot = target_slot
                
                # 如果成功重建引用，添加到 connections
                if connection.source_event and connection.target_slot:
                    # 建立双向连接（如果还没有建立）
                    if connection.target_slot not in connection.source_event.connected_slots:
                        connection.source_event.connect(connection.target_slot)
                    if connection.source_event not in connection.target_slot.connected_events:
                        connection.target_slot.connect(connection.source_event)
                    
                    self.connections.append(connection)
                    # 重建映射
                    key = (connection.source_event, connection.target_slot)
                    self._event_slot_connections[key] = connection


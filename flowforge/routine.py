"""
Routine2 基类

改进的 Routine 机制，支持 slots（输入插槽）和 events（输出事件）。
"""
from __future__ import annotations
import uuid
from typing import Dict, Any, Callable, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from flowforge.slot import Slot
    from flowforge.event import Event
    from flowforge.flow import Flow

from flowforge.utils.serializable import register_serializable, Serializable
from flowforge.serialization_utils import get_routine_class_info


@register_serializable
class Routine2(Serializable):
    """
    改进的 Routine 基类
    
    特性：
    - 支持 slots（输入插槽）
    - 支持 events（输出事件）
    - 提供 stats() 方法返回状态字典
    """
    
    def __init__(self):
        """初始化 Routine2 对象"""
        super().__init__()
        self._id: str = hex(id(self))
        self._slots: Dict[str, 'Slot'] = {}  # 插槽字典
        self._events: Dict[str, 'Event'] = {}  # 事件字典
        self._stats: Dict[str, Any] = {}  # 状态字典
        
        # 注册可序列化字段
        self.add_serializable_fields(["_id", "_stats", "_slots", "_events"])
    
    def __repr__(self) -> str:
        """返回对象的字符串表示"""
        return f"{self.__class__.__name__}[{self._id}]"
    
    def define_slot(
        self,
        name: str,
        handler: Optional[Callable] = None,
        merge_strategy: str = "override"
    ) -> 'Slot':
        """
        定义一个输入插槽
        
        Args:
            name: 插槽名称
            handler: 处理函数，当插槽接收到数据时调用
            merge_strategy: 合并策略 ("override", "append", 或自定义函数)
        
        Returns:
            Slot 对象
        
        Raises:
            ValueError: 如果插槽名称已存在
        """
        if name in self._slots:
            raise ValueError(f"Slot '{name}' already exists in {self}")
        
        # 延迟导入避免循环依赖
        from flowforge.slot import Slot
        
        slot = Slot(name, self, handler, merge_strategy)
        self._slots[name] = slot
        return slot
    
    def define_event(
        self,
        name: str,
        output_params: Optional[List[str]] = None
    ) -> 'Event':
        """
        定义一个输出事件
        
        Args:
            name: 事件名称
            output_params: 输出参数列表（可选，用于文档化）
        
        Returns:
            Event 对象
        
        Raises:
            ValueError: 如果事件名称已存在
        """
        if name in self._events:
            raise ValueError(f"Event '{name}' already exists in {self}")
        
        # 延迟导入避免循环依赖
        from flowforge.event import Event
        
        event = Event(name, self, output_params or [])
        self._events[name] = event
        return event
    
    def emit(self, event_name: str, flow: Optional['Flow'] = None, **kwargs) -> None:
        """
        触发一个事件
        
        Args:
            event_name: 事件名称
            flow: Flow 对象（用于参数映射，可选，如果不提供会尝试从上下文获取）
            **kwargs: 传递给事件的数据
        
        Raises:
            ValueError: 如果事件不存在
        """
        if event_name not in self._events:
            raise ValueError(f"Event '{event_name}' does not exist in {self}")
        
        event = self._events[event_name]
        
        # 如果没有提供 flow，尝试从上下文获取
        if flow is None and hasattr(self, '_current_flow'):
            flow = getattr(self, '_current_flow', None)
        
        event.emit(flow=flow, **kwargs)
        
        # 更新状态
        self._stats.setdefault("emitted_events", []).append({
            "event": event_name,
            "data": kwargs
        })
        
        # 如果 flow 存在，记录执行历史
        if flow is not None:
            if flow.job_state is not None:
                flow.job_state.record_execution(self._id, event_name, kwargs)
            
            # 记录到执行跟踪器
            if flow.execution_tracker is not None:
                # 查找目标 routine（通过连接的 slots）
                target_routine_id = None
                event_obj = self._events.get(event_name)
                if event_obj and event_obj.connected_slots:
                    # 获取第一个连接的 slot 的 routine
                    target_routine_id = event_obj.connected_slots[0].routine._id
                
                flow.execution_tracker.record_event(
                    self._id, event_name, target_routine_id, kwargs
                )
    
    def stats(self) -> Dict[str, Any]:
        """
        返回状态字典的副本
        
        Returns:
            状态字典的副本
        """
        return self._stats.copy()
    
    def __call__(self, **kwargs) -> None:
        """
        执行 routine
        
        子类应该重写此方法来实现具体的执行逻辑
        
        Args:
            **kwargs: 传递给 routine 的参数
        """
        # 更新状态
        self._stats["called"] = True
        self._stats["call_count"] = self._stats.get("call_count", 0) + 1
        
        # 子类可以重写此方法来实现具体逻辑
        pass
    
    def get_slot(self, name: str) -> Optional['Slot']:
        """
        获取指定的插槽
        
        Args:
            name: 插槽名称
        
        Returns:
            Slot 对象，如果不存在则返回 None
        """
        return self._slots.get(name)
    
    def get_event(self, name: str) -> Optional['Event']:
        """
        获取指定的事件
        
        Args:
            name: 事件名称
        
        Returns:
            Event 对象，如果不存在则返回 None
        """
        return self._events.get(name)
    
    def serialize(self) -> Dict[str, Any]:
        """
        序列化 Routine2，包括类信息和状态
        
        Returns:
            序列化后的字典
        """
        data = super().serialize()
        
        # 添加类信息
        class_info = get_routine_class_info(self)
        data["_class_info"] = class_info
        
        # 序列化 slots（保存名称和元数据，不保存 handler 函数）
        slots_data = {}
        for name, slot in self._slots.items():
            slot_data = slot.serialize()
            # 保存 handler 元数据
            from flowforge.serialization_utils import serialize_callable
            handler_data = serialize_callable(slot.handler)
            if handler_data:
                slot_data["_handler_metadata"] = handler_data
            slots_data[name] = slot_data
        data["_slots"] = slots_data
        
        # 序列化 events
        events_data = {}
        for name, event in self._events.items():
            events_data[name] = event.serialize()
        data["_events"] = events_data
        
        return data
    
    def deserialize(self, data: Dict[str, Any]) -> None:
        """
        反序列化 Routine2
        
        Args:
            data: 序列化数据
        """
        # 先反序列化基本字段（不包括 _slots 和 _events，它们需要特殊处理）
        basic_data = {k: v for k, v in data.items() if k not in ["_slots", "_events", "_class_info"]}
        super().deserialize(basic_data)
        
        # 恢复 slots（基本结构，handler 在 Flow.deserialize 中恢复）
        if "_slots" in data:
            from flowforge.slot import Slot
            
            self._slots = {}
            for name, slot_data in data["_slots"].items():
                slot = Slot()
                slot.name = slot_data.get("name", name)
                slot._data = slot_data.get("_data", {})
                slot.merge_strategy = slot_data.get("merge_strategy", "override")
                slot.routine = self
                # 保存 handler 元数据以便后续恢复
                if "_handler_metadata" in slot_data:
                    slot._handler_metadata = slot_data["_handler_metadata"]
                if "_merge_strategy_metadata" in slot_data:
                    slot._merge_strategy_metadata = slot_data["_merge_strategy_metadata"]
                self._slots[name] = slot
        
        # 恢复 events
        if "_events" in data:
            from flowforge.event import Event
            
            self._events = {}
            for name, event_data in data["_events"].items():
                event = Event()
                event.deserialize(event_data)
                event.routine = self
                self._events[name] = event


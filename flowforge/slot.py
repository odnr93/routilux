"""
Slot 类

输入插槽，用于接收来自其他 routine 的数据。
"""
from __future__ import annotations
from typing import Callable, Optional, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from flowforge.routine import Routine2
    from flowforge.event import Event

from flowforge.utils.serializable import register_serializable, Serializable
from flowforge.serialization_utils import serialize_callable, deserialize_callable


@register_serializable
class Slot(Serializable):
    """
    输入插槽
    
    一个 slot 可以连接到多个 events（多对多关系）
    """
    
    def __init__(
        self,
        name: str = "",
        routine: Optional['Routine2'] = None,
        handler: Optional[Callable] = None,
        merge_strategy: str = "override"
    ):
        """
        初始化 Slot
        
        Args:
            name: 插槽名称
            routine: 所属的 Routine2 对象
            handler: 处理函数
            merge_strategy: 合并策略 ("override", "append", 或自定义函数)
        """
        super().__init__()
        self.name: str = name
        self.routine: 'Routine2' = routine
        self.handler: Optional[Callable] = handler
        self.merge_strategy: Any = merge_strategy
        self.connected_events: List['Event'] = []  # 连接的 events
        self._data: Dict[str, Any] = {}  # 存储的数据
        
        # 注册可序列化字段
        self.add_serializable_fields(["name", "_data", "merge_strategy"])
    
    def __repr__(self) -> str:
        """返回对象的字符串表示"""
        return f"Slot[{self.routine._id}.{self.name}]"
    
    def connect(self, event: 'Event', param_mapping: Optional[Dict[str, str]] = None) -> None:
        """
        连接到一个 event
        
        Args:
            event: 要连接的 Event 对象
            param_mapping: 参数映射字典，将 event 的参数名映射到 slot 的参数名
        """
        if event not in self.connected_events:
            self.connected_events.append(event)
            # 双向连接
            if self not in event.connected_slots:
                event.connected_slots.append(self)
    
    def disconnect(self, event: 'Event') -> None:
        """
        断开与 event 的连接
        
        Args:
            event: 要断开的 Event 对象
        """
        if event in self.connected_events:
            self.connected_events.remove(event)
            # 双向断开
            if self in event.connected_slots:
                event.connected_slots.remove(self)
    
    def receive(self, data: Dict[str, Any]) -> None:
        """
        接收数据并调用 handler
        
        Args:
            data: 接收到的数据字典
        """
        # 合并数据
        merged_data = self._merge_data(data)
        
        # 调用 handler
        if self.handler is not None:
            try:
                import inspect
                sig = inspect.signature(self.handler)
                params = list(sig.parameters.keys())
                
                # 如果 handler 接受 **kwargs，直接传递所有数据
                if self._is_kwargs_handler(self.handler):
                    self.handler(**merged_data)
                elif len(params) == 1 and params[0] == 'data':
                    # handler 只接受一个 'data' 参数，传递整个字典
                    self.handler(merged_data)
                elif len(params) == 1:
                    # handler 只接受一个参数，尝试传递匹配的值
                    param_name = params[0]
                    if param_name in merged_data:
                        self.handler(merged_data[param_name])
                    else:
                        # 如果没有匹配的参数，传递整个字典
                        self.handler(merged_data)
                else:
                    # 多个参数，尝试匹配
                    matched_params = {}
                    for param_name in params:
                        if param_name in merged_data:
                            matched_params[param_name] = merged_data[param_name]
                    
                    if matched_params:
                        self.handler(**matched_params)
                    else:
                        # 如果没有匹配，传递整个字典作为第一个参数
                        self.handler(merged_data)
            except Exception as e:
                # 记录异常但不中断流程
                import logging
                logging.exception(f"Error in slot {self} handler: {e}")
                self.routine._stats.setdefault("errors", []).append({
                    "slot": self.name,
                    "error": str(e)
                })
    
    def _merge_data(self, new_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并新数据到现有数据
        
        Args:
            new_data: 新数据
        
        Returns:
            合并后的数据
        """
        if self.merge_strategy == "override":
            # 覆盖策略：新数据覆盖旧数据
            self._data = new_data.copy()
            return self._data
        elif self.merge_strategy == "append":
            # 追加策略：数据追加到列表
            merged = {}
            for key, value in new_data.items():
                if key not in self._data:
                    self._data[key] = []
                if not isinstance(self._data[key], list):
                    self._data[key] = [self._data[key]]
                self._data[key].append(value)
                merged[key] = self._data[key]
            return merged
        elif callable(self.merge_strategy):
            # 自定义合并函数
            return self.merge_strategy(self._data, new_data)
        else:
            # 默认覆盖
            self._data = new_data.copy()
            return self._data
    
    @staticmethod
    def _is_kwargs_handler(handler: Callable) -> bool:
        """
        检查 handler 是否接受 **kwargs
        
        Args:
            handler: 处理函数
        
        Returns:
            如果接受 **kwargs 返回 True
        """
        import inspect
        sig = inspect.signature(handler)
        for param in sig.parameters.values():
            if param.kind == inspect.Parameter.VAR_KEYWORD:
                return True
        return False
    
    def serialize(self) -> Dict[str, Any]:
        """
        序列化 Slot
        
        Returns:
            序列化后的字典
        """
        data = super().serialize()
        
        # 保存 routine 引用（通过 routine_id）
        if self.routine:
            data["_routine_id"] = self.routine._id
        
        # 保存 handler 元数据（不直接序列化函数）
        if self.handler:
            handler_data = serialize_callable(self.handler)
            if handler_data:
                data["_handler_metadata"] = handler_data
        
        # 处理 merge_strategy（如果是函数，也需要序列化元数据）
        if callable(self.merge_strategy) and self.merge_strategy not in ["override", "append"]:
            strategy_data = serialize_callable(self.merge_strategy)
            if strategy_data:
                data["_merge_strategy_metadata"] = strategy_data
                data["merge_strategy"] = "_custom"
        
        return data
    
    def deserialize(self, data: Dict[str, Any]) -> None:
        """
        反序列化 Slot
        
        Args:
            data: 序列化数据
        """
        # 保存 routine_id 以便后续恢复引用
        routine_id = data.pop("_routine_id", None)
        handler_metadata = data.pop("_handler_metadata", None)
        strategy_metadata = data.pop("_merge_strategy_metadata", None)
        
        # 反序列化基本字段
        super().deserialize(data)
        
        # routine 引用需要在 Flow 恢复时重建
        # handler 和 merge_strategy 也需要在恢复时重建
        if handler_metadata:
            self._handler_metadata = handler_metadata
        if strategy_metadata:
            self._merge_strategy_metadata = strategy_metadata
        if routine_id:
            self._routine_id = routine_id


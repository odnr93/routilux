"""
Connection 类

连接对象，表示一个 event 到 slot 的连接。
"""
from __future__ import annotations
from typing import Dict, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from flowforge.event import Event
    from flowforge.slot import Slot

from flowforge.utils.serializable import register_serializable, Serializable


@register_serializable
class Connection(Serializable):
    """
    连接对象
    
    表示一个 event 到 slot 的连接
    """
    
    def __init__(
        self,
        source_event: Optional['Event'] = None,
        target_slot: Optional['Slot'] = None,
        param_mapping: Optional[Dict[str, str]] = None
    ):
        """
        初始化 Connection
        
        Args:
            source_event: 源 Event 对象
            target_slot: 目标 Slot 对象
            param_mapping: 参数映射字典，将 source 的参数名映射到 target 的参数名
        """
        super().__init__()
        self.source_event: Optional['Event'] = source_event
        self.target_slot: Optional['Slot'] = target_slot
        self.param_mapping: Dict[str, str] = param_mapping or {}  # 参数映射
        
        # 建立连接（如果提供了 event 和 slot）
        if source_event is not None and target_slot is not None:
            source_event.connect(target_slot)
        
        # 注册可序列化字段
        self.add_serializable_fields(["param_mapping"])
    
    def serialize(self) -> Dict[str, Any]:
        """
        序列化 Connection
        
        Returns:
            序列化后的字典
        """
        data = super().serialize()
        
        # 保存引用信息（通过 routine_id + event/slot name）
        if self.source_event and self.source_event.routine:
            data["_source_routine_id"] = self.source_event.routine._id
            data["_source_event_name"] = self.source_event.name
        
        if self.target_slot and self.target_slot.routine:
            data["_target_routine_id"] = self.target_slot.routine._id
            data["_target_slot_name"] = self.target_slot.name
        
        return data
    
    def deserialize(self, data: Dict[str, Any]) -> None:
        """
        反序列化 Connection
        
        Args:
            data: 序列化数据
        """
        # 保存引用信息以便后续恢复
        source_routine_id = data.pop("_source_routine_id", None)
        source_event_name = data.pop("_source_event_name", None)
        target_routine_id = data.pop("_target_routine_id", None)
        target_slot_name = data.pop("_target_slot_name", None)
        
        # 反序列化基本字段
        super().deserialize(data)
        
        # 保存引用信息，在 Flow 恢复时重建
        if source_routine_id:
            self._source_routine_id = source_routine_id
        if source_event_name:
            self._source_event_name = source_event_name
        if target_routine_id:
            self._target_routine_id = target_routine_id
        if target_slot_name:
            self._target_slot_name = target_slot_name
    
    def __repr__(self) -> str:
        """返回对象的字符串表示"""
        return f"Connection[{self.source_event} -> {self.target_slot}]"
    
    def activate(self, data: Dict[str, Any]) -> None:
        """
        激活连接，传递数据
        
        Args:
            data: 要传递的数据字典
        """
        # 应用参数映射
        mapped_data = self._apply_mapping(data)
        
        # 传递到目标 slot
        self.target_slot.receive(mapped_data)
    
    def _apply_mapping(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用参数映射
        
        Args:
            data: 原始数据
        
        Returns:
            映射后的数据
        """
        if not self.param_mapping:
            # 没有映射，直接返回
            return data
        
        mapped_data = {}
        for source_key, target_key in self.param_mapping.items():
            if source_key in data:
                mapped_data[target_key] = data[source_key]
        
        # 对于没有映射的参数，如果目标 slot 的 handler 需要，也传递
        # 这里简化处理：传递所有未映射的参数（如果目标参数名与源参数名相同）
        for key, value in data.items():
            if key not in self.param_mapping.values() and key not in mapped_data:
                # 检查是否与目标参数名匹配（这里简化，实际应该检查 handler 签名）
                mapped_data[key] = value
        
        return mapped_data
    
    def disconnect(self) -> None:
        """断开连接"""
        self.source_event.disconnect(self.target_slot)


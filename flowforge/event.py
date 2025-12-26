"""
Event 类

输出事件，用于向其他 routine 发送数据。
"""
from __future__ import annotations
from typing import List, Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from flowforge.routine import Routine
    from flowforge.slot import Slot
    from flowforge.flow import Flow

from flowforge.utils.serializable import register_serializable, Serializable


@register_serializable
class Event(Serializable):
    """
    输出事件
    
    一个 event 可以连接到多个 slots（多对多关系）
    """
    
    def __init__(
        self,
        name: str = "",
        routine: Optional['Routine'] = None,
        output_params: Optional[List[str]] = None
    ):
        """
        初始化 Event
        
        Args:
            name: 事件名称
            routine: 所属的 Routine 对象
            output_params: 输出参数列表（用于文档化）
        """
        super().__init__()
        self.name: str = name
        self.routine: 'Routine' = routine
        self.output_params: List[str] = output_params or []  # 输出参数列表
        self.connected_slots: List['Slot'] = []  # 连接的 slots
        
        # 注册可序列化字段
        self.add_serializable_fields(["name", "output_params"])
    
    def serialize(self) -> Dict[str, Any]:
        """
        序列化 Event
        
        Returns:
            序列化后的字典
        """
        data = super().serialize()
        
        # 保存 routine 引用（通过 routine_id）
        if self.routine:
            data["_routine_id"] = self.routine._id
        
        return data
    
    def deserialize(self, data: Dict[str, Any]) -> None:
        """
        反序列化 Event
        
        Args:
            data: 序列化数据
        """
        # 保存 routine_id 以便后续恢复引用
        routine_id = data.pop("_routine_id", None)
        
        # 反序列化基本字段
        super().deserialize(data)
        
        # routine 引用需要在 Flow 恢复时重建
        if routine_id:
            self._routine_id = routine_id
    
    def __repr__(self) -> str:
        """返回对象的字符串表示"""
        return f"Event[{self.routine._id}.{self.name}]"
    
    def connect(self, slot: 'Slot', param_mapping: Optional[Dict[str, str]] = None) -> None:
        """
        连接到一个 slot
        
        Args:
            slot: 要连接的 Slot 对象
            param_mapping: 参数映射字典（由 Connection 管理，这里只是建立连接）
        """
        if slot not in self.connected_slots:
            self.connected_slots.append(slot)
            # 双向连接
            if self not in slot.connected_events:
                slot.connected_events.append(self)
    
    def disconnect(self, slot: 'Slot') -> None:
        """
        断开与 slot 的连接
        
        Args:
            slot: 要断开的 Slot 对象
        """
        if slot in self.connected_slots:
            self.connected_slots.remove(slot)
            # 双向断开
            if self in slot.connected_events:
                slot.connected_events.remove(self)
    
    def emit(self, flow: Optional['Flow'] = None, **kwargs) -> None:
        """
        触发事件，向所有连接的 slots 发送数据
        
        Args:
            flow: Flow 对象（用于查找 Connection 以应用参数映射）
            **kwargs: 要传递的数据
        """
        # 向所有连接的 slots 发送数据
        for slot in self.connected_slots:
            # 如果提供了 flow，尝试通过 Connection 传递（应用参数映射）
            if flow is not None:
                connection = flow._find_connection(self, slot)
                if connection is not None:
                    # 通过 Connection 传递，应用参数映射
                    connection.activate(kwargs)
                else:
                    # 没有找到 Connection，直接传递
                    slot.receive(kwargs)
            else:
                # 没有提供 flow，直接传递
                slot.receive(kwargs)


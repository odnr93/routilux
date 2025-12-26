"""
JobState 和 ExecutionRecord 类

用于记录 flow 的执行状态。
"""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from flowforge.utils.serializable import register_serializable, Serializable
import json


@register_serializable
class ExecutionRecord(Serializable):
    """
    执行记录
    
    记录一次 routine 的执行
    """
    
    def __init__(
        self,
        routine_id: str = "",
        event_name: str = "",
        data: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        初始化 ExecutionRecord
        
        Args:
            routine_id: Routine ID
            event_name: 事件名称
            data: 传递的数据
            timestamp: 时间戳（如果为 None 则使用当前时间）
        """
        super().__init__()
        self.routine_id: str = routine_id
        self.event_name: str = event_name
        self.data: Dict[str, Any] = data or {}
        self.timestamp: datetime = timestamp or datetime.now()
        
        # 注册可序列化字段
        self.add_serializable_fields(["routine_id", "event_name", "data", "timestamp"])
    
    def __repr__(self) -> str:
        """返回对象的字符串表示"""
        return f"ExecutionRecord[{self.routine_id}.{self.event_name}@{self.timestamp}]"
    
    def serialize(self) -> Dict[str, Any]:
        """序列化，处理 datetime"""
        data = super().serialize()
        # 将 datetime 转换为字符串
        if isinstance(data.get("timestamp"), datetime):
            data["timestamp"] = data["timestamp"].isoformat()
        return data
    
    def deserialize(self, data: Dict[str, Any]) -> None:
        """反序列化，处理 datetime"""
        # 将字符串转换为 datetime
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        super().deserialize(data)


@register_serializable
class JobState(Serializable):
    """
    作业状态
    
    记录 flow 的执行状态
    """
    
    def __init__(self, flow_id: str = ""):
        """
        初始化 JobState
        
        Args:
            flow_id: Flow ID
        """
        super().__init__()
        self.flow_id: str = flow_id
        self.job_id: str = str(uuid.uuid4())
        self.status: str = "pending"  # pending, running, paused, completed, failed, cancelled
        self.pause_points: List[Dict[str, Any]] = []  # 暂停点列表
        self.current_routine_id: Optional[str] = None  # 当前执行的 routine
        self.routine_states: Dict[str, Dict[str, Any]] = {}  # routine_id -> state
        self.execution_history: List[ExecutionRecord] = []  # 执行历史
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()
        
        # 注册可序列化字段
        self.add_serializable_fields([
            "flow_id", "job_id", "status", "current_routine_id",
            "routine_states", "execution_history", "created_at", "updated_at", "pause_points"
        ])
    
    def __repr__(self) -> str:
        """返回对象的字符串表示"""
        return f"JobState[{self.job_id}:{self.status}]"
    
    def update_routine_state(self, routine_id: str, state: Dict[str, Any]) -> None:
        """
        更新某个 routine 的状态
        
        Args:
            routine_id: Routine ID
            state: 状态字典
        """
        self.routine_states[routine_id] = state.copy()
        self.updated_at = datetime.now()
    
    def get_routine_state(self, routine_id: str) -> Optional[Dict[str, Any]]:
        """
        获取某个 routine 的状态
        
        Args:
            routine_id: Routine ID
        
        Returns:
            状态字典，如果不存在则返回 None
        """
        return self.routine_states.get(routine_id)
    
    def record_execution(
        self,
        routine_id: str,
        event_name: str,
        data: Dict[str, Any]
    ) -> None:
        """
        记录执行历史
        
        Args:
            routine_id: Routine ID
            event_name: 事件名称
            data: 传递的数据
        """
        record = ExecutionRecord(routine_id, event_name, data)
        self.execution_history.append(record)
        self.updated_at = datetime.now()
    
    def get_execution_history(
        self,
        routine_id: Optional[str] = None
    ) -> List[ExecutionRecord]:
        """
        获取执行历史
        
        Args:
            routine_id: 如果指定，只返回该 routine 的历史
        
        Returns:
            执行历史列表（按时间排序）
        """
        if routine_id is None:
            history = self.execution_history
        else:
            history = [
                r for r in self.execution_history
                if r.routine_id == routine_id
            ]
        
        # 按时间排序
        return sorted(history, key=lambda x: x.timestamp)
    
    def _set_paused(self, reason: str = "", checkpoint: Optional[Dict[str, Any]] = None) -> None:
        """
        内部方法：设置暂停状态（由 Flow 调用）
        
        Args:
            reason: 暂停原因
            checkpoint: 检查点数据
        """
        self.status = "paused"
        pause_point = {
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "current_routine_id": self.current_routine_id,
            "checkpoint": checkpoint or {}
        }
        self.pause_points.append(pause_point)
        self.updated_at = datetime.now()
    
    def _set_running(self) -> None:
        """
        内部方法：设置运行状态（由 Flow 调用）
        """
        if self.status == "paused":
            self.status = "running"
            self.updated_at = datetime.now()
    
    def _set_cancelled(self, reason: str = "") -> None:
        """
        内部方法：设置取消状态（由 Flow 调用）
        
        Args:
            reason: 取消原因
        """
        self.status = "cancelled"
        self.updated_at = datetime.now()
        if reason:
            self.routine_states.setdefault("_cancellation", {})["reason"] = reason
    
    def save(self, filepath: str) -> None:
        """
        持久化状态到文件
        
        Args:
            filepath: 文件路径
        """
        import os
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
        
        data = self.serialize()
        # 处理 datetime
        if isinstance(data.get("created_at"), datetime):
            data["created_at"] = data["created_at"].isoformat()
        if isinstance(data.get("updated_at"), datetime):
            data["updated_at"] = data["updated_at"].isoformat()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, filepath: str) -> 'JobState':
        """
        从文件恢复状态
        
        Args:
            filepath: 文件路径
        
        Returns:
            JobState 对象
        
        Raises:
            FileNotFoundError: 如果文件不存在
            ValueError: 如果文件格式不正确
        """
        import os
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"JobState file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 验证数据格式
        if "_type" not in data or data["_type"] != "JobState":
            raise ValueError(f"Invalid JobState file format: {filepath}")
        
        # 创建对象
        job_state = cls(data.get("flow_id", ""))
        job_state.deserialize(data)
        
        # 处理 datetime
        if isinstance(job_state.created_at, str):
            job_state.created_at = datetime.fromisoformat(job_state.created_at)
        if isinstance(job_state.updated_at, str):
            job_state.updated_at = datetime.fromisoformat(job_state.updated_at)
        
        return job_state
    
    def serialize(self) -> Dict[str, Any]:
        """序列化，处理 datetime 和 ExecutionRecord"""
        data = super().serialize()
        # 处理 datetime
        if isinstance(data.get("created_at"), datetime):
            data["created_at"] = data["created_at"].isoformat()
        if isinstance(data.get("updated_at"), datetime):
            data["updated_at"] = data["updated_at"].isoformat()
        return data
    
    def deserialize(self, data: Dict[str, Any]) -> None:
        """反序列化，处理 datetime 和 ExecutionRecord"""
        # 处理 datetime
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("updated_at"), str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        
        # 处理 ExecutionRecord 列表
        if "execution_history" in data and isinstance(data["execution_history"], list):
            records = []
            for record_data in data["execution_history"]:
                if isinstance(record_data, dict):
                    record = ExecutionRecord(
                        record_data.get("routine_id", ""),
                        record_data.get("event_name", ""),
                        record_data.get("data", {}),
                        datetime.fromisoformat(record_data["timestamp"]) if isinstance(record_data.get("timestamp"), str) else None
                    )
                    records.append(record)
            data["execution_history"] = records
        
        super().deserialize(data)


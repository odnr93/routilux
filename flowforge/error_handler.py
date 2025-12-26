"""
错误处理策略

定义错误处理策略和重试机制。
"""
from __future__ import annotations
from typing import Callable, Optional, Dict, Any, List, TYPE_CHECKING
from enum import Enum
import time
import logging
from flowforge.utils.serializable import register_serializable, Serializable

if TYPE_CHECKING:
    from flowforge.routine import Routine2
    from flowforge.flow import Flow

logger = logging.getLogger(__name__)


class ErrorStrategy(Enum):
    """错误处理策略"""
    STOP = "stop"  # 停止执行
    CONTINUE = "continue"  # 继续执行下一个
    RETRY = "retry"  # 重试
    SKIP = "skip"  # 跳过


@register_serializable
class ErrorHandler(Serializable):
    """
    错误处理器
    
    定义错误处理策略和重试机制
    """
    
    def __init__(
        self,
        strategy: str = "stop",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        retry_backoff: float = 2.0,
        retryable_exceptions: Optional[tuple] = None
    ):
        """
        初始化 ErrorHandler
        
        Args:
            strategy: 错误处理策略
            max_retries: 最大重试次数
            retry_delay: 初始重试延迟（秒）
            retry_backoff: 重试延迟增长倍数
            retryable_exceptions: 可重试的异常类型
        """
        super().__init__()
        # 支持字符串或枚举
        if isinstance(strategy, str):
            self.strategy: ErrorStrategy = ErrorStrategy(strategy)
        else:
            self.strategy: ErrorStrategy = strategy
        self.max_retries: int = max_retries
        self.retry_delay: float = retry_delay
        self.retry_backoff: float = retry_backoff
        self.retryable_exceptions: tuple = retryable_exceptions or (Exception,)
        self.retry_count: int = 0
        
        # 注册可序列化字段
        self.add_serializable_fields([
            "strategy", "max_retries", "retry_delay", "retry_backoff", "retry_count"
        ])
    
    def handle_error(
        self,
        error: Exception,
        routine: 'Routine2',
        routine_id: str,
        flow: 'Flow',
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        处理错误
        
        Args:
            error: 异常对象
            routine: 出错的 Routine
            routine_id: Routine ID
            flow: Flow 对象
            context: 上下文信息
        
        Returns:
            如果应该继续执行返回 True，否则返回 False
        """
        context = context or {}
        
        if self.strategy == ErrorStrategy.STOP:
            logger.error(f"Error in routine {routine_id}: {error}. Stopping execution.")
            return False
        
        elif self.strategy == ErrorStrategy.CONTINUE:
            logger.warning(f"Error in routine {routine_id}: {error}. Continuing execution.")
            # 记录错误但继续执行
            if flow.job_state:
                flow.job_state.record_execution(routine_id, "error_continued", {
                    "error": str(error),
                    "error_type": type(error).__name__
                })
            return True
        
        elif self.strategy == ErrorStrategy.RETRY:
            if self.retry_count < self.max_retries:
                self.retry_count += 1
                delay = self.retry_delay * (self.retry_backoff ** (self.retry_count - 1))
                logger.warning(
                    f"Error in routine {routine_id}: {error}. "
                    f"Retrying ({self.retry_count}/{self.max_retries}) after {delay}s..."
                )
                time.sleep(delay)
                return True  # 返回 True 表示应该重试
            else:
                logger.error(
                    f"Error in routine {routine_id}: {error}. "
                    f"Max retries ({self.max_retries}) exceeded. Stopping."
                )
                return False
        
        elif self.strategy == ErrorStrategy.SKIP:
            logger.warning(f"Error in routine {routine_id}: {error}. Skipping routine.")
            # 标记为跳过
            if flow.job_state:
                flow.job_state.update_routine_state(routine_id, {
                    "status": "skipped",
                    "error": str(error)
                })
            return True
        
        return False
    
    def reset(self) -> None:
        """重置重试计数"""
        self.retry_count = 0


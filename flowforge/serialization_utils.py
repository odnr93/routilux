"""
序列化工具函数

用于处理 Routine2、Flow 等对象的序列化和反序列化。
"""
import importlib
import inspect
from typing import Dict, Any, Optional, Callable, Type


def serialize_callable(callable_obj: Optional[Callable]) -> Optional[Dict[str, Any]]:
    """
    序列化可调用对象（函数或方法）
    
    Args:
        callable_obj: 要序列化的可调用对象
    
    Returns:
        序列化后的字典，如果无法序列化则返回 None
    """
    if callable_obj is None:
        return None
    
    try:
        # 尝试获取函数信息
        if inspect.ismethod(callable_obj):
            # 方法
            return {
                "_type": "method",
                "class_name": callable_obj.__self__.__class__.__name__,
                "method_name": callable_obj.__name__,
                "object_id": getattr(callable_obj.__self__, "_id", None)
            }
        elif inspect.isfunction(callable_obj):
            # 函数
            module = inspect.getmodule(callable_obj)
            if module:
                return {
                    "_type": "function",
                    "module": module.__name__,
                    "name": callable_obj.__name__
                }
        elif inspect.isbuiltin(callable_obj):
            # 内置函数
            return {
                "_type": "builtin",
                "name": callable_obj.__name__
            }
    except Exception:
        pass
    
    return None


def deserialize_callable(callable_data: Optional[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> Optional[Callable]:
    """
    反序列化可调用对象
    
    Args:
        callable_data: 序列化的可调用对象数据
        context: 上下文信息（如 routine 对象字典）
    
    Returns:
        可调用对象，如果无法反序列化则返回 None
    """
    if callable_data is None:
        return None
    
    context = context or {}
    
    try:
        callable_type = callable_data.get("_type")
        
        if callable_type == "method":
            # 恢复方法
            class_name = callable_data.get("class_name")
            method_name = callable_data.get("method_name")
            object_id = callable_data.get("object_id")
            
            if object_id and "routines" in context:
                # 从 context 中查找对象
                for routine in context["routines"].values():
                    if hasattr(routine, "_id") and routine._id == object_id:
                        if hasattr(routine, method_name):
                            return getattr(routine, method_name)
        
        elif callable_type == "function":
            # 恢复函数
            module_name = callable_data.get("module")
            function_name = callable_data.get("name")
            
            if module_name and function_name:
                module = importlib.import_module(module_name)
                if hasattr(module, function_name):
                    return getattr(module, function_name)
        
        elif callable_type == "builtin":
            # 内置函数
            name = callable_data.get("name")
            if name:
                return __builtins__.get(name)
    
    except Exception:
        pass
    
    return None


def get_routine_class_info(routine: Any) -> Dict[str, Any]:
    """
    获取 Routine 的类信息
    
    Args:
        routine: Routine2 实例
    
    Returns:
        包含类信息的字典
    """
    cls = routine.__class__
    return {
        "class_name": cls.__name__,
        "module": cls.__module__
    }


def load_routine_class(class_info: Dict[str, Any]) -> Optional[Type]:
    """
    从类信息加载 Routine 类
    
    Args:
        class_info: 包含 class_name 和 module 的字典
    
    Returns:
        Routine 类，如果无法加载则返回 None
    """
    try:
        module_name = class_info.get("module")
        class_name = class_info.get("class_name")
        
        if module_name and class_name:
            module = importlib.import_module(module_name)
            if hasattr(module, class_name):
                return getattr(module, class_name)
    except Exception:
        pass
    
    return None


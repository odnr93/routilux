# flowforge 测试说明

## 测试结构

```
tests/
├── __init__.py              # 测试包初始化
├── conftest.py              # pytest 配置和 fixtures
├── test_routine.py          # Routine 测试
├── test_slot.py             # Slot 测试
├── test_event.py            # Event 测试
├── test_connection.py       # Connection 测试
├── test_flow.py             # Flow 测试
├── test_job_state.py        # JobState 测试
├── test_persistence.py      # 持久化测试
├── test_integration.py      # 集成测试
└── test_resume.py           # 恢复功能测试
```

## 运行测试

### 安装依赖

```bash
pip install pytest pytest-cov pytest-mock
```

### 运行所有测试

```bash
pytest tests/
```

### 运行特定测试文件

```bash
pytest tests/test_routine.py
```

### 运行特定测试用例

```bash
pytest tests/test_routine.py::TestRoutineBasic::test_create_routine
```

### 生成覆盖率报告

```bash
pytest --cov=flowforge --cov-report=html tests/
```

### 详细输出

```bash
pytest -v tests/
```

### 显示打印输出

```bash
pytest -s tests/
```

## 测试说明

### 当前状态

**注意**：当前测试文件中的测试用例都是占位符，因为 `flowforge` 的核心类还没有实现。这些测试用例：

1. 作为实现指南，描述了期望的行为
2. 使用 `pass` 语句，不会实际执行
3. 在实现相应功能后，需要取消注释并实现实际的测试逻辑

### 实现步骤

1. **实现核心类**：
   - `Routine` (routine.py)
   - `Slot` (slot.py)
   - `Event` (event.py)
   - `Connection` (connection.py)
   - `Flow` (flow.py)
   - `JobState` (job_state.py)

2. **更新测试用例**：
   - 取消注释测试代码
   - 导入实际的类
   - 实现测试逻辑
   - 确保测试通过

3. **运行测试**：
   - 逐步运行测试，修复问题
   - 确保所有测试通过
   - 达到 >90% 的代码覆盖率

## 测试覆盖

### 单元测试
- ✅ Routine 基本功能
- ✅ Slot 连接和数据接收
- ✅ Event 连接和触发
- ✅ Connection 参数映射
- ✅ Flow 管理和执行
- ✅ JobState 状态管理

### 集成测试
- ✅ 完整流程执行
- ✅ 错误处理流程
- ✅ 并行处理流程
- ✅ 复杂嵌套流程

### 持久化测试
- ✅ Flow 保存和加载
- ✅ JobState 保存和加载
- ✅ 一致性验证

### 恢复测试
- ✅ 从中间状态恢复
- ✅ 从完成状态恢复
- ✅ 从错误状态恢复
- ✅ 状态一致性验证

## 注意事项

1. **独立性**：所有测试都可以独立运行，不依赖外部服务
2. **临时文件**：使用 `temp_file` fixture 管理临时文件
3. **清理**：测试后自动清理临时文件
4. **Mock**：使用 pytest-mock 进行 mock（如需要）

## 持续集成

测试应该在 CI 环境中自动运行：
- 所有测试必须通过
- 代码覆盖率 > 90%
- 没有 lint 错误


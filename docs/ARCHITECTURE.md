# 系统架构文档

## 概述

多Agent协作需求拆解系统采用管道（Pipeline）模式，通过4个专业Agent依次处理产品需求，最终输出完整的技术方案。

## 架构图

```
输入：产品需求（自然语言）
    ↓
┌─────────────────────────────────────────┐
│  PlannerAgent（规划Agent）              │
│  - 理解需求                             │
│  - 拆解为功能模块                       │
│  - 识别模块依赖关系                     │
└─────────────────────────────────────────┘
    ↓ functional_modules (JSON)
┌─────────────────────────────────────────┐
│  TechAgent（技术Agent）                 │
│  - 为每个模块设计API接口                │
│  - 生成伪代码                           │
│  - 确定数据模型                         │
└─────────────────────────────────────────┘
    ↓ technical_design (JSON)
┌─────────────────────────────────────────┐
│  TestAgent（测试Agent）                 │
│  - 根据接口设计生成测试用例             │
│  - 覆盖正常流程和异常流程               │
│  - 生成测试数据                         │
└─────────────────────────────────────────┘
    ↓ test_plan (JSON)
┌─────────────────────────────────────────┐
│  OutputAgent（输出Agent）               │
│  - 汇总所有结果                         │
│  - 生成最终JSON方案                     │
│  - 可选：创建JIRA任务                   │
└─────────────────────────────────────────┘
    ↓
输出：完整技术方案（JSON格式）
```

## 数据流

系统使用 `PipelineContext` 对象在Agent之间传递状态：

```python
@dataclass
class PipelineContext:
    requirement_id: str
    original_requirement: str
    current_stage: str
    functional_modules: List[Dict]     # PlannerAgent输出
    technical_design: List[Dict]       # TechAgent输出
    test_plan: List[Dict]              # TestAgent输出
    final_result: Dict                 # OutputAgent输出
    jira_task_ids: List[str]
```

## Agent详细说明

### 1. PlannerAgent（规划Agent）

**输入**：需求描述（字符串）
**输出**：功能模块列表（JSON）

**职责**：
- 理解产品需求的核心目标
- 拆解为独立的功能模块
- 识别模块类型和依赖关系
- 估算每个模块的工作量

**输出格式**：
```json
{
  "modules": [
    {
      "module_id": "MOD-001",
      "module_name": "模块名称",
      "module_type": "core|support|integration",
      "description": "模块描述",
      "dependencies": ["MOD-000"],
      "estimated_effort_days": 3.5
    }
  ]
}
```

### 2. TechAgent（技术Agent）

**输入**：功能模块列表
**输出**：技术设计（含API接口和伪代码）

**职责**：
- 为每个模块设计RESTful API接口
- 生成关键逻辑的伪代码
- 确定数据模型和数据库表结构
- 指定需要的第三方服务

**输出格式**：
```json
{
  "module_id": "MOD-001",
  "api_endpoints": [
    {
      "method": "POST",
      "path": "/api/v1/...",
      "description": "...",
      "request_body": {...},
      "response": {...}
    }
  ],
  "pseudo_code": "function...",
  "data_models": [...]
}
```

### 3. TestAgent（测试Agent）

**输入**：技术设计
**输出**：测试计划和测试用例

**职责**：
- 为每个API接口生成测试用例
- 覆盖正常流程、异常流程、边界条件
- 生成测试数据
- 制定测试执行计划

**输出格式**：
```json
{
  "module_id": "MOD-001",
  "test_suites": [
    {
      "suite_name": "接口名称测试",
      "cases": [
        {
          "case_id": "TC-001",
          "title": "测试用例标题",
          "steps": ["步骤1", "步骤2"],
          "expected": "预期结果",
          "priority": "high|medium|low"
        }
      ]
    }
  ]
}
```

### 4. OutputAgent（输出Agent）

**输入**：前面所有Agent的输出
**输出**：完整技术方案（JSON）

**职责**：
- 汇总所有Agent的输出
- 生成统一格式的JSON方案
- 计算总体工作量估算
- 进行风险评估
- 可选：在JIRA中创建任务

## 技术栈

- **Python 3.10+**：主编程语言
- **OpenAI GPT-4 API**：Agent推理引擎
- **Pydantic**：数据验证和序列化
- **Streamlit**：Web界面
- **JIRA REST API**：任务管理集成（可选）

## 扩展点

1. **支持更多LLM**：可替换为其他大语言模型（Claude、Gemini等）
2. **自定义Agent**：继承`BaseAgent`类可实现自定义Agent
3. **输出格式**：可扩展支持更多输出格式（Markdown、YAML等）
4. **集成**：可集成更多项目管理工具（Notion、Linear等）

# 多Agent协作需求拆解系统

## 平台申报成果描述

---

## 一、项目核心痛点

### 1.1 传统需求拆解的困境

在软件工程实践中，产品经理输出的"一句话需求"到可执行的技术方案之间存在巨大鸿沟。传统流程面临以下核心痛点：

**信息衰减严重**：产品经理描述的业务需求经过多层传递后，技术细节严重失真。产品说"做一个登录功能"，开发理解为"做个表单验证"，测试理解为"输对密码能进"，最终交付结果与原始需求相去甚远。

**知识断层频发**：需求分析依赖个人经验，不同产品经理对需求的理解深度差异巨大。技术方案的设计质量完全取决于特定开发者的能力和状态，缺乏系统性的质量保障机制。

**返工成本高昂**：据业界统计，需求澄清阶段的问题若未能在设计阶段前发现，后期修复成本将增加5-10倍。传统模式下，需求→设计→开发→测试的线性流程导致问题发现严重滞后。

**协作效率低下**：产品、技术、测试三方对需求的理解需要反复沟通对齐。每次需求变更都需要召开多方评审会议，时间成本巨大且效果难以保证。

### 1.2 现有工具的局限

当前市场上的需求管理工具（如JIRA、Confluence、Tapd等）本质上仍是"文档协作平台"，而非"智能分析引擎"。它们能够存储和管理需求文档，但无法：
- 理解需求的业务语义
- 自动拆解功能模块
- 生成可执行的技术方案
- 确保需求→方案的一致性

---

## 二、系统技术架构

### 2.1 总体架构

本系统采用**管道（Pipeline）架构**结合**多Agent协作模式**，基于大语言模型（LLM）的推理能力，实现从自然语言需求到完整技术方案的端到端自动生成。

系统由4个专业Agent组成的处理管道，每个Agent承担特定职责，通过**PipelineContext**实现跨Agent状态传递，确保长链推理的上下文一致性。

```
┌──────────────────────────────────────────────────────────────────┐
│                      用户交互层                                    │
│   • Streamlit Web界面（可视化操作）                                 │
│   • Python API（程序化调用）                                        │
│   • 命令行CLI（快速集成）                                           │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                      管道编排层 (RequirementPipeline)              │
│   • 阶段调度与状态管理                                              │
│   • PipelineContext跨Agent状态传递                                  │
│   • 中间结果持久化与回溯                                            │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐
│ Planner    │ →  │ Tech       │ →  │ Test       │ →  │ Output     │
│ Agent      │    │ Agent      │    │ Agent      │    │ Agent      │
│            │    │            │    │            │    │            │
│ 功能模块    │    │ API设计    │    │ 测试用例   │    │ 汇总+JIRA  │
│ 拆解       │    │ +伪代码    │    │ 生成       │    │ 任务创建   │
└────────────┘    └────────────┘    └────────────┘    └────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                      输出层                                        │
│   • 结构化JSON方案（含工作量估算）                                   │
│   • JIRA任务（可选）                                               │
│   • 中间过程文件（可审计）                                          │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 核心数据结构

系统定义了`PipelineContext`作为跨Agent状态传递的载体：

```python
@dataclass
class PipelineContext:
    requirement_id: str                          # 需求唯一标识
    original_requirement: str                   # 原始需求文本
    current_stage: str                          # 当前处理阶段
    
    # 各阶段输出（Agent间传递的核心数据）
    planner_output: Dict                         # 功能模块拆解结果
    tech_output: Dict                           # 技术设计方案
    test_output: Dict                           # 测试用例集
    output: Dict                                # 最终汇总结果
    
    # 元数据
    jira_task_ids: List[str]                    # 创建的JIRA任务ID
    metadata: Dict                              # 扩展元数据
```

该设计确保：
1. **上下文一致性**：每个Agent都能获取完整的历史处理信息
2. **可审计性**：完整记录从需求到方案的推导过程
3. **容错性**：单阶段失败不影响其他阶段的已有结果

---

## 三、多Agent协作逻辑流

### 3.1 阶段一：规划Agent（PlannerAgent）

**输入**：产品经理的一句话需求（自然语言）

**核心能力**：
- 理解业务语义，识别需求的业务目标和约束
- 拆解为独立的功能模块集合
- 识别模块间的依赖关系和调用顺序
- 评估模块优先级和技术风险
- 估算各模块工作量

**输出格式**：
```json
{
  "functional_modules": [
    {
      "module_id": "MOD-001",
      "module_name": "用户认证模块",
      "module_type": "core",
      "description": "支持邮箱/手机号注册登录",
      "dependencies": [],
      "priority": "high",
      "estimated_effort_days": 4.5
    },
    {
      "module_id": "MOD-002",
      "module_name": "用户信息管理",
      "module_type": "core",
      "description": "用户资料的CRUD操作",
      "dependencies": ["MOD-001"],
      "priority": "high",
      "estimated_effort_days": 3.0
    }
  ],
  "overall_estimate": {
    "total_days": 12.5,
    "risk_level": "medium"
  }
}
```

### 3.2 阶段二：技术Agent（TechAgent）

**输入**：功能模块列表（来自PlannerAgent）

**核心能力**：
- 为每个模块设计RESTful API接口
- 确定接口的HTTP方法、路径、请求/响应格式
- 生成核心业务逻辑的伪代码
- 设计数据模型和数据库表结构
- 指定需要的技术栈和第三方服务依赖

**输出格式**：
```json
{
  "modules": [
    {
      "module_id": "MOD-001",
      "api_endpoints": [
        {
          "method": "POST",
          "path": "/api/v1/auth/register",
          "description": "用户注册",
          "request_body": {
            "email": "string (必填)",
            "password": "string (必填, 8-32位)",
            "username": "string (必填)"
          },
          "response": {
            "success": true,
            "user_id": "uuid",
            "token": "jwt_token"
          }
        }
      ],
      "pseudo_code": "function register(email, password, username) {\n  validateInput(email, password, username);\n  checkDuplicate(email);\n  hashedPassword = bcrypt.hash(password);\n  user = db.users.create({email, hashedPassword, username});\n  return generateToken(user);\n}",
      "data_models": ["User", "Session"],
      "tech_stack": ["Node.js", "Express", "MongoDB"]
    }
  ]
}
```

### 3.3 阶段三：测试Agent（TestAgent）

**输入**：技术设计方案（来自TechAgent）

**核心能力**：
- 为每个API端点设计测试用例
- 覆盖正常流程、异常流程、边界条件
- 生成测试数据和前置条件
- 识别潜在的质量风险点
- 制定测试执行计划

**输出格式**：
```json
{
  "modules": [
    {
      "module_id": "MOD-001",
      "test_suites": [
        {
          "suite_name": "用户注册接口测试",
          "cases": [
            {
              "case_id": "TC-001",
              "title": "正常注册流程",
              "type": "positive",
              "steps": [
                "POST /api/v1/auth/register",
                "body: {email, password, username}"
              ],
              "expected": "201 Created, 返回token",
              "priority": "P0"
            },
            {
              "case_id": "TC-002",
              "title": "邮箱格式错误",
              "type": "negative",
              "steps": [
                "POST /api/v1/auth/register",
                "body: {email: 'invalid-email', ...}"
              ],
              "expected": "400 Bad Request, 错误提示",
              "priority": "P1"
            }
          ]
        }
      ]
    }
  ]
}
```

### 3.4 阶段四：输出Agent（OutputAgent）

**输入**：前三个阶段的所有输出

**核心能力**：
- 汇总所有Agent的输出为统一格式
- 计算总体工作量估算
- 进行风险评估
- 生成结构化的JSON方案
- （可选）调用JIRA API创建Epic/Task/Sub-task

**最终输出格式**：
```json
{
  "requirement_id": "REQ-20260502-A7F3B2",
  "original_requirement": "开发一个用户管理系统...",
  "timestamp": "2026-05-02T20:30:00Z",
  "modules": [...],
  "summary": {
    "total_modules": 4,
    "total_api_endpoints": 12,
    "total_test_cases": 45,
    "estimated_effort": {
      "total_days": 15.5,
      "by_module": {...}
    },
    "risk_assessment": {
      "level": "medium",
      "factors": ["第三方服务依赖", "数据迁移复杂度"]
    }
  },
  "jira_tasks": [
    {"id": "DEMO-101", "type": "Epic", "title": "用户管理系统"},
    {"id": "DEMO-102", "type": "Task", "title": "用户认证模块"}
  ]
}
```

---

## 四、长链推理机制

### 4.1 推理链路设计

系统采用**顺序推理 + 状态累积**的策略：

```
需求文本
    ↓ [Planner: 理解业务语义]
功能模块列表 + 工作量估算
    ↓ [Tech: 承接业务语义, 转化为技术表达]
API设计 + 伪代码 + 数据模型
    ↓ [Test: 基于技术设计推导测试场景]
测试用例 + 测试数据
    ↓ [Output: 综合所有推导结果, 形成完整方案]
最终JSON方案
```

每一阶段的输出不仅包含该阶段的直接结果，还包含：
- 对前序阶段的确认或修正
- 对后续阶段的建议或约束
- 推理过程中的关键决策点

### 4.2 上下文保持策略

1. **PipelineContext注入**：每个Agent接收完整的上下文对象，而非仅接收前序Agent的输出
2. **JSON Schema规范化**：各Agent的输入输出遵循统一的数据Schema，确保格式一致性
3. **中间结果持久化**：每个阶段完成后自动保存中间结果，支持失败恢复和过程审计
4. **溯源追踪**：每个功能模块的API设计可追溯到原始需求，确保需求→方案的完整链路

### 4.3 质量保障机制

- **自检机制**：每个Agent在输出前进行内部校验，确保输出符合Schema要求
- **一致性检查**：OutputAgent负责验证前后阶段输出的一致性
- **人工干预点**：支持在任意阶段暂停，由人工审核后继续执行
- **版本管理**：所有输出包含版本号和时间戳，支持历史回溯

---

## 五、技术创新点

### 5.1 架构创新

- **专业化Agent分工**：将需求拆解这个复杂任务分解为4个专业化子任务，每个Agent专注特定能力，降低单一Agent的认知负担
- **Pipeline编排模式**：通过统一的管道编排层管理Agent间的数据流和依赖关系，而非简单的串行调用
- **Context驱动设计**：通过PipelineContext实现跨阶段状态共享，解决长链推理中的上下文丢失问题

### 5.2 方法论创新

- **业务-技术-测试三位一体**：打破传统的产品→技术→测试的线性流程，让三个视角在同一管道中协同工作
- **可推导性优先**：不仅输出最终方案，还保留完整的推导过程，支持方案审计和结果解释
- **增量式拆解**：支持对复杂需求进行多轮渐进式拆解，而非一次性输出

### 5.3 工程化创新

- **多形态交付**：支持Web界面、Python API、命令行CLI三种使用形态，满足不同场景需求
- **JIRA深度集成**：不仅生成方案，还能自动在JIRA中创建Epic/Task/Sub-task，真正实现需求到任务的闭环
- **可扩展架构**：Agent基类提供标准化接口，支持自定义Agent扩展系统能力

---

## 六、应用价值与推广前景

### 6.1 直接价值

| 维度 | 传统方式 | 本系统 |
|------|---------|--------|
| 需求澄清时间 | 3-5人天 | 10-30分钟 |
| 方案完整性 | 依赖个人经验 | 系统化保障 |
| 返工率 | 15-25% | 预计降低至5%以下 |
| 文档规范性 | 不统一 | 标准化JSON输出 |

### 6.2 推广场景

- **企业内部工具**：集成到企业需求管理流程，提升需求分析效率
- **SaaS服务平台**：作为需求分析服务的核心引擎，提供API调用
- **教育培训场景**：帮助新人理解需求分析的思维框架
- **项目交付标准化**：作为交付物模板，确保项目文档质量

### 6.3 技术演进方向

- **多模态支持**：支持输入原型图、流程图等视觉信息
- **知识库集成**：对接企业知识库，利用历史项目经验辅助分析
- **团队协作**：支持多人协同审核和修订AI生成方案
- **多语言适配**：支持生成不同编程语言的技术方案

---

## 七、项目信息

- **项目名称**：多Agent协作需求拆解系统
- **技术栈**：Python 3.10+ / OpenAI GPT-4 / Streamlit / JIRA REST API
- **开源地址**：GitHub (multi-agent-requirement-system)
- **许可证**：MIT License

---

*本文档为平台申报用成果描述，真实反映项目的技术架构和创新价值。*

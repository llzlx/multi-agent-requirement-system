# 多 Agent 协作需求拆解系统

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

基于 AutoGen 风格的多 Agent 协作系统，将产品经理的一句话需求自动拆解为完整的技术方案（含 API 设计、伪代码、测试用例，并可选创建 JIRA 任务）。

## 功能特性

- **四阶段多 Agent 协作**：规划 → 技术设计 → 测试设计 → 汇总输出
- **长链推理**：每个 Agent 的输出作为下一个 Agent 的输入
- **JIRA 集成**：自动创建 Epic / Task / Sub-task
- **Web 界面**：基于 Streamlit 的可视化操作界面
- **完整 JSON 输出**：结构化方案，含工作量估算和风险评估

## 系统架构

```
产品经理输入
     |
     v
+------------------------------------+
|   Agent 1: 规划 Agent（PlannerAgent）  |
|   需求 → 功能模块列表                   |
+------------------------------------+
     |
     v
+------------------------------------+
|   Agent 2: 技术 Agent（TechAgent）    |
|   模块列表 → API 接口设计 + 伪代码    |
+------------------------------------+
     |
     v
+------------------------------------+
|   Agent 3: 测试 Agent（TestAgent）    |
|   接口设计 → 测试用例                 |
+------------------------------------+
     |
     v
+------------------------------------+
|   Agent 4: 输出 Agent（OutputAgent）  |
|   汇总 → JSON 方案 + JIRA 任务创建    |
+------------------------------------+
     |
     v
 完整技术方案（JSON）
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
# 或使用 poetry
poetry install
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写：

```bash
# OpenAI API（必填）
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
OPENAI_API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-4

# JIRA（可选，用于自动创建任务）
JIRA_SERVER=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-api-token
JIRA_PROJECT_KEY=DEMO
```

### 3. 运行

**命令行模式：**
```bash
python -m multi_agent_system.pipeline
```

**Web 界面模式：**
```bash
streamlit run multi_agent_system/web_app.py
```

**Python API：**
```python
from multi_agent_system.pipeline import create_pipeline

result = create_pipeline(
    requirement="开发一个用户管理系统，支持注册、登录、权限控制",
    use_jira=False,
    output_dir="./output"
)

print(result)
```

## 输出示例

```json
{
  "requirement_id": "REQ-20260502-A7F3B2",
  "original_requirement": "开发一个用户管理系统...",
  "modules": [
    {
      "module_id": "MOD-001",
      "module_name": "用户管理模块",
      "module_type": "core",
      "api_endpoints": [...],
      "pseudo_code": "...",
      "test_suites": [...]
    }
  ],
  "summary": {
    "total_modules": 4,
    "total_api_endpoints": 12,
    "total_test_cases": 45,
    "estimated_effort": {"total_days": 15.5}
  }
}
```

## 项目结构

```
multi-agent-requirement-system/
├── multi_agent_system/
│   ├── __init__.py
│   ├── pipeline.py          # 主管道逻辑
│   ├── config.py            # 配置管理
│   ├── web_app.py          # Streamlit Web 界面
│   └── agents/
│       ├── __init__.py
│       ├── base.py         # Agent 基类
│       ├── planner.py      # 规划 Agent
│       ├── tech.py         # 技术 Agent
│       ├── test.py         # 测试 Agent
│       ├── output.py       # 输出 Agent
│       └── jira_integration.py  # JIRA 集成
├── examples/
│   └── sample_output.json  # 示例输出
├── .env.example
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── LICENSE
└── README.md
```

## 技术栈

- **Python 3.10+**
- **OpenAI GPT-4** / 兼容 API
- **Streamlit** - Web 界面
- **JIRA REST API** - 任务管理集成
- **Pydantic** - 数据验证

## 配置说明

| 环境变量 | 必填 | 说明 |
|---------|------|------|
| `OPENAI_API_KEY` | 是 | OpenAI API Key |
| `OPENAI_API_BASE` | 否 | API 基础地址（默认官方） |
| `MODEL_NAME` | 否 | 模型名称（默认 gpt-4） |
| `JIRA_SERVER` | 否 | JIRA 服务器地址 |
| `JIRA_EMAIL` | 否 | JIRA 账号邮箱 |
| `JIRA_API_TOKEN` | 否 | JIRA API Token |
| `JIRA_PROJECT_KEY` | 否 | JIRA 项目 Key |

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 作者

Built with AutoGen-style multi-agent collaboration.

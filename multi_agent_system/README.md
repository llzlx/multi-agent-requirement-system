# 多 Agent 协作需求拆解系统

## 环境依赖

```
openai>=1.0.0
python-dotenv>=1.0.0
requests>=2.31.0
pydantic>=2.0.0
streamlit>=1.28.0
```

## 安装

```bash
pip install -r requirements.txt
```

## 环境变量配置

创建 `.env` 文件：

```bash
# OpenAI API 配置
OPENAI_API_KEY=your-api-key
OPENAI_API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-4

# JIRA 配置（可选）
JIRA_SERVER=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@domain.com
JIRA_API_TOKEN=your-api-token
JIRA_PROJECT_KEY=DEMO
```

## 运行方式

### 1. 命令行模式

```bash
python -m multi_agent_system.pipeline
```

### 2. Web 界面模式

```bash
streamlit run multi_agent_system/web_app.py
```

### 3. Python API

```python
from multi_agent_system.pipeline import create_pipeline

result = create_pipeline(
    requirement="开发一个用户管理系统...",
    use_jira=False,
    output_dir="./output"
)
```

## 架构说明

- `agents/base.py` - Agent 基类和上下文管理
- `agents/planner.py` - 规划 Agent
- `agents/tech.py` - 技术 Agent
- `agents/test.py` - 测试 Agent
- `agents/output.py` - 输出 Agent
- `agents/jira_integration.py` - JIRA 集成
- `pipeline.py` - 主管道逻辑

## 输出结构

```json
{
  "requirement_id": "REQ-日期-随机ID",
  "original_requirement": "原始需求",
  "modules": [
    {
      "module_id": "MOD-001",
      "module_name": "模块名称",
      "api_endpoints": [...],
      "pseudo_code": "...",
      "test_suites": [...],
      ...
    }
  ],
  "summary": {...}
}
```

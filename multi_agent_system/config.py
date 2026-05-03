"""
配置模块 - 管理所有配置和常量
"""
import os
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class ModelConfig:
    """模型配置"""
    model_name: str = "gpt-4"
    api_key: str = ""
    api_base: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class JIRAConfig:
    """JIRA 配置"""
    server: str = "https://your-domain.atlassian.net"
    email: str = ""
    api_token: str = ""
    project_key: str = "PROJ"
    issue_type: str = "Task"


@dataclass
class AgentConfig:
    """Agent 配置"""
    name: str
    role: str
    goal: str
    backstory: str
    system_message: str


@dataclass
class SystemConfig:
    """系统配置"""
    model: ModelConfig = field(default_factory=ModelConfig)
    jira: JIRAConfig = field(default_factory=JIRAConfig)
    use_jira: bool = False
    output_dir: str = "./output"
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "SystemConfig":
        """从环境变量加载配置"""
        config = cls()

        # 加载模型配置
        if os.getenv("OPENAI_API_KEY"):
            config.model.api_key = os.getenv("OPENAI_API_KEY")
        if os.getenv("OPENAI_API_BASE"):
            config.model.api_base = os.getenv("OPENAI_API_BASE")
        if os.getenv("MODEL_NAME"):
            config.model.model_name = os.getenv("MODEL_NAME")

        # 加载 JIRA 配置
        if os.getenv("JIRA_SERVER"):
            config.jira.server = os.getenv("JIRA_SERVER")
        if os.getenv("JIRA_EMAIL"):
            config.jira.email = os.getenv("JIRA_EMAIL")
        if os.getenv("JIRA_API_TOKEN"):
            config.jira.api_token = os.getenv("JIRA_API_TOKEN")
        if os.getenv("JIRA_PROJECT_KEY"):
            config.jira.project_key = os.getenv("JIRA_PROJECT_KEY")

        config.use_jira = all([
            config.jira.email,
            config.jira.api_token
        ])

        return config


# Agent 角色定义
PLANNER_PROMPT = """你是一个专业的需求分析师，擅长将模糊的需求拆解为清晰的功能模块。"""

TECH_AGENT_PROMPT = """你是一个资深后端架构师，擅长设计 RESTful API 接口和编写高质量的伪代码。"""

TEST_AGENT_PROMPT = """你是一个测试专家，擅长设计全面的测试用例，确保代码质量。"""

OUTPUT_AGENT_PROMPT = """你是一个项目经理，擅长汇总技术方案并以结构化格式输出。"""

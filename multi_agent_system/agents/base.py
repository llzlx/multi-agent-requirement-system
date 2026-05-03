"""
基础 Agent 类 - 所有 Agent 的基类
"""
import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum


class AgentRole(Enum):
    """Agent 角色枚举"""
    PLANNER = "planner"
    TECH = "tech"
    TEST = "test"
    OUTPUT = "output"


@dataclass
class AgentMessage:
    """Agent 消息结构"""
    sender: str
    receiver: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AgentOutput:
    """Agent 输出结构"""
    agent_name: str
    role: AgentRole
    success: bool
    content: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "agent_name": self.agent_name,
            "role": self.role.value,
            "success": self.success,
            "content": self.content,
            "error": self.error,
            "metadata": self.metadata
        }


class BaseAgent(ABC):
    """Agent 基类"""
    
    def __init__(
        self,
        name: str,
        role: AgentRole,
        goal: str,
        system_prompt: str,
        model_client: Optional[Any] = None
    ):
        self.name = name
        self.role = role
        self.goal = goal
        self.system_prompt = system_prompt
        self.model_client = model_client
        self.message_history: List[AgentMessage] = []
        
    @abstractmethod
    def process(self, input_data: Any) -> AgentOutput:
        """处理输入数据，返回 Agent 输出"""
        pass
    
    def _format_output(self, content: Any, success: bool = True, error: Optional[str] = None) -> AgentOutput:
        """格式化输出"""
        return AgentOutput(
            agent_name=self.name,
            role=self.role,
            success=success,
            content=content,
            error=error
        )
    
    def add_message(self, message: AgentMessage):
        """添加消息到历史"""
        self.message_history.append(message)
    
    def get_history(self) -> List[Dict]:
        """获取消息历史"""
        return [msg.to_dict() for msg in self.message_history]
    
    def clear_history(self):
        """清空消息历史"""
        self.message_history = []


class PipelineContext:
    """管道上下文 - 在 Agent 之间传递数据"""
    
    def __init__(self, requirement_id: str, original_requirement: str):
        self.requirement_id = requirement_id
        self.original_requirement = original_requirement
        self.created_at = datetime.now().isoformat()
        self.planner_output: Optional[Dict] = None
        self.tech_output: Optional[Dict] = None
        self.test_output: Optional[Dict] = None
        self.output: Optional[Dict] = None
        self.metadata: Dict[str, Any] = {}
        
    def to_dict(self) -> Dict:
        return {
            "requirement_id": self.requirement_id,
            "original_requirement": self.original_requirement,
            "created_at": self.created_at,
            "planner_output": self.planner_output,
            "tech_output": self.tech_output,
            "test_output": self.test_output,
            "final_output": self.output,
            "metadata": self.metadata
        }
    
    def get_modules(self) -> List[Dict]:
        """获取模块列表"""
        if self.tech_output and "modules" in self.tech_output:
            return self.tech_output["modules"]
        return []

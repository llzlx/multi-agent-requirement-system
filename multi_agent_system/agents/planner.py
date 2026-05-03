"""
规划 Agent - 将需求拆解为功能模块列表
"""
import json
from typing import Dict, List, Any
from .base import BaseAgent, AgentRole, AgentOutput


class PlannerAgent(BaseAgent):
    """规划 Agent - 需求分析与模块拆分"""
    
    def __init__(self, model_client: Any = None):
        system_prompt = """你是一个专业的需求分析师。你的职责是将产品经理的一句话需求拆解为清晰的功能模块列表。

## 输出要求

你必须输出一个 JSON 对象，包含以下结构：

{
    "requirement_summary": "需求的简要概括（一句话）",
    "stakeholders": ["相关干系人列表"],
    "functional_modules": [
        {
            "module_id": "MOD-001",
            "module_name": "模块名称",
            "module_type": "core|support|integration|report",
            "description": "模块的详细描述",
            "sub_features": ["子功能1", "子功能2"],
            "priority": "high|medium|low",
            "dependencies": ["依赖的模块ID"],
            "acceptance_criteria": ["验收标准1", "验收标准2"]
        }
    ],
    "non_functional_requirements": {
        "performance": "性能要求",
        "security": "安全要求",
        "scalability": "可扩展性要求"
    },
    "implementation_notes": "实现注意事项"
}

## 分析原则

1. **完整性**: 确保覆盖需求的各个方面
2. **模块化**: 每个模块有清晰的职责边界
3. **可测试性**: 每个模块有明确的验收标准
4. **优先级**: 区分核心功能和辅助功能

## 模块类型说明

- core: 核心业务模块
- support: 支持性模块
- integration: 第三方集成模块
- report: 报表/统计模块

请直接输出 JSON，不要添加额外的解释。"""
        
        super().__init__(
            name="PlannerAgent",
            role=AgentRole.PLANNER,
            goal="将需求拆解为功能模块列表",
            system_prompt=system_prompt,
            model_client=model_client
        )
    
    def process(self, input_data: str) -> AgentOutput:
        """处理需求输入，生成模块列表"""
        try:
            if self.model_client:
                # 使用模型客户端
                response = self.model_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": f"请分析以下需求并拆解为功能模块：\n\n{input_data}"}
                    ],
                    temperature=0.7,
                    max_tokens=4096
                )
                content = response.choices[0].message.content
            else:
                # 模拟输出（当没有 API 时使用）
                content = self._generate_mock_output(input_data)
            
            # 尝试解析 JSON
            try:
                # 提取 JSON 部分
                json_str = self._extract_json(content)
                parsed_content = json.loads(json_str)
            except json.JSONDecodeError:
                # 如果解析失败，保留原始内容
                parsed_content = {
                    "raw_output": content,
                    "parse_error": "无法解析为 JSON"
                }
            
            return self._format_output(parsed_content)
            
        except Exception as e:
            return self._format_output(
                content=None,
                success=False,
                error=str(e)
            )
    
    def _extract_json(self, text: str) -> str:
        """从文本中提取 JSON"""
        import re
        # 尝试匹配 ```json 和 ``` 之间的内容
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            return json_match.group(1)
        
        # 尝试匹配 ``` 和 ``` 之间的内容
        code_match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
        if code_match:
            return code_match.group(1)
        
        # 尝试直接解析整个文本
        text = text.strip()
        if text.startswith('{') and text.endswith('}'):
            return text
        
        # 找到第一个 { 和最后一个 }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return text[start:end+1]
        
        return text
    
    def _generate_mock_output(self, requirement: str) -> str:
        """生成模拟输出（用于测试）"""
        return json.dumps({
            "requirement_summary": f"实现 {requirement} 相关功能",
            "stakeholders": ["产品经理", "开发团队", "测试团队", "终端用户"],
            "functional_modules": [
                {
                    "module_id": "MOD-001",
                    "module_name": "用户管理模块",
                    "module_type": "core",
                    "description": "处理用户的注册、登录、信息管理等基础功能",
                    "sub_features": [
                        "用户注册与验证",
                        "用户登录与认证",
                        "用户信息管理",
                        "密码找回与重置"
                    ],
                    "priority": "high",
                    "dependencies": [],
                    "acceptance_criteria": [
                        "支持邮箱/手机号注册",
                        "支持第三方登录",
                        "密码加密存储"
                    ]
                },
                {
                    "module_id": "MOD-002",
                    "module_name": "核心业务模块",
                    "module_type": "core",
                    "description": "处理核心业务逻辑",
                    "sub_features": [
                        "业务数据管理",
                        "业务流程控制",
                        "业务规则引擎"
                    ],
                    "priority": "high",
                    "dependencies": ["MOD-001"],
                    "acceptance_criteria": [
                        "支持业务流程配置",
                        "支持规则自定义"
                    ]
                },
                {
                    "module_id": "MOD-003",
                    "module_name": "数据报表模块",
                    "module_type": "report",
                    "description": "生成业务数据报表",
                    "sub_features": [
                        "数据统计",
                        "报表生成",
                        "报表导出"
                    ],
                    "priority": "medium",
                    "dependencies": ["MOD-002"],
                    "acceptance_criteria": [
                        "支持多种图表类型",
                        "支持 Excel/PDF 导出"
                    ]
                }
            ],
            "non_functional_requirements": {
                "performance": "接口响应时间 < 200ms",
                "security": "符合等保三级要求",
                "scalability": "支持水平扩展"
            },
            "implementation_notes": "建议采用微服务架构，核心模块独立部署"
        }, ensure_ascii=False, indent=2)

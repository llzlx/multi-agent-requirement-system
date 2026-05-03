"""
测试 Agent - 生成测试用例
"""
import json
from typing import Dict, List, Any
from .base import BaseAgent, AgentRole, AgentOutput


class TestAgent(BaseAgent):
    """测试 Agent - 测试用例生成"""
    
    def __init__(self, model_client: Any = None):
        system_prompt = """你是一个专业的测试工程师。你的职责是为每个功能模块设计全面的测试用例。

## 输入格式

你会收到一个 JSON 对象，包含模块的接口设计和伪代码，格式如下：

{
    "modules": [
        {
            "module_id": "MOD-001",
            "module_name": "模块名称",
            "api_endpoints": [
                {
                    "method": "GET|POST|PUT|DELETE",
                    "path": "/api/v1/endpoint",
                    "description": "接口描述",
                    "request_params": {...},
                    "response": {...}
                }
            ],
            "pseudo_code": "# 伪代码"
        }
    ]
}

## 输出要求

你必须输出一个 JSON 对象，结构如下：

{
    "modules": [
        {
            "module_id": "原模块ID",
            "module_name": "模块名称",
            "test_suites": [
                {
                    "suite_name": "测试套件名称",
                    "test_type": "unit|integration|e2e|performance",
                    "test_cases": [
                        {
                            "case_id": "TC-001",
                            "case_name": "测试用例名称",
                            "case_type": "positive|negative|boundary",
                            "preconditions": ["前置条件"],
                            "test_steps": [
                                "步骤1: 描述",
                                "步骤2: 描述"
                            ],
                            "test_data": {
                                "input": {},
                                "expected_output": {}
                            },
                            "priority": "P0|P1|P2|P3",
                            "automated": true
                        }
                    ]
                }
            ],
            "test_coverage": {
                "api_coverage": "95%",
                "branch_coverage": "90%",
                "edge_cases": ["边界情况列表"]
            },
            "test_environment": {
                "framework": "pytest",
                "fixtures": ["fixture列表"],
                "mock_services": ["mock服务列表"]
            }
        }
    ]
}

## 测试用例设计原则

1. **覆盖率**: 覆盖所有 API 端点
2. **分类**:
   - positive: 正向测试
   - negative: 异常测试
   - boundary: 边界测试
3. **优先级**:
   - P0: 核心功能，必须通过
   - P1: 重要功能
   - P2: 一般功能
   - P3: 边缘功能
4. **可自动化**: 优先设计可自动化执行的用例

## 测试类型

- unit: 单元测试
- integration: 集成测试
- e2e: 端到端测试
- performance: 性能测试

请直接输出 JSON，不要添加额外的解释。"""
        
        super().__init__(
            name="TestAgent",
            role=AgentRole.TEST,
            goal="生成测试用例",
            system_prompt=system_prompt,
            model_client=model_client
        )
    
    def process(self, input_data: Dict) -> AgentOutput:
        """处理接口设计，生成测试用例"""
        try:
            if isinstance(input_data, str):
                try:
                    input_data = json.loads(input_data)
                except:
                    pass
            
            modules_input = input_data.get("modules", [input_data])
            
            if self.model_client:
                # 使用模型客户端
                response = self.model_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": f"请为以下模块生成测试用例：\n\n{json.dumps(modules_input, ensure_ascii=False, indent=2)}"}
                    ],
                    temperature=0.7,
                    max_tokens=8192
                )
                content = response.choices[0].message.content
            else:
                # 模拟输出
                content = self._generate_mock_output(modules_input)
            
            # 解析 JSON
            try:
                json_str = self._extract_json(content)
                parsed_content = json.loads(json_str)
            except json.JSONDecodeError:
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
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            return json_match.group(1)
        
        code_match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
        if code_match:
            return code_match.group(1)
        
        text = text.strip()
        if text.startswith('{') and text.endswith('}'):
            return text
        
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return text[start:end+1]
        
        return text
    
    def _generate_mock_output(self, modules: List[Dict]) -> str:
        """生成模拟测试用例"""
        modules_output = []
        
        for module in modules:
            module_id = module.get("module_id", "MOD-001")
            module_name = module.get("module_name", "模块")
            api_endpoints = module.get("api_endpoints", [])
            
            test_suites = []
            test_case_id = 1
            
            # 为每个端点生成测试用例
            for endpoint in api_endpoints:
                method = endpoint.get("method", "GET")
                path = endpoint.get("path", "")
                description = endpoint.get("description", "")
                request_params = endpoint.get("request_params", {})
                
                # 提取端点名称
                path_parts = path.split("/")
                endpoint_name = path_parts[-1] if path_parts else "endpoint"
                
                suite = {
                    "suite_name": f"{endpoint_name}接口测试",
                    "test_type": "integration",
                    "test_cases": []
                }
                
                # 正向测试用例
                suite["test_cases"].append({
                    "case_id": f"TC-{test_case_id:03d}",
                    "case_name": f"{description} - 正常场景",
                    "case_type": "positive",
                    "preconditions": ["服务正常运行", "数据库已初始化"],
                    "test_steps": [
                        f"发送 {method} 请求到 {path}",
                        "验证请求参数正确",
                        "验证响应状态码正确"
                    ],
                    "test_data": {
                        "request": self._generate_sample_request(method, request_params),
                        "expected_status": 200 if method == "GET" else 201
                    },
                    "priority": "P0",
                    "automated": True
                })
                test_case_id += 1
                
                # 参数验证测试
                suite["test_cases"].append({
                    "case_id": f"TC-{test_case_id:03d}",
                    "case_name": f"{description} - 必填参数缺失",
                    "case_type": "negative",
                    "preconditions": [],
                    "test_steps": [
                        f"发送 {method} 请求到 {path}，不传必填参数",
                        "验证返回错误码 400"
                    ],
                    "test_data": {
                        "request": {},
                        "expected_status": 400,
                        "expected_error": "缺少必填参数"
                    },
                    "priority": "P0",
                    "automated": True
                })
                test_case_id += 1
                
                # 边界值测试
                suite["test_cases"].append({
                    "case_id": f"TC-{test_case_id:03d}",
                    "case_name": f"{description} - 参数边界值",
                    "case_type": "boundary",
                    "preconditions": [],
                    "test_steps": [
                        f"发送 {method} 请求，参数使用边界值",
                        "验证响应正确"
                    ],
                    "test_data": {
                        "request": {"name": "", "description": "x" * 10000},
                        "expected_status": 400,
                        "expected_error": "参数超出范围"
                    },
                    "priority": "P1",
                    "automated": True
                })
                test_case_id += 1
                
                # 未授权测试
                if "header" not in request_params:
                    suite["test_cases"].append({
                        "case_id": f"TC-{test_case_id:03d}",
                        "case_name": f"{description} - 未授权访问",
                        "case_type": "negative",
                        "preconditions": [],
                        "test_steps": [
                            f"发送 {method} 请求，不带认证 Token",
                            "验证返回 401 未授权"
                        ],
                        "test_data": {
                            "headers": {},
                            "expected_status": 401
                        },
                        "priority": "P1",
                        "automated": True
                    })
                    test_case_id += 1
                
                test_suites.append(suite)
            
            # 单元测试套件
            unit_suite = {
                "suite_name": f"{module_name}业务逻辑单元测试",
                "test_type": "unit",
                "test_cases": [
                    {
                        "case_id": f"TC-{test_case_id:03d}",
                        "case_name": f"{module_name} - 创建实体成功",
                        "case_type": "positive",
                        "preconditions": ["数据库连接正常"],
                        "test_steps": [
                            "调用服务层创建方法",
                            "验证实体创建成功",
                            "验证属性正确"
                        ],
                        "test_data": {
                            "input": {"name": "测试数据", "description": "测试描述"},
                            "expected": {"name": "测试数据", "id": ">0"}
                        },
                        "priority": "P0",
                        "automated": True
                    },
                    {
                        "case_id": f"TC-{test_case_id:03d}",
                        "case_name": f"{module_name} - 创建实体失败 - 名称重复",
                        "case_type": "negative",
                        "preconditions": ["数据库中已存在同名数据"],
                        "test_steps": [
                            "调用服务层创建方法",
                            "验证抛出重复异常"
                        ],
                        "test_data": {
                            "input": {"name": "已存在的数据"},
                            "expected_error": "数据已存在"
                        },
                        "priority": "P1",
                        "automated": True
                    }
                ]
            }
            test_suites.append(unit_suite)
            
            modules_output.append({
                "module_id": module_id,
                "module_name": module_name,
                "test_suites": test_suites,
                "test_coverage": {
                    "api_coverage": f"{min(95, len(api_endpoints) * 30)}%",
                    "branch_coverage": "85%",
                    "edge_cases": [
                        "空参数",
                        "超长参数",
                        "特殊字符",
                        "SQL注入",
                        "XSS攻击"
                    ]
                },
                "test_environment": {
                    "framework": "pytest + pytest-asyncio",
                    "fixtures": [
                        "db_setup",
                        "auth_token",
                        "sample_data",
                        "cleanup"
                    ],
                    "mock_services": [
                        "mock_database",
                        "mock_redis",
                        "mock_external_api"
                    ],
                    "test_data_factory": "factory_boy"
                }
            })
        
        return json.dumps({
            "modules": modules_output,
            "total_test_cases": sum(
                len(m.get("test_suites", [{}])) * 5 
                for m in modules_output
            ),
            "test_execution_plan": {
                "phase_1": "单元测试 (CI)",
                "phase_2": "集成测试 (PR)",
                "phase_3": "E2E测试 (Release)",
                "phase_4": "性能测试 (Staging)"
            }
        }, ensure_ascii=False, indent=2)
    
    def _generate_sample_request(self, method: str, request_params: Dict) -> Dict:
        """生成示例请求数据"""
        sample = {}
        
        body = request_params.get("body", {})
        for key, value in body.items():
            if "string" in str(value):
                sample[key] = "test_value"
            elif "int" in str(value):
                sample[key] = 1
            elif "bool" in str(value):
                sample[key] = True
        
        return sample

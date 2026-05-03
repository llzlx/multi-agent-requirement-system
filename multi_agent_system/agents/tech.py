"""
技术 Agent - 生成接口设计和伪代码
"""
import json
from typing import Dict, List, Any
from .base import BaseAgent, AgentRole, AgentOutput


class TechAgent(BaseAgent):
    """技术 Agent - 接口设计与伪代码生成"""
    
    def __init__(self, model_client: Any = None):
        system_prompt = """你是一个资深后端架构师。你的职责是为每个功能模块设计 RESTful API 接口并生成伪代码。

## 输入格式

你会收到一个 JSON 对象，包含功能模块列表，格式如下：

{
    "functional_modules": [
        {
            "module_id": "MOD-001",
            "module_name": "模块名称",
            "module_type": "core|support|integration|report",
            "description": "模块描述",
            "sub_features": ["子功能1", "子功能2"],
            "priority": "high|medium|low",
            "dependencies": ["依赖的模块ID"]
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
            "data_models": {
                "Request": {
                    "字段名": "类型: 说明"
                },
                "Response": {
                    "字段名": "类型: 说明"
                }
            },
            "api_endpoints": [
                {
                    "method": "GET|POST|PUT|DELETE",
                    "path": "/api/v1/endpoint",
                    "description": "接口描述",
                    "request_params": {
                        "path": {},
                        "query": {},
                        "body": {}
                    },
                    "response": {
                        "success": {"code": 200, "message": "成功"},
                        "error": {"code": 400, "message": "参数错误"}
                    }
                }
            ],
            "pseudo_code": "# 伪代码实现\n# Python/伪代码格式",
            "database_schema": {
                "table_name": {
                    "columns": [
                        {"name": "字段名", "type": "类型", "constraints": "约束"}
                    ]
                }
            },
            "tech_stack": {
                "language": "Python",
                "framework": "FastAPI/Flask",
                "database": "PostgreSQL",
                "cache": "Redis"
            }
        }
    ],
    "architecture_notes": "架构说明",
    "security_considerations": "安全考虑"
}

## 设计原则

1. **RESTful 规范**: 使用标准 HTTP 方法
2. **版本控制**: API 路径包含版本号 /api/v1/
3. **命名规范**: 小写下划线分隔
4. **分页**: 列表接口支持分页参数 page, page_size
5. **错误码**: 使用统一的错误码体系

## 伪代码要求

- 使用 Python 风格
- 包含必要的异常处理
- 包含输入验证
- 注释清晰

请直接输出 JSON，不要添加额外的解释。"""
        
        super().__init__(
            name="TechAgent",
            role=AgentRole.TECH,
            goal="生成接口设计和伪代码",
            system_prompt=system_prompt,
            model_client=model_client
        )
    
    def process(self, input_data: Dict) -> AgentOutput:
        """处理模块列表，生成接口设计和伪代码"""
        try:
            # 从输入中提取模块列表
            if isinstance(input_data, str):
                try:
                    input_data = json.loads(input_data)
                except:
                    pass
            
            modules_input = input_data.get("functional_modules", [input_data])
            
            if self.model_client:
                # 使用模型客户端
                response = self.model_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": f"请为以下功能模块设计接口和伪代码：\n\n{json.dumps(modules_input, ensure_ascii=False, indent=2)}"}
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
        """生成模拟输出"""
        modules_output = []
        
        for module in modules:
            module_id = module.get("module_id", "MOD-001")
            module_name = module.get("module_name", "模块")
            module_type = module.get("module_type", "core")
            description = module.get("description", "")
            sub_features = module.get("sub_features", [])
            
            # 根据模块类型生成不同的 API
            if "用户" in module_name:
                api_endpoints = [
                    {
                        "method": "POST",
                        "path": "/api/v1/users/register",
                        "description": "用户注册",
                        "request_params": {
                            "body": {
                                "username": "string: 用户名",
                                "email": "string: 邮箱",
                                "password": "string: 密码"
                            }
                        },
                        "response": {
                            "success": {"code": 201, "message": "注册成功"},
                            "error": {"code": 400, "message": "参数错误"}
                        }
                    },
                    {
                        "method": "POST",
                        "path": "/api/v1/users/login",
                        "description": "用户登录",
                        "request_params": {
                            "body": {
                                "username": "string: 用户名",
                                "password": "string: 密码"
                            }
                        },
                        "response": {
                            "success": {"code": 200, "message": "登录成功", "data": {"token": "JWT Token"}},
                            "error": {"code": 401, "message": "认证失败"}
                        }
                    },
                    {
                        "method": "GET",
                        "path": "/api/v1/users/me",
                        "description": "获取当前用户信息",
                        "request_params": {
                            "header": {"Authorization": "Bearer Token"}
                        },
                        "response": {
                            "success": {"code": 200, "message": "成功", "data": {"user_id": 1, "username": "xxx"}}
                        }
                    }
                ]
                pseudo_code = '''# 用户服务伪代码
class UserService:
    def register(self, username: str, email: str, password: str) -> User:
        # 验证用户名唯一性
        if self.user_repo.exists_by_username(username):
            raise ValidationError("用户名已存在")
        
        # 验证邮箱格式
        if not self.validate_email(email):
            raise ValidationError("邮箱格式不正确")
        
        # 密码加密
        hashed_password = self.hash_password(password)
        
        # 创建用户
        user = User(
            username=username,
            email=email,
            password=hashed_password
        )
        
        self.user_repo.save(user)
        return user
    
    def login(self, username: str, password: str) -> str:
        user = self.user_repo.find_by_username(username)
        
        if not user or not self.verify_password(password, user.password):
            raise AuthenticationError("用户名或密码错误")
        
        # 生成 JWT Token
        token = self.jwt_service.generate_token(user.id)
        return token'''
            else:
                # 通用模块 API
                module_name_lower = module_name.lower().replace("模块", "")
                api_endpoints = [
                    {
                        "method": "GET",
                        "path": f"/api/v1/{module_name_lower}s",
                        "description": f"获取{module_name}列表",
                        "request_params": {
                            "query": {
                                "page": "int: 页码",
                                "page_size": "int: 每页数量"
                            }
                        },
                        "response": {
                            "success": {"code": 200, "message": "成功", "data": {"items": [], "total": 0}}
                        }
                    },
                    {
                        "method": "POST",
                        "path": f"/api/v1/{module_name_lower}s",
                        "description": f"创建{module_name}",
                        "request_params": {
                            "body": {"name": "string: 名称", "description": "string: 描述"}
                        },
                        "response": {
                            "success": {"code": 201, "message": "创建成功"}
                        }
                    },
                    {
                        "method": "GET",
                        "path": f"/api/v1/{module_name_lower}s/{{id}}",
                        "description": f"获取{module_name}详情",
                        "request_params": {
                            "path": {"id": "int: ID"}
                        },
                        "response": {
                            "success": {"code": 200, "message": "成功"}
                        }
                    }
                ]
                pseudo_code = f'''# {module_name}服务伪代码
class {module_name.replace("模块", "")}Service:
    def create(self, name: str, description: str) -> {module_name.replace("模块", "")}:
        # 数据验证
        if not name or len(name) > 100:
            raise ValidationError("名称长度应在1-100之间")
        
        # 创建实体
        entity = {module_name.replace("模块", "")}(
            name=name,
            description=description,
            status="active",
            created_at=datetime.now()
        )
        
        # 保存到数据库
        self.repo.save(entity)
        
        # 记录操作日志
        self.logger.info(f"创建{module_name}: {{entity.id}}")
        
        return entity
    
    def get_by_id(self, entity_id: int) -> {module_name.replace("模块", "")}:
        entity = self.repo.find_by_id(entity_id)
        if not entity:
            raise NotFoundError("{module_name}不存在")
        return entity
    
    def list(self, page: int = 1, page_size: int = 20) -> PageResult:
        return self.repo.find_paginated(page, page_size)'''
            
            modules_output.append({
                "module_id": module_id,
                "module_name": module_name,
                "module_type": module_type,
                "description": description,
                "sub_features": sub_features,
                "data_models": {
                    "Request": {
                        "name": "string: 名称",
                        "description": "string: 描述"
                    },
                    "Response": {
                        "id": "int: ID",
                        "name": "string: 名称",
                        "description": "string: 描述",
                        "status": "string: 状态",
                        "created_at": "datetime: 创建时间"
                    }
                },
                "api_endpoints": api_endpoints,
                "pseudo_code": pseudo_code,
                "database_schema": {
                    f"{module_name_lower}s": {
                        "columns": [
                            {"name": "id", "type": "BIGINT", "constraints": "PRIMARY KEY AUTO_INCREMENT"},
                            {"name": "name", "type": "VARCHAR(100)", "constraints": "NOT NULL"},
                            {"name": "description", "type": "TEXT", "constraints": ""},
                            {"name": "status", "type": "VARCHAR(20)", "constraints": "DEFAULT 'active'"},
                            {"name": "created_at", "type": "DATETIME", "constraints": "NOT NULL"},
                            {"name": "updated_at", "type": "DATETIME", "constraints": ""}
                        ]
                    }
                },
                "tech_stack": {
                    "language": "Python 3.11+",
                    "framework": "FastAPI",
                    "orm": "SQLAlchemy 2.0",
                    "database": "PostgreSQL 15",
                    "cache": "Redis 7",
                    "api_docs": "OpenAPI/Swagger"
                }
            })
        
        return json.dumps({
            "modules": modules_output,
            "architecture_notes": "采用分层架构：Router -> Service -> Repository",
            "security_considerations": [
                "所有接口需要 JWT 认证",
                "敏感数据加密存储",
                "SQL 注入防护",
                "请求频率限制"
            ]
        }, ensure_ascii=False, indent=2)

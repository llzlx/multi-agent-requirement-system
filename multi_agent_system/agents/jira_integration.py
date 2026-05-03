"""
JIRA 集成模块 - 与 JIRA API 交互
"""
import json
import base64
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class JIRAIssue:
    """JIRA Issue 结构"""
    key: str
    id: str
    summary: str
    description: str
    issue_type: str
    status: str
    priority: str
    assignee: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    components: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "key": self.key,
            "id": self.id,
            "summary": self.summary,
            "description": self.description,
            "issue_type": self.issue_type,
            "status": self.status,
            "priority": self.priority,
            "assignee": self.assignee,
            "labels": self.labels,
            "components": self.components
        }


class JIRAClient:
    """JIRA API 客户端"""
    
    def __init__(
        self,
        server: str,
        email: str,
        api_token: str,
        project_key: str
    ):
        self.server = server.rstrip("/")
        self.email = email
        self.api_token = api_token
        self.project_key = project_key
        self.api_base = f"{self.server}/rest/api/3"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {self._get_auth()}"
        }
    
    def _get_auth(self) -> str:
        """获取认证字符串"""
        auth_str = f"{self.email}:{self.api_token}"
        return base64.b64encode(auth_str.encode()).decode()
    
    def create_issue(self, issue_data: Dict) -> JIRAIssue:
        """创建 JIRA Issue"""
        url = f"{self.api_base}/issue"
        
        # 构建 issue 数据
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": issue_data.get("summary", ""),
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": issue_data.get("description", "")
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {"name": issue_data.get("issue_type", "Task")}
            }
        }
        
        # 添加优先级
        if issue_data.get("priority"):
            payload["fields"]["priority"] = {"name": issue_data["priority"]}
        
        # 添加标签
        if issue_data.get("labels"):
            payload["fields"]["labels"] = issue_data["labels"]
        
        # 添加组件
        if issue_data.get("components"):
            payload["fields"]["components"] = [
                {"name": c} for c in issue_data["components"]
            ]
        
        response = requests.post(
            url,
            headers=self.headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        return JIRAIssue(
            key=data["key"],
            id=data["id"],
            summary=issue_data.get("summary", ""),
            description=issue_data.get("description", ""),
            issue_type=issue_data.get("issue_type", "Task"),
            status="Created",
            priority=issue_data.get("priority", "Medium"),
            labels=issue_data.get("labels", []),
            components=issue_data.get("components", [])
        )
    
    def create_subtasks(
        self,
        parent_key: str,
        subtasks: List[Dict]
    ) -> List[JIRAIssue]:
        """创建子任务"""
        issues = []
        for subtask in subtasks:
            subtask_data = {
                **subtask,
                "issue_type": "Sub-task",
                "parent_key": parent_key
            }
            
            url = f"{self.api_base}/issue"
            payload = {
                "fields": {
                    "project": {"key": self.project_key},
                    "summary": subtask.get("summary", ""),
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": subtask.get("description", "")
                                    }
                                ]
                            }
                        ]
                    },
                    "issuetype": {"name": "Sub-task"},
                    "parent": {"key": parent_key}
                }
            }
            
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            issues.append(JIRAIssue(
                key=data["key"],
                id=data["id"],
                summary=subtask.get("summary", ""),
                description=subtask.get("description", ""),
                issue_type="Sub-task",
                status="Created",
                priority=subtask.get("priority", "Medium"),
                labels=subtask.get("labels", []),
                components=subtask.get("components", [])
            ))
        
        return issues
    
    def link_issues(self, parent_key: str, child_keys: List[str], link_type: str = "Blocks"):
        """链接 Issue"""
        for child_key in child_keys:
            url = f"{self.api_base}/issue/{child_key}/remotelink"
            payload = {
                "object": {
                    "url": f"{self.server}/browse/{parent_key}",
                    "title": parent_key
                }
            }
            
            requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
    
    def get_issue(self, issue_key: str) -> Dict:
        """获取 Issue 详情"""
        url = f"{self.api_base}/issue/{issue_key}"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def transition_issue(self, issue_key: str, transition_name: str):
        """转换 Issue 状态"""
        # 获取可用的转换
        url = f"{self.api_base}/issue/{issue_key}/transitions"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        transitions = response.json()["transitions"]
        
        # 找到目标转换
        target_id = None
        for t in transitions:
            if t["name"].lower() == transition_name.lower():
                target_id = t["id"]
                break
        
        if target_id:
            # 执行转换
            url = f"{self.api_base}/issue/{issue_key}/transitions"
            payload = {"transition": {"id": target_id}}
            requests.post(url, headers=self.headers, json=payload, timeout=30)
    
    def add_comment(self, issue_key: str, comment: str):
        """添加评论"""
        url = f"{self.api_base}/issue/{issue_key}/comment"
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comment
                            }
                        ]
                    }
                ]
            }
        }
        response = requests.post(url, headers=self.headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()


def create_module_issues(
    client: JIRACient,
    modules: List[Dict],
    requirement_id: str
) -> List[Dict]:
    """为模块创建 JIRA Issues"""
    issues = []
    
    for idx, module in enumerate(modules):
        module_id = module.get("module_id", f"MOD-{idx+1:03d}")
        module_name = module.get("module_name", f"模块{idx+1}")
        
        # 创建模块主任务
        main_issue_data = {
            "summary": f"[{requirement_id}] {module_name} - 开发",
            "description": f"""## 模块信息
- **模块ID**: {module_id}
- **模块名称**: {module_name}
- **模块类型**: {module.get('module_type', 'N/A')}
- **描述**: {module.get('description', 'N/A')}

## 子功能
{chr(10).join(f'- {f}' for f in module.get('sub_features', []))}

## 验收标准
{chr(10).join(f'- {c}' for c in module.get('acceptance_criteria', []))}

---
_由多 Agent 系统自动创建_""",
            "issue_type": "Epic" if module.get("module_type") == "core" else "Task",
            "priority": module.get("priority", "Medium"),
            "labels": ["ai-generated", requirement_id.lower()],
            "components": [module.get("module_type", "general")]
        }
        
        try:
            main_issue = client.create_issue(main_issue_data)
            issues.append({
                "module_id": module_id,
                "issue": main_issue.to_dict(),
                "subtasks": []
            })
            
            # 创建子任务
            subtasks = []
            
            # API 设计子任务
            if module.get("api_endpoints"):
                subtasks.append({
                    "summary": f"[{main_issue.key}] API 接口设计",
                    "description": "完成模块的 API 接口设计文档",
                    "priority": "High"
                })
            
            # 伪代码子任务
            if module.get("pseudo_code"):
                subtasks.append({
                    "summary": f"[{main_issue.key}] 伪代码实现",
                    "description": "完成模块的伪代码编写",
                    "priority": "High"
                })
            
            # 测试用例子任务
            if module.get("test_cases"):
                subtasks.append({
                    "summary": f"[{main_issue.key}] 编写测试用例",
                    "description": "完成模块的测试用例编写",
                    "priority": "Medium"
                })
            
            # 创建子任务
            if subtasks:
                created_subtasks = client.create_subtasks(main_issue.key, subtasks)
                issues[-1]["subtasks"] = [s.to_dict() for s in created_subtasks]
                
        except Exception as e:
            issues.append({
                "module_id": module_id,
                "error": str(e),
                "subtasks": []
            })
    
    return issues

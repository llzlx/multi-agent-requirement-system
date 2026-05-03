"""
输出 Agent - 汇总结果并创建 JIRA 任务
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base import BaseAgent, AgentRole, AgentOutput
from .jira_integration import JIRAClient, create_module_issues


class OutputAgent(BaseAgent):
    """输出 Agent - 汇总结果并创建 JIRA 任务"""
    
    def __init__(
        self,
        model_client: Any = None,
        jira_client: Optional[JIRACient] = None
    ):
        system_prompt = """你是一个项目经理。你的职责是汇总所有 Agent 的输出，生成最终的技术方案文档。"""
        
        super().__init__(
            name="OutputAgent",
            role=AgentRole.OUTPUT,
            goal="汇总结果并创建 JIRA 任务",
            system_prompt=system_prompt,
            model_client=model_client
        )
        self.jira_client = jira_client
    
    def process(
        self,
        requirement_id: str,
        original_requirement: str,
        planner_output: Dict,
        tech_output: Dict,
        test_output: Dict,
        use_jira: bool = False
    ) -> AgentOutput:
        """汇总所有输出，生成最终方案"""
        try:
            # 构建最终输出结构
            final_output = self._build_final_output(
                requirement_id,
                original_requirement,
                planner_output,
                tech_output,
                test_output
            )
            
            # 如果配置了 JIRA，创建任务
            jira_results = {"created": False, "issues": []}
            if use_jira and self.jira_client:
                try:
                    modules = tech_output.get("modules", [])
                    jira_results = {
                        "created": True,
                        "issues": create_module_issues(
                            self.jira_client,
                            modules,
                            requirement_id
                        )
                    }
                    final_output["jira_tasks"] = jira_results["issues"]
                except Exception as e:
                    jira_results["error"] = str(e)
                    final_output["jira_error"] = str(e)
            
            # 添加元数据
            final_output["metadata"] = {
                "generated_at": datetime.now().isoformat(),
                "agent_version": "1.0.0",
                "requirement_id": requirement_id
            }
            
            return self._format_output(
                final_output,
                metadata={"jira_created": jira_results["created"]}
            )
            
        except Exception as e:
            return self._format_output(
                content=None,
                success=False,
                error=str(e)
            )
    
    def _build_final_output(
        self,
        requirement_id: str,
        original_requirement: str,
        planner_output: Dict,
        tech_output: Dict,
        test_output: Dict
    ) -> Dict:
        """构建最终输出结构"""
        
        # 合并模块数据
        merged_modules = []
        tech_modules = tech_output.get("modules", [])
        test_modules = test_output.get("modules", [])
        
        # 创建模块索引
        tech_modules_map = {m["module_id"]: m for m in tech_modules}
        test_modules_map = {m["module_id"]: m for m in test_modules}
        
        # 获取规划器模块列表
        planner_modules = planner_output.get("functional_modules", [])
        
        for pm in planner_modules:
            module_id = pm.get("module_id", "MOD-001")
            
            merged_module = {
                "module_id": module_id,
                "module_name": pm.get("module_name", ""),
                "module_type": pm.get("module_type", ""),
                "description": pm.get("description", ""),
                "sub_features": pm.get("sub_features", []),
                "priority": pm.get("priority", "medium"),
                "dependencies": pm.get("dependencies", []),
                "acceptance_criteria": pm.get("acceptance_criteria", [])
            }
            
            # 合并技术信息
            if module_id in tech_modules_map:
                tm = tech_modules_map[module_id]
                merged_module["data_models"] = tm.get("data_models", {})
                merged_module["api_endpoints"] = tm.get("api_endpoints", [])
                merged_module["pseudo_code"] = tm.get("pseudo_code", "")
                merged_module["database_schema"] = tm.get("database_schema", {})
                merged_module["tech_stack"] = tm.get("tech_stack", {})
            
            # 合并测试信息
            if module_id in test_modules_map:
                tm = test_modules_map[module_id]
                merged_module["test_suites"] = tm.get("test_suites", [])
                merged_module["test_coverage"] = tm.get("test_coverage", {})
                merged_module["test_environment"] = tm.get("test_environment", {})
            
            merged_modules.append(merged_module)
        
        # 构建最终输出
        return {
            "requirement_id": requirement_id,
            "original_requirement": original_requirement,
            "created_at": datetime.now().isoformat(),
            "requirement_summary": planner_output.get("requirement_summary", ""),
            "stakeholders": planner_output.get("stakeholders", []),
            "non_functional_requirements": planner_output.get(
                "non_functional_requirements", {}
            ),
            "implementation_notes": planner_output.get("implementation_notes", ""),
            "modules": merged_modules,
            "architecture_notes": tech_output.get("architecture_notes", ""),
            "security_considerations": tech_output.get(
                "security_considerations", []
            ),
            "test_execution_plan": test_output.get("test_execution_plan", {}),
            "summary": self._generate_summary(
                requirement_id,
                merged_modules,
                planner_output,
                tech_output,
                test_output
            )
        }
    
    def _generate_summary(
        self,
        requirement_id: str,
        modules: List[Dict],
        planner_output: Dict,
        tech_output: Dict,
        test_output: Dict
    ) -> Dict:
        """生成方案摘要"""
        
        # 统计信息
        module_count = len(modules)
        total_endpoints = sum(
            len(m.get("api_endpoints", [])) for m in modules
        )
        total_test_cases = sum(
            sum(len(s.get("test_cases", [])) for s in m.get("test_suites", []))
            for m in modules
        )
        
        # 优先级分布
        priority_dist = {}
        for m in modules:
            p = m.get("priority", "medium")
            priority_dist[p] = priority_dist.get(p, 0) + 1
        
        # 模块类型分布
        type_dist = {}
        for m in modules:
            t = m.get("module_type", "general")
            type_dist[t] = type_dist.get(t, 0) + 1
        
        return {
            "requirement_id": requirement_id,
            "total_modules": module_count,
            "total_api_endpoints": total_endpoints,
            "total_test_cases": total_test_cases,
            "priority_distribution": priority_dist,
            "module_type_distribution": type_dist,
            "estimated_effort": self._estimate_effort(modules),
            "risk_assessment": self._assess_risks(modules)
        }
    
    def _estimate_effort(self, modules: List[Dict]) -> Dict:
        """估算工作量"""
        # 简单估算：每个模块基础 3 人天
        base_effort_per_module = 3
        
        # 根据类型调整
        type_multiplier = {
            "core": 2.0,
            "integration": 1.5,
            "support": 1.0,
            "report": 1.2
        }
        
        total_effort = 0
        effort_breakdown = []
        
        for m in modules:
            module_type = m.get("module_type", "support")
            multiplier = type_multiplier.get(module_type, 1.0)
            
            # 根据子功能数量调整
            sub_feature_count = len(m.get("sub_features", []))
            feature_adjustment = 1 + (sub_feature_count * 0.1)
            
            effort = base_effort_per_module * multiplier * feature_adjustment
            total_effort += effort
            
            effort_breakdown.append({
                "module_id": m.get("module_id", ""),
                "module_name": m.get("module_name", ""),
                "estimated_days": round(effort, 1)
            })
        
        return {
            "total_days": round(total_effort, 1),
            "breakdown": effort_breakdown,
            "note": "基于简单估算，实际工作量可能有所不同"
        }
    
    def _assess_risks(self, modules: List[Dict]) -> List[Dict]:
        """风险评估"""
        risks = []
        
        # 检查依赖关系
        modules_with_deps = [m for m in modules if m.get("dependencies")]
        if modules_with_deps:
            risks.append({
                "risk": "模块间依赖",
                "level": "medium",
                "description": f"{len(modules_with_deps)} 个模块存在依赖关系",
                "mitigation": "先完成无依赖的模块，建立清晰的接口契约"
            })
        
        # 检查集成模块
        integration_modules = [m for m in modules if m.get("module_type") == "integration"]
        if integration_modules:
            risks.append({
                "risk": "第三方集成",
                "level": "high",
                "description": f"涉及 {len(integration_modules)} 个第三方系统集成",
                "mitigation": "提前与第三方确认接口规范，准备 mock 方案"
            })
        
        # 检查核心模块
        core_modules = [m for m in modules if m.get("module_type") == "core"]
        if core_modules:
            risks.append({
                "risk": "核心模块复杂度",
                "level": "medium",
                "description": f"{len(core_modules)} 个核心模块，需要充分测试",
                "mitigation": "核心模块优先开发，配备资深开发资源"
            })
        
        return risks


def save_output(output: Dict, output_dir: str = "./output") -> str:
    """保存输出到文件"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    requirement_id = output.get("requirement_id", "unknown")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{requirement_id}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    return filepath

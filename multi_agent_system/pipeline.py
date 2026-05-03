"""
多 Agent 协作需求拆解系统

基于 AutoGen 风格的多 Agent 协作流程：
1. 规划 Agent - 拆分需求为功能模块
2. 技术 Agent - 生成接口设计和伪代码
3. 测试 Agent - 生成测试用例
4. 输出 Agent - 汇总结果并创建 JIRA 任务
"""

import json
import uuid
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from agents import (
    PlannerAgent,
    TechAgent,
    TestAgent,
    OutputAgent,
    PipelineContext,
    JIRAClient,
    save_output
)


class PipelineStatus(Enum):
    """管道状态"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PipelineConfig:
    """管道配置"""
    requirement_id: str = ""
    use_jira: bool = False
    jira_config: Optional[Dict] = None
    output_dir: str = "./output"
    verbose: bool = True
    save_intermediate: bool = True


class RequirementPipeline:
    """
    需求拆解管道

    协调多个 Agent 完成需求拆解的完整流程
    """

    def __init__(
        self,
        config: PipelineConfig,
        model_client: Any = None,
        logger: Optional[logging.Logger] = None
    ):
        self.config = config
        self.model_client = model_client
        self.logger = logger or self._setup_logger()

        # 初始化 Agent
        self._init_agents()

        # 管道状态
        self.status = PipelineStatus.IDLE
        self.context: Optional[PipelineContext] = None
        self.intermediate_outputs: Dict[str, Any] = {}

    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("RequirementPipeline")
        logger.setLevel(logging.DEBUG if self.config.verbose else logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _init_agents(self):
        """初始化所有 Agent"""
        self.planner = PlannerAgent(model_client=self.model_client)
        self.tech = TechAgent(model_client=self.model_client)
        self.test = TestAgent(model_client=self.model_client)

        # JIRA 客户端
        jira_client = None
        if self.config.use_jira and self.config.jira_config:
            jira_client = JIRACient(**self.config.jira_config)

        self.output = OutputAgent(
            model_client=self.model_client,
            jira_client=jira_client
        )

    def run(self, requirement: str) -> Dict[str, Any]:
        """
        运行完整的管道流程

        Args:
            requirement: 产品需求描述

        Returns:
            包含完整方案的字典
        """
        self.status = PipelineStatus.RUNNING

        # 生成需求 ID
        if not self.config.requirement_id:
            self.config.requirement_id = f"REQ-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        self.logger.info(f"开始处理需求: {self.config.requirement_id}")
        self.logger.info(f"原始需求: {requirement}")

        try:
            # 初始化上下文
            self.context = PipelineContext(
                requirement_id=self.config.requirement_id,
                original_requirement=requirement
            )

            # ==== 阶段 1: 规划 Agent ====
            self.logger.info("=" * 50)
            self.logger.info("阶段 1: 规划 Agent - 拆解功能模块")
            self.logger.info("=" * 50)

            planner_result = self._run_planner(requirement)
            self.context.planner_output = planner_result
            self.intermediate_outputs["planner"] = planner_result

            if self.config.save_intermediate:
                self._save_intermediate("01_planner_output.json", planner_result)

            # ==== 阶段 2: 技术 Agent ====
            self.logger.info("=" * 50)
            self.logger.info("阶段 2: 技术 Agent - 生成接口设计和伪代码")
            self.logger.info("=" * 50)

            tech_result = self._run_tech(planner_result)
            self.context.tech_output = tech_result
            self.intermediate_outputs["tech"] = tech_result

            if self.config.save_intermediate:
                self._save_intermediate("02_tech_output.json", tech_result)

            # ==== 阶段 3: 测试 Agent ====
            self.logger.info("=" * 50)
            self.logger.info("阶段 3: 测试 Agent - 生成测试用例")
            self.logger.info("=" * 50)

            test_result = self._run_test(tech_result)
            self.context.test_output = test_result
            self.intermediate_outputs["test"] = test_result

            if self.config.save_intermediate:
                self._save_intermediate("03_test_output.json", test_result)

            # ==== 阶段 4: 输出 Agent ====
            self.logger.info("=" * 50)
            self.logger.info("阶段 4: 输出 Agent - 汇总结果")
            self.logger.info("=" * 50)

            final_result = self._run_output(
                planner_result,
                tech_result,
                test_result
            )
            self.context.output = final_result
            self.intermediate_outputs["final"] = final_result

            # 保存最终输出
            output_path = save_output(
                final_result,
                self.config.output_dir
            )
            self.logger.info(f"最终输出已保存至: {output_path}")

            self.status = PipelineStatus.COMPLETED
            self.logger.info("=" * 50)
            self.logger.info("管道执行完成!")
            self.logger.info("=" * 50)

            return final_result

        except Exception as e:
            self.status = PipelineStatus.FAILED
            self.logger.error(f"管道执行失败: {str(e)}")
            raise

    def _run_planner(self, requirement: str) -> Dict:
        """运行规划 Agent"""
        self.logger.info("分析需求，拆解功能模块...")

        result = self.planner.process(requirement)

        if not result.success:
            raise RuntimeError(f"规划 Agent 执行失败: {result.error}")

        modules = result.content.get("functional_modules", [])
        self.logger.info(f"识别出 {len(modules)} 个功能模块:")
        for m in modules:
            self.logger.info(f"  - {m.get('module_id')}: {m.get('module_name')} ({m.get('priority', 'medium')})")

        return result.content

    def _run_tech(self, planner_output: Dict) -> Dict:
        """运行技术 Agent"""
        self.logger.info("设计接口和伪代码...")

        result = self.tech.process(planner_output)

        if not result.success:
            raise RuntimeError(f"技术 Agent 执行失败: {result.error}")

        modules = result.content.get("modules", [])
        total_endpoints = sum(len(m.get("api_endpoints", [])) for m in modules)
        self.logger.info(f"生成了 {len(modules)} 个模块的接口设计，共 {total_endpoints} 个 API 端点")

        return result.content

    def _run_test(self, tech_output: Dict) -> Dict:
        """运行测试 Agent"""
        self.logger.info("生成测试用例...")

        result = self.test.process(tech_output)

        if not result.success:
            raise RuntimeError(f"测试 Agent 执行失败: {result.error}")

        modules = result.content.get("modules", [])
        total_cases = sum(
            sum(len(s.get("test_cases", []))
                for s in m.get("test_suites", []))
            for m in modules
        )
        self.logger.info(f"生成了 {len(modules)} 个模块的测试用例，共 {total_cases} 个测试用例")

        return result.content

    def _run_output(
        self,
        planner_output: Dict,
        tech_output: Dict,
        test_output: Dict
    ) -> Dict:
        """运行输出 Agent"""
        self.logger.info("汇总结果并生成最终方案...")

        result = self.output.process(
            requirement_id=self.config.requirement_id,
            original_requirement=self.context.original_requirement,
            planner_output=planner_output,
            tech_output=tech_output,
            test_output=test_output,
            use_jira=self.config.use_jira
        )

        if not result.success:
            raise RuntimeError(f"输出 Agent 执行失败: {result.error}")

        # 打印摘要
        summary = result.content.get("summary", {})
        self.logger.info("-" * 30)
        self.logger.info("方案摘要:")
        self.logger.info(f"  - 需求ID: {summary.get('requirement_id')}")
        self.logger.info(f"  - 模块总数: {summary.get('total_modules')}")
        self.logger.info(f"  - API 端点总数: {summary.get('total_api_endpoints')}")
        self.logger.info(f"  - 测试用例总数: {summary.get('total_test_cases')}")

        effort = summary.get("estimated_effort", {})
        self.logger.info(f"  - 预估工作量: {effort.get('total_days')} 人天")

        # JIRA 创建情况
        jira_tasks = result.content.get("jira_tasks", [])
        if jira_tasks:
            self.logger.info(f"  - JIRA 任务: {len(jira_tasks)} 个已创建")
        elif self.config.use_jira:
            self.logger.warning("  - JIRA 任务: 创建失败")

        return result.content

    def _save_intermediate(self, filename: str, data: Any):
        """保存中间输出"""
        import os
        output_dir = os.path.join(self.config.output_dir, "intermediate")
        os.makedirs(output_dir, exist_ok=True)

        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.logger.debug(f"中间输出已保存: {filepath}")

    def get_pipeline_status(self) -> Dict:
        """获取管道状态"""
        return {
            "status": self.status.value,
            "requirement_id": self.config.requirement_id,
            "has_context": self.context is not None,
            "intermediate_stages": list(self.intermediate_outputs.keys())
        }


def create_pipeline(
    requirement: str,
    use_jira: bool = False,
    jira_config: Optional[Dict] = None,
    output_dir: str = "./output",
    verbose: bool = True,
    model_client: Any = None
) -> Dict[str, Any]:
    """
    便捷函数：创建并运行管道

    Args:
        requirement: 产品需求描述
        use_jira: 是否创建 JIRA 任务
        jira_config: JIRA 配置
        output_dir: 输出目录
        verbose: 是否输出详细信息
        model_client: LLM 模型客户端

    Returns:
        最终方案 JSON
    """
    config = PipelineConfig(
        requirement_id=f"REQ-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
        use_jira=use_jira,
        jira_config=jira_config,
        output_dir=output_dir,
        verbose=verbose
    )

    pipeline = RequirementPipeline(config, model_client=model_client)
    return pipeline.run(requirement)


if __name__ == "__main__":
    # 示例用法
    import os
    from dotenv import load_dotenv

    # 加载环境变量
    load_dotenv()

    # 示例需求
    sample_requirement = """
    我们需要开发一个用户管理系统，包含以下功能：
    1. 用户注册和登录
    2. 用户信息管理
    3. 用户权限控制
    4. 操作日志记录

    系统需要支持每日 10 万活跃用户，响应时间控制在 200ms 以内。
    """

    # 可选：配置 JIRA（需要设置环境变量或传入配置）
    jira_config = None
    if os.getenv("JIRA_EMAIL") and os.getenv("JIRA_API_TOKEN"):
        jira_config = {
            "server": os.getenv("JIRA_SERVER", "https://your-domain.atlassian.net"),
            "email": os.getenv("JIRA_EMAIL"),
            "api_token": os.getenv("JIRA_API_TOKEN"),
            "project_key": os.getenv("JIRA_PROJECT_KEY", "DEMO")
        }

    # 运行管道
    print("=" * 60)
    print("多 Agent 协作需求拆解系统")
    print("=" * 60)

    result = create_pipeline(
        requirement=sample_requirement,
        use_jira=False,  # 设置为 True 并配置 JIRA 以创建任务
        jira_config=jira_config,
        output_dir="./output",
        verbose=True
    )

    print("\n" + "=" * 60)
    print("最终输出 (JSON):")
    print("=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))

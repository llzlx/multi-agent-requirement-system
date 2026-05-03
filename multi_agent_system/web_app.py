"""
Streamlit Web 界面
"""
import streamlit as st
import json
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multi_agent_system.pipeline import create_pipeline, PipelineConfig, RequirementPipeline
from multi_agent_system.config import SystemConfig


st.set_page_config(
    page_title="多 Agent 需求拆解系统",
    page_icon="🤖",
    layout="wide"
)


def main():
    st.title("🤖 多 Agent 协作需求拆解系统")
    st.markdown("基于 AutoGen 风格的多 Agent 协作，将一句话需求自动拆解为完整技术方案")
    
    # 侧边栏配置
    with st.sidebar:
        st.header("⚙️ 配置")
        
        # JIRA 配置
        use_jira = st.toggle("启用 JIRA 集成", value=False)
        
        jira_config = None
        if use_jira:
            st.subheader("JIRA 配置")
            jira_server = st.text_input(
                "JIRA Server",
                value="https://your-domain.atlassian.net",
                help="JIRA 服务器地址"
            )
            jira_email = st.text_input("邮箱", help="JIRA 账号邮箱")
            jira_token = st.text_input(
                "API Token",
                type="password",
                help="JIRA API Token"
            )
            jira_project = st.text_input(
                "项目 Key",
                value="DEMO",
                help="JIRA 项目标识"
            )
            
            if jira_email and jira_token:
                jira_config = {
                    "server": jira_server,
                    "email": jira_email,
                    "api_token": jira_token,
                    "project_key": jira_project
                }
        
        output_dir = st.text_input(
            "输出目录",
            value="./output",
            help="方案输出目录"
        )
        
        st.divider()
        
        # 系统说明
        st.subheader("📖 系统说明")
        st.markdown("""
        **流程说明：**
        
        1. **规划 Agent** - 分析需求，拆解功能模块
        2. **技术 Agent** - 设计 API 接口，生成伪代码
        3. **测试 Agent** - 生成测试用例
        4. **输出 Agent** - 汇总结果，创建 JIRA 任务
        """)
    
    # 主内容区
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 输入需求")
        
        # 预设示例
        example_options = {
            "请选择示例...": None,
            "用户管理系统": """
开发一个用户管理系统，包含以下功能：
1. 用户注册和登录（支持邮箱、手机号）
2. 用户信息管理（查看、修改个人资料）
3. 用户权限控制（角色：管理员、普通用户）
4. 操作日志记录

系统需要支持每日 10 万活跃用户，响应时间控制在 200ms 以内。
""",
            "电商订单系统": """
开发一个电商订单处理系统，功能包括：
1. 商品管理（增删改查、上下架）
2. 购物车功能
3. 订单创建和支付
4. 订单状态跟踪
5. 售后服务（退款、退货）

预计日订单量 5 万单，需要对接支付宝和微信支付。
""",
            "社交分享功能": """
为现有应用添加社交分享功能：
1. 支持分享到微信、微博、QQ
2. 生成分享海报
3. 分享回调统计
4. 邀请好友奖励机制

需要追踪分享效果数据。
"""
        }
        
        selected_example = st.selectbox("快速示例", list(example_options.keys()))
        
        if selected_example != "请选择示例...":
            default_text = example_options[selected_example]
        else:
            default_text = ""
        
        requirement = st.text_area(
            "输入产品需求描述",
            value=default_text,
            height=250,
            placeholder="请输入一句话需求描述..."
        )
        
        submitted = st.button("🚀 开始拆解", type="primary", use_container_width=True)
    
    # 处理结果
    if submitted and requirement:
        with st.spinner("正在运行多 Agent 协作管道..."):
            try:
                # 运行管道
                result = create_pipeline(
                    requirement=requirement.strip(),
                    use_jira=use_jira,
                    jira_config=jira_config,
                    output_dir=output_dir,
                    verbose=True
                )
                
                st.success("✅ 拆解完成!")
                
                # 显示结果
                with col2:
                    st.header("📊 拆解结果")
                    
                    # 摘要信息
                    summary = result.get("summary", {})
                    
                    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                    
                    with metric_col1:
                        st.metric("功能模块", summary.get("total_modules", 0))
                    
                    with metric_col2:
                        st.metric("API 端点", summary.get("total_api_endpoints", 0))
                    
                    with metric_col3:
                        st.metric("测试用例", summary.get("total_test_cases", 0))
                    
                    with metric_col4:
                        effort = summary.get("estimated_effort", {})
                        st.metric("预估工时", f"{effort.get('total_days', 0)} 天")
                    
                    st.divider()
                    
                    # 选项卡展示详细内容
                    tab1, tab2, tab3, tab4 = st.tabs([
                        "📋 模块列表",
                        "🔌 API 设计",
                        "🧪 测试用例",
                        "📄 完整 JSON"
                    ])
                    
                    with tab1:
                        st.subheader("功能模块列表")
                        modules = result.get("modules", [])
                        for idx, module in enumerate(modules, 1):
                            with st.expander(
                                f"{idx}. {module.get('module_name', '模块')} "
                                f"[{module.get('priority', 'medium').upper()}]"
                            ):
                                st.markdown(f"**类型**: {module.get('module_type', 'N/A')}")
                                st.markdown(f"**描述**: {module.get('description', 'N/A')}")
                                st.markdown("**子功能**:")
                                for feature in module.get("sub_features", []):
                                    st.markdown(f"- {feature}")
                                st.markdown("**验收标准**:")
                                for criteria in module.get("acceptance_criteria", []):
                                    st.markdown(f"- {criteria}")
                    
                    with tab2:
                        st.subheader("API 接口设计")
                        for module in modules:
                            endpoints = module.get("api_endpoints", [])
                            if endpoints:
                                with st.expander(f"📁 {module.get('module_name')} ({len(endpoints)} 个端点)"):
                                    for ep in endpoints:
                                        method_color = {
                                            "GET": "🟢",
                                            "POST": "🔵",
                                            "PUT": "🟠",
                                            "DELETE": "🔴"
                                        }.get(ep.get("method", "GET"), "⚪")
                                        
                                        st.markdown(
                                            f"{method_color} **{ep.get('method', 'GET')}** "
                                            f"`{ep.get('path', '/')}`"
                                        )
                                        st.markdown(f"*{ep.get('description', '')}*")
                                        st.divider()
                                    
                                    # 伪代码
                                    pseudo_code = module.get("pseudo_code", "")
                                    if pseudo_code:
                                        with st.expander("📝 伪代码"):
                                            st.code(pseudo_code, language="python")
                    
                    with tab3:
                        st.subheader("测试用例")
                        for module in modules:
                            test_suites = module.get("test_suites", [])
                            if test_suites:
                                with st.expander(f"🧪 {module.get('module_name')} ({len(test_suites)} 个测试套件)"):
                                    for suite in test_suites:
                                        st.markdown(f"**{suite.get('suite_name')}** ({suite.get('test_type')})")
                                        for tc in suite.get("test_cases", [])[:5]:  # 只显示前5个
                                            priority_emoji = {
                                                "P0": "🔴",
                                                "P1": "🟠",
                                                "P2": "🟡",
                                                "P3": "🟢"
                                            }.get(tc.get("priority", "P2"), "⚪")
                                            
                                            st.markdown(
                                                f"{priority_emoji} {tc.get('case_id')}: "
                                                f"{tc.get('case_name')} ({tc.get('case_type')})"
                                            )
                                        st.divider()
                    
                    with tab4:
                        st.subheader("完整 JSON 方案")
                        st.json(result, expanded=False)
                        
                        # 下载按钮
                        json_str = json.dumps(result, ensure_ascii=False, indent=2)
                        st.download_button(
                            label="📥 下载 JSON",
                            data=json_str,
                            file_name=f"{result.get('requirement_id', 'requirement')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                
                # JIRA 任务信息
                jira_tasks = result.get("jira_tasks", [])
                if jira_tasks:
                    st.divider()
                    st.subheader("📎 JIRA 任务")
                    
                    jira_col1, jira_col2 = st.columns([1, 2])
                    
                    with jira_col1:
                        st.metric("已创建任务", len(jira_tasks))
                    
                    with jira_col2:
                        task_keys = [t.get("issue", {}).get("key", "N/A") for t in jira_tasks]
                        st.markdown("**任务列表**: " + ", ".join(task_keys))
                
            except Exception as e:
                st.error(f"❌ 执行失败: {str(e)}")
                import traceback
                with st.expander("详细错误信息"):
                    st.code(traceback.format_exc())
    
    elif submitted and not requirement:
        st.warning("⚠️ 请输入需求描述")


if __name__ == "__main__":
    main()

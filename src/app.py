import streamlit as st
from llm_client import EnhancedLLMClient
from report_generator import ReportGenerator, SlitherReportGenerator

# 页面全局配置
st.set_page_config(
    page_title="AI智能合约审计工具",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 全局标题
st.title("🔒 AI智能合约安全审计工具")
st.divider()

# 初始化客户端（缓存，避免重复加载）
@st.cache_resource
def init_clients():
    llm_client = EnhancedLLMClient()
    report_generator = ReportGenerator()
    slither_report_generator = SlitherReportGenerator()
    return llm_client, report_generator, slither_report_generator

llm_client, report_generator, slither_report_generator = init_clients()

# 审计模式选择
audit_mode = st.radio(
    "选择审计模式",
    ["🚀 快速审计 (LLM Only)", "🔬 深度审计 (Slither + LLM)"],
    horizontal=True
)

# 界面布局
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 输入待审计的Solidity合约")
    contract_code = st.text_area(
        "合约代码",
        height=400,
        placeholder="请粘贴你的Solidity合约代码，支持0.4.x ~ 0.8.x版本",
        label_visibility="collapsed"
    )
    
    audit_button = st.button("🚀 开始安全审计", type="primary", use_container_width=True)

with col2:
    st.subheader("📊 审计结果")
    if audit_button:
        if not contract_code.strip():
            st.warning("⚠️ 请先输入合约代码再执行审计")
        else:
            if audit_mode == "🚀 快速审计 (LLM Only)":
                with st.spinner("正在执行：合约解析 → 漏洞检索 → AI智能分析..."):
                    analysis_result = llm_client.analyze_contract_enhanced(contract_code)
                    st.session_state["analysis_result"] = analysis_result
                    st.session_state["contract_code"] = contract_code
                    st.session_state["audit_mode"] = "llm_only"
                    st.success("✅ 审计完成！")
                    st.markdown(analysis_result)
            else:
                with st.spinner("正在执行：Slither静态分析 → AI智能解释 → 报告生成..."):
                    slither_report = slither_report_generator.generate_slither_report(contract_code)
                    st.session_state["slither_report"] = slither_report
                    st.session_state["contract_code"] = contract_code
                    st.session_state["audit_mode"] = "slither_llm"
                    st.success("✅ 深度审计完成！")
                    
                    with st.expander("📋 查看详细报告", expanded=True):
                        st.markdown("### Slither分析摘要")
                        slither_result = slither_report["slither_analysis"]
                        if slither_result.get("success"):
                            summary = slither_result.get("summary", {})
                            cols = st.columns(5)
                            cols[0].metric("总问题", summary.get('total_issues', 0))
                            cols[1].metric("严重", summary.get('critical', 0), delta_color="inverse")
                            cols[2].metric("高危", summary.get('high', 0), delta_color="inverse")
                            cols[3].metric("中危", summary.get('medium', 0))
                            cols[4].metric("低危", summary.get('low', 0))
                            
                            st.markdown("### LLM专家分析")
                            for idx, item in enumerate(slither_report["llm_explanations"], 1):
                                finding = item["finding"]
                                with st.expander(f"{idx}. [{finding['severity']}] {finding['title']}"):
                                    st.markdown(f"**类型:** {finding['type']}")
                                    st.markdown(f"**描述:** {finding['description']}")
                                    st.markdown("**AI分析:**")
                                    st.markdown(item["explanation"])

# 报告导出区域
st.divider()
st.subheader("📥 导出审计报告")
if "audit_mode" in st.session_state:
    if st.session_state["audit_mode"] == "llm_only":
        html_report = report_generator.generate_html_report(
            st.session_state["analysis_result"],
            st.session_state["contract_code"]
        )
        st.download_button(
            label="下载HTML格式审计报告",
            data=html_report,
            file_name="智能合约安全审计报告.html",
            mime="text/html",
            use_container_width=True
        )
    else:
        html_report = st.session_state["slither_report"]["html_report"]
        st.download_button(
            label="下载深度审计报告 (Slither + LLM)",
            data=html_report,
            file_name="智能合约深度审计报告.html",
            mime="text/html",
            use_container_width=True
        )
else:
    st.info("请先完成合约审计，再导出结构化报告")
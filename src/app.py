import streamlit as st
from llm_client import EnhancedLLMClient
from report_generator import ReportGenerator

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
    return llm_client, report_generator

llm_client, report_generator = init_clients()

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
            with st.spinner("正在执行：合约解析 → 漏洞检索 → AI智能分析..."):
                # 调用增强版审计接口
                analysis_result = llm_client.analyze_contract_enhanced(contract_code)
                # 保存到会话状态，用于导出报告
                st.session_state["analysis_result"] = analysis_result
                st.session_state["contract_code"] = contract_code
                
                st.success("✅ 审计完成！")
                st.markdown(analysis_result)

# 报告导出区域
st.divider()
st.subheader("📥 导出审计报告")
if "analysis_result" in st.session_state:
    # 生成HTML结构化报告
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
    st.info("请先完成合约审计，再导出结构化报告")
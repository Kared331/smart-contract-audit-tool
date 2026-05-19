# src/config.py
import os

class Config:
    # LLM API配置
    LLM_API_URL = os.getenv("LLM_API_URL", "http://localhost:1234/v1")
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "qwen2.5-coder-7b-instruct-q4_k_m.gguf")

    # Slither配置
    SLITHER_PATH = os.getenv("SLITHER_PATH", "slither")
    SLITHER_TIMEOUT = int(os.getenv("SLITHER_TIMEOUT", "60"))

    # 知识库配置
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")

    # 分析参数
    TEMPERATURE = 0.3
    MAX_TOKENS = 1024

    # 报告生成配置
    ENABLE_LLM_EXPLANATION = os.getenv("ENABLE_LLM_EXPLANATION", "true").lower() == "true"
    REPORT_OUTPUT_DIR = os.getenv("REPORT_OUTPUT_DIR", "./reports")

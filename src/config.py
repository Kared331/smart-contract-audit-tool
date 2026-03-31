# src/config.py
import os

class Config:
    # LLM API配置
    LLM_API_URL = os.getenv("LLM_API_URL", "http://localhost:1234/v1")
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "qwen2.5-coder-7b-instruct-q4_k_m.gguf")

    # 知识库配置
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")

    # 分析参数
    TEMPERATURE = 0.3
    MAX_TOKENS = 1024

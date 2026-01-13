import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目路径
PROJECT_ROOT = "."
DATASETS_DIR = os.path.join(PROJECT_ROOT, "datasets")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")


# 数据集配置
LLM_DATASET_CONFIG = {
    "general_qa": {  # general_qa benchmark
        "local_path": os.path.join(DATASETS_DIR, "llm", "qa"),
        "subset_list": [
            "qa_with_reference"       
        ],
    },
    "text2sql": {  # text2sql benchmark
        "dataset_id": os.path.join(DATASETS_DIR, "llm", "text2sql"),  # 使用 dataset_id 覆盖 adapter 中的默认值
        "subset_list": [
            "example1",
            "example2",
        ],
    }
}


LLM_SERVER_CONFIG = {
    'deepseek-chat': {
        'model': os.getenv('DEEPSEEK_CHAT', 'deepseek-chat'),
        'url': os.getenv('DEEPSEEK_URL', 'https://api.deepseek.com'),
        'api_key': os.getenv('DEEPSEEK_API_KEY', ''),
        'params': '671B'
    },
    'deepseek-reasoner': {
        'model': os.getenv('DEEPSEEK_REASONER', 'deepseek-reasoner'),
        'url': os.getenv('DEEPSEEK_URL', 'https://api.deepseek.com'),
        'api_key': os.getenv('DEEPSEEK_API_KEY', ''),
        'params': '671B'
    },
    'Qwen/Qwen3-Next-80B-A3B-Instruct-FP8': {
        'model': os.getenv('QWEN3_80B', 'Qwen/Qwen3-Next-80B-A3B-Instruct-FP8'),
        'url': os.getenv('QWEN3_80B_URL'),
        'api_key': os.getenv('QWEN3_80B_API_KEY', ''),
        'params': '80B'
    }
}



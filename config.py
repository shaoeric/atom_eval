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
}



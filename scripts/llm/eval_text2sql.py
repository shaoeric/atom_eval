import os
import sys
import logging
from evalscope.run import run_task

# 将项目根目录和 evalscope 源码目录添加到 sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from config import LLM_SERVER_CONFIG, LLM_DATASET_CONFIG, PROJECT_ROOT
import benchmarks.text2sql.text2sql_adapter

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



def main():
    # 1. 配置待评测的模型
    model_name = os.getenv('USE_LLM_NAME', 'deepseek-chat')
    if model_name not in LLM_SERVER_CONFIG:
        logger.error(f"模型 {model_name} 不在 LLM_SERVER_CONFIG 中")
        return
    
    model_config = LLM_SERVER_CONFIG[model_name]
    
    # 2. 获取数据集配置
    # 该数据集应包含 question, schema, 和 ground_truth
    dataset_name = 'text2sql'
    dataset_config = LLM_DATASET_CONFIG[dataset_name]
    
    # 3. 构造任务配置
    # 我们使用自定义的 text2sql benchmark，它将计算 SQL AST 相似性
    task_cfg = {
        "model": model_config['model'],
        "api_url": model_config['url'],
        "api_key": model_config['api_key'],
        "eval_type": "openai_api",
        "datasets": [dataset_name],
        "dataset_args": {
            dataset_name: dataset_config
        },
        "generation_config": {
            "batch_size": 1,
            "temperature": 0.0
        },
        "work_dir": os.path.join(PROJECT_ROOT, "results", "text2sql", model_name),
        "no_timestamp": True,
    }

    try:
        # 执行评估
        run_task(task_cfg)
        logger.info("评估任务圆满完成。")
    except Exception as e:
        logger.error(f"评估执行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()

import os
import sys
import logging
from evalscope.run import run_task

# 将项目根目录和 evalscope 源码目录添加到 sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from config import LLM_SERVER_CONFIG

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



def main():
    # 1. 配置待评测的模型
    # 从环境变量或 config.py 获取模型配置
    model_name = os.getenv('USE_LLM_NAME', 'deepseek-chat')
    if model_name not in LLM_SERVER_CONFIG:
        logger.error(f"模型 {model_name} 不在 LLM_SERVER_CONFIG 中")
        return
    
    model_config = LLM_SERVER_CONFIG[model_name]
    
    # 2. 指定数据集文件
    # 该数据集应包含 question, contexts (或 schema), 和 ground_truth
    dataset_name = 'text2sql'
    dataset_file = os.path.join(PROJECT_ROOT, "datasets", "llm", "text2sql", "sample_text2sql.json")
    
    if not os.path.exists(dataset_file):
        logger.error(f"测试集文件不存在: {dataset_file}")
        return

    # 3. 构造任务配置
    # 我们使用自定义的 text2sql benchmark，它将计算 SQL AST 相似性
    task_cfg = {
        "model": model_config['model'],
        "api_url": model_config['url'],
        "api_key": model_config['api_key'],
        "eval_type": "openai_api",
        "datasets": [dataset_name],
        "dataset_args": {
            dataset_name: {
                "local_path": os.path.dirname(dataset_file),
                "subset_list": [
                    "sample_text2sql"       
                ],
            }
        },
        "generation_config": {
            "batch_size": 1,
            "temperature": 0.0
        },
        "work_dir": os.path.join(PROJECT_ROOT, "results", "text2sql", model_name),
        "no_timestamp": True,
    }

    logger.info(f"开始执行 text2sql 评估任务 (AST Similarity)...")
    logger.info(f"模型: {model_name}")
    logger.info(f"数据集: {dataset_file}")
    
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

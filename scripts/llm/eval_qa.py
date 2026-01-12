import argparse
import sys
import os
import logging
from evalscope.run import run_task
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import LLM_SERVER_CONFIG, LLM_DATASET_CONFIG, PROJECT_ROOT

# 设置基础日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="QA Evaluation via EvalScope")
    parser.add_argument("--model", type=str, default=None, help="模型名称")
    parser.add_argument("--dataset", type=str, default="general_qa", help="数据集名称")
    parser.add_argument("--limit", type=int, default=None, help="样本限制数量")
    args = parser.parse_args()

    model_name = args.model if args.model else os.environ['USE_LLM_NAME']
    model_config = LLM_SERVER_CONFIG[model_name]
    params = model_config['params']  # 参数量
    
    dataset_config = LLM_DATASET_CONFIG[args.dataset]
    work_dir = os.path.join(PROJECT_ROOT, "results", args.dataset, model_name, params)

    task_config = {
        "model": model_config['model'],
        "api_url": model_config['url'],
        "api_key": model_config['api_key'],
        "eval_type": "openai_api",
        "datasets": [args.dataset],
        "limit": args.limit,
        "dataset_args": {
            args.dataset: dataset_config
        },
        "generation_config": {
            "batch_size": 1,
            "temperature": 0.0
        },
        "work_dir": work_dir,
        "no_timestamp": True,
        "timeout": 600,
    }

    logger.info(f"开始评测任务: model={args.model}, dataset={args.dataset}")
    
    try:
        # 执行评测
        run_task(task_config)
        logger.info("评测任务圆满完成。")
    except Exception as e:
        logger.error(f"评测执行失败: {e}")
        sys.exit(1)

    

if __name__ == "__main__":
    main()

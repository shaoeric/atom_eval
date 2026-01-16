import sys
import os
import logging
from evalscope.run import run_task

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils import parse_args, get_task_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# python benchmarks/general_fc/main.py --model Qwen/Qwen3-Next-80B-A3B-Instruct-FP8
def main():
    args = parse_args(benchmark_name="general_fc")
    task_config = get_task_config(args)

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

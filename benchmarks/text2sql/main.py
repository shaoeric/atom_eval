import os
import sys
import logging
from evalscope.run import run_task

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils import parse_args, get_task_config

import benchmarks.text2sql.text2sql_adapter

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# python benchmarks/text2sql/main.py --model Qwen/Qwen3-Next-80B-A3B-Instruct-FP8
def main():
    args = parse_args(benchmark_name="text2sql")
    task_config = get_task_config(args)

    try:
        run_task(task_config)
    except Exception as e:
        logger.error(f"评估执行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()

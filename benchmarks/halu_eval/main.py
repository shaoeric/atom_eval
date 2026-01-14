import os
import sys
import logging

# 预导入 datasets 以确保 modelscope 可以正确导入相关模块
# 注意：需要 datasets==3.6.0，datasets 4.x 版本不兼容
import datasets

from evalscope.run import run_task

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils import parse_args, get_task_config

import benchmarks.halu_eval.halu_eval_adapter

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# python benchmarks/halu_eval/main.py --model Qwen/Qwen3-Next-80B-A3B-Instruct-FP8
def main():
    args = parse_args(benchmark_name="halu_eval")
    task_config = get_task_config(args)

    logger.info(f"开始评测任务: model={args.model}, dataset={args.dataset}")
    
    try:
        # 执行评测
        run_task(task_config)
        logger.info("评测任务圆满完成。")
    except Exception as e:
        logger.error(f"评估执行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()

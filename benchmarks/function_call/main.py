import os
import sys
import logging
from evalscope import TaskConfig, run_task

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils import parse_args, get_task_config


args = parse_args(benchmark_name="general_fc")
task_cfg = get_task_config(args)
run_task(task_cfg=task_cfg)

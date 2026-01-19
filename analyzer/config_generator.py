"""配置生成器，根据推荐的 benchmark 生成评测配置。"""
import os
import argparse
from typing import List, Dict, Any
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import get_task_config
import config


class ConfigGenerator:
    """评测配置生成器"""
    
    def __init__(self):
        pass
    
    def generate_single_config(
        self,
        benchmark_name: str,
        model_name: str,
        batch_size: int = 1,
        max_tokens: int = 2048,
        limit: int = None,
        use_llm_judge: bool = False,
        judge_model_name: str = None,
        work_dir: str = None,
    ) -> Dict[str, Any]:
        """
        为单个 benchmark 和 model 的组合生成评测配置
        
        Args:
            benchmark_name: benchmark 名称
            model_name: 模型名称
            batch_size: 批量大小
            max_tokens: 最大 token 数
            limit: 样本限制数量
            use_llm_judge: 是否使用 LLM judge
            judge_model_name: LLM judge 模型名称
            work_dir: 工作目录
            
        Returns:
            评测配置字典
        """
        # 创建模拟的 args 对象
        class Args:
            def __init__(self):
                self.model = model_name
                self.dataset = benchmark_name
                self.batch_size = batch_size
                self.max_tokens = max_tokens
                self.limit = limit
                self.use_llm_judge = use_llm_judge
                self.judge_model_name = judge_model_name
                self.work_dir = work_dir
        
        args = Args()
        
        # 使用现有的 get_task_config 函数生成配置
        task_config = get_task_config(args)
        return task_config
    
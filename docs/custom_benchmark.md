# 自定义 Benchmark 配置

本文档介绍如何在 Atom Eval 中创建和配置自定义评估任务（Benchmark）。

## 概述

创建自定义 benchmark 需要以下步骤：

1. 创建 Benchmark 目录结构
2. 实现 Adapter（数据适配器）
3. 创建主入口文件
4. 配置数据集
5. 准备数据集
6. 创建 README 文档
7. 运行自定义 Benchmark

## 1. 创建 Benchmark 目录结构

在 `benchmarks/` 目录下创建新的任务目录：

```bash
mkdir -p benchmarks/your_benchmark
```

## 2. 实现 Adapter

创建 `your_benchmark_adapter.py` 文件，实现自定义的数据适配器。

### 基本结构

```python
from evalscope.api.benchmark import BenchmarkMeta, DefaultDataAdapter
from evalscope.api.dataset import Sample
from evalscope.api.evaluator import TaskState
from evalscope.api.metric import Score
from evalscope.api.registry import register_benchmark
from evalscope.constants import Tags

@register_benchmark(
    BenchmarkMeta(
        name='your_benchmark',
        dataset_id='your_dataset',
        pretty_name='Your Benchmark',
        tags=[Tags.REASONING],  # 根据任务类型选择标签
        metric_list=['accuracy'],  # 评估指标列表
        prompt_template='Your prompt template: {input}',
    )
)
class YourBenchmarkAdapter(DefaultDataAdapter):
    def record_to_sample(self, record):
        """将数据记录转换为评估样本"""
        # 实现数据记录到样本的转换
        return Sample(
            input=record['input'],
            target=record['target']
        )
    
    def extract_answer(self, prediction, task_state):
        """从模型输出中提取答案"""
        # 实现从模型输出中提取答案的逻辑
        return prediction.strip()
    
    def match_score(self, original_prediction, filtered_prediction, reference, task_state):
        """计算评分"""
        # 实现评分逻辑
        score = Score(
            extracted_prediction=filtered_prediction,
            prediction=original_prediction,
            value={'accuracy': 1.0 if filtered_prediction == reference else 0.0},
            main_score_name='accuracy'
        )
        return score
```

### 关键方法说明

#### record_to_sample

将数据记录转换为 `Sample` 对象：

```python
def record_to_sample(self, record):
    """
    Args:
        record: 数据记录（字典格式）
    
    Returns:
        Sample: 包含 input 和 target 的样本对象
    """
    return Sample(
        input=record['input'],  # 模型输入
        target=record['target']  # 标准答案
    )
```

#### extract_answer

从模型输出中提取答案，用于后续评分：

```python
def extract_answer(self, prediction, task_state):
    """
    Args:
        prediction: 模型的原始输出
        task_state: 任务状态对象
    
    Returns:
        str: 提取的答案
    """
    # 示例：提取代码块中的内容
    import re
    pattern = r'```python\n(.*?)\n```'
    match = re.search(pattern, prediction, re.DOTALL)
    if match:
        return match.group(1).strip()
    return prediction.strip()
```

#### match_score

计算模型输出与标准答案的匹配分数：

```python
def match_score(self, original_prediction, filtered_prediction, reference, task_state):
    """
    Args:
        original_prediction: 模型原始输出
        filtered_prediction: 提取后的答案
        reference: 标准答案
        task_state: 任务状态对象
    
    Returns:
        Score: 评分对象
    """
    from evalscope.metrics import exact_match
    
    score = Score(
        extracted_prediction=filtered_prediction,
        prediction=original_prediction,
        value={'accuracy': exact_match(gold=reference, pred=filtered_prediction)},
        main_score_name='accuracy'
    )
    return score
```

### 参考示例

- **Text2SQL**: [benchmarks/text2sql/text2sql_adapter.py](../benchmarks/text2sql/text2sql_adapter.py)
  - 自定义 SQL 提取逻辑
  - 使用 AST 相似度评分
  
- **HaluEval**: [benchmarks/halu_eval/halu_eval_adapter.py](../benchmarks/halu_eval/halu_eval_adapter.py)
  - 自定义聚合指标（accuracy, precision, recall, f1_score）
  - 多子任务支持

- **FRAMES**: [benchmarks/frames/frames_adapter.py](../benchmarks/frames/frames_adapter.py)
  - 支持 LLM Judge 评估
  - 长上下文处理

## 3. 创建主入口文件

创建 `main.py` 文件：

```python
import sys
import os
import logging
from evalscope.run import run_task

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils import parse_args, get_task_config

# 导入 adapter（确保 adapter 被注册）
import benchmarks.your_benchmark.your_benchmark_adapter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    args = parse_args(benchmark_name="your_benchmark")
    task_config = get_task_config(args)
    
    logger.info(f"开始评测任务: model={args.model}, dataset={args.dataset}")
    
    try:
        run_task(task_config)
        logger.info("评测任务圆满完成。")
    except Exception as e:
        logger.error(f"评测执行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**重要**：确保在 `main.py` 中导入 adapter，这样 adapter 才会被注册。

## 4. 配置数据集

在 `config.py` 的 `LLM_DATASET_CONFIG` 中添加数据集配置：

```python
LLM_DATASET_CONFIG = {
    # 现有配置...
    
    "your_benchmark": {
        "local_path": os.path.join(DATASETS_DIR, "llm", "your_benchmark"),
        "subset_list": [
            "subset1",
            "subset2"
        ]
    }
}
```

### 配置选项说明

- `local_path`: 数据集本地路径
- `subset_list`: 子集列表，对应数据集目录下的文件名（不含扩展名）

如果使用 `dataset_id` 而不是 `local_path`，adapter 中的 `dataset_id` 会被覆盖：

```python
"your_benchmark": {
    "dataset_id": os.path.join(DATASETS_DIR, "llm", "your_benchmark"),
    "subset_list": ["subset1", "subset2"]
}
```

## 5. 准备数据集

在 `datasets/llm/your_benchmark/` 目录下放置数据集文件，格式为 **JSONL**（每行一个 JSON 对象）：

```jsonl
{"input": "问题1", "target": "答案1"}
{"input": "问题2", "target": "答案2"}
{"input": "问题3", "target": "答案3"}
```

### 数据集文件命名

- 如果 `subset_list` 为 `["subset1", "subset2"]`
- 则数据集文件应为：`subset1.jsonl` 和 `subset2.jsonl`

### 数据格式要求

- 每行一个 JSON 对象
- 必须包含 adapter 的 `record_to_sample` 方法中使用的字段
- 建议包含 `input` 和 `target` 字段

## 6. 创建 README 文档

在 benchmark 目录下创建 `README.md`，包含以下内容：

1. **任务描述**：说明该 benchmark 的评估目标和任务类型
2. **数据集样例**：展示 JSONL 格式的数据样例（至少两行）
3. **字段说明**：说明每个字段的含义和是否必选
4. **启动命令**：如何运行该 benchmark
5. **评价指标样例**：展示评估结果的格式
6. **评价指标说明**：详细说明每个指标的计算方式和含义

参考示例：[benchmarks/general_qa/README.md](../benchmarks/general_qa/README.md)

## 7. 运行自定义 Benchmark

配置完成后，可以运行自定义 benchmark：

```bash
python benchmarks/your_benchmark/main.py --model deepseek-chat
```

### 测试运行

建议先用少量样本测试：

```bash
python benchmarks/your_benchmark/main.py --model deepseek-chat --limit 5
```

## 高级功能

### 自定义评估指标

如果需要自定义评估指标，可以在 `match_score` 方法中实现：

```python
def match_score(self, original_prediction, filtered_prediction, reference, task_state):
    # 自定义评分逻辑
    custom_score = calculate_custom_metric(filtered_prediction, reference)
    
    score = Score(
        extracted_prediction=filtered_prediction,
        prediction=original_prediction,
        value={
            'custom_metric': custom_score,
            'accuracy': 1.0 if filtered_prediction == reference else 0.0
        },
        main_score_name='custom_metric'
    )
    return score
```

### 支持 LLM Judge

参考 FRAMES benchmark 的实现，支持使用 LLM 作为评估器：

```python
def llm_match_score(self, original_prediction, filtered_prediction, reference, task_state):
    """使用 LLM Judge 进行评估"""
    # 实现 LLM Judge 逻辑
    pass
```

### 多子任务支持

如果 benchmark 包含多个子任务，可以在 `BenchmarkMeta` 中配置：

```python
BenchmarkMeta(
    name='your_benchmark',
    subset_list=['task1', 'task2', 'task3'],
    # ...
)
```

## 常见问题

### Q: Adapter 没有被注册怎么办？

A: 确保在 `main.py` 中导入了 adapter 模块：
```python
import benchmarks.your_benchmark.your_benchmark_adapter
```

### Q: 数据集加载失败怎么办？

A: 检查以下几点：
1. 数据集路径是否正确
2. 文件格式是否为 JSONL
3. 文件命名是否与 `subset_list` 匹配
4. JSON 格式是否正确

### Q: 如何实现复杂的评分逻辑？

A: 可以在 `match_score` 方法中实现任意复杂的评分逻辑，包括：
- 调用外部评估工具
- 使用机器学习模型评分
- 实现多维度评分

### Q: 如何支持批量评估？

A: EvalScope 框架会自动处理批量评估，只需在运行时指定 `--batch_size` 参数即可。

## 最佳实践

1. **保持代码简洁**：Adapter 应该只负责数据转换和评分，复杂逻辑可以抽取到独立模块
2. **完善的文档**：README 应该包含足够的信息，让其他人能够理解和使用
3. **充分的测试**：使用 `--limit` 参数进行小规模测试，确保一切正常
4. **遵循命名规范**：使用清晰、描述性的名称
5. **错误处理**：在关键位置添加错误处理和日志记录

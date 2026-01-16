# FRAMES Benchmark

## 任务描述

FRAMES 是一个综合评估数据集，用于测试检索增强生成（RAG）系统在以下方面的能力：
1. **事实性（Factuality）**：生成内容与提供知识的一致性
2. **检索准确性（Retrieval Accuracy）**：从给定上下文中提取正确信息的能力
3. **推理能力（Reasoning）**：基于提供的信息进行推理和回答的能力

该 benchmark 提供长上下文（包含多个维基百科条目），要求模型基于这些信息回答问题。

## 数据集样例

数据集位于 `datasets/llm/frames/` 目录下，**文件格式为 JSONL（每行一个 JSON 对象）**。

### 数据格式示例

```jsonl
{"wiki_items": [{"title": "Python编程语言", "text": "Python是一种高级、解释型的编程语言，以其简洁性和可读性而闻名。它由Guido van Rossum创建，于1991年首次发布。Python支持多种编程范式，包括过程式、面向对象和函数式编程。"}, {"title": "编程语言", "text": "编程语言是一种形式语言，包含一组产生各种输出的指令。编程语言用于计算机编程以实现算法。"}], "Prompt": "Python是哪一年首次发布的？", "Answer": "1991"}
{"wiki_items": [{"title": "珠穆朗玛峰", "text": "珠穆朗玛峰是地球上海拔最高的山峰，位于喜马拉雅山脉的马哈兰古尔喜马拉雅子山脉。中尼边界横跨其峰顶。其海拔8848.86米，是2020年由中国和尼泊尔当局最新确定的。"}, {"title": "喜马拉雅山脉", "text": "喜马拉雅山脉是亚洲的一个山脉，将印度次大陆的平原与青藏高原分开。该山脉拥有许多地球最高峰，包括最高的珠穆朗玛峰。"}], "Prompt": "珠穆朗玛峰的海拔是多少米？", "Answer": "8848.86"}
```

### 字段说明

- `wiki_items`（必选）：维基百科条目列表，每个条目是一个对象，包含：
  - `title`（必选）：条目标题
  - `text`（必选）：条目正文内容
- `Prompt`（必选）：需要回答的问题
- `Answer`（必选）：标准答案，用于评估模型输出的准确性

## 启动命令

### 基础命令

```bash
python benchmarks/frames/main.py --model <model_name>
```

### 使用 LLM Judge 评估

FRAMES 支持使用 LLM Judge 进行更灵活的评估：

```bash
python benchmarks/frames/main.py --model <model_name> --use_llm_judge --judge_model_name <judge_model>
```

### 参数说明

- `--model`: 模型名称（必选）
  - 可选值：`deepseek-chat`, `deepseek-reasoner`, `Qwen/Qwen3-Next-80B-A3B-Instruct-FP8`
- `--dataset`: 数据集名称（默认：`FRAMES`）
- `--batch_size`: 批量大小（默认：1）
- `--max_tokens`: 最大token数（默认：2048）
- `--limit`: 样本限制数量（可选）
- `--use_llm_judge`: 是否使用 LLM Judge 进行评估（可选）
- `--judge_model_name`: LLM Judge 模型名称（使用 `--use_llm_judge` 时必选）

### 示例

```bash
# 使用 DeepSeek Chat 模型，标准评估
python benchmarks/frames/main.py --model deepseek-chat

# 使用 LLM Judge 评估（使用 deepseek-reasoner 作为 judge）
python benchmarks/frames/main.py --model deepseek-chat --use_llm_judge --judge_model_name deepseek-reasoner

# 使用 Qwen3 模型，限制50个样本
python benchmarks/frames/main.py --model Qwen/Qwen3-Next-80B-A3B-Instruct-FP8 --limit 50
```

## 评价指标样例

### 标准评估结果

评测结果会生成在 `results/FRAMES/<model_name>_<params>/reports/` 目录下，示例结果：

```json
{
  "name": "deepseek-chat@FRAMES",
  "dataset_name": "FRAMES",
  "model_name": "deepseek-chat",
  "score": 0.625,
  "metrics": [
    {
      "name": "mean_acc",
      "num": 8,
      "score": 0.625
    }
  ]
}
```

### LLM Judge 评估结果

使用 LLM Judge 时，结果中会包含额外的元数据：

```json
{
  "sample_score": {
    "score": {
      "value": {
        "acc": 1.0
      },
      "explanation": "LLM judge: YES",
      "metadata": {
        "source": "llm_judge",
        "judge_strategy": "auto",
        "model": "deepseek-reasoner"
      }
    }
  }
}
```

## 评价指标说明

### acc (准确率)
- **定义**：模型答案与标准答案完全匹配的比例
- **范围**：0-1，值越高表示答案越准确
- **计算方式**：
  1. 从模型输出中提取答案（支持中文格式："答案是..."）
  2. 对答案进行标准化处理（去除标点、转换为小写等）
  3. 与标准答案进行精确匹配

### 评估模式

#### 1. 标准评估模式（默认）
- **方法**：基于文本精确匹配
- **优点**：快速、客观
- **缺点**：对语义相同但表达不同的答案可能误判

#### 2. LLM Judge 评估模式
- **方法**：使用另一个 LLM 模型判断答案是否正确
- **优点**：
  - 能够理解语义等价性
  - 对格式要求更宽松
  - 可以处理复杂推理问题
- **缺点**：
  - 评估时间更长
  - 需要额外的 judge 模型
  - 可能存在 judge 模型的偏差

### 答案提取

模型输出会被自动处理以提取答案：
- 支持中文格式：`"因此，答案是（答案内容）"`
- 自动去除标点符号和多余字符
- 进行大小写和空白字符标准化

### 答案标准化

答案会经过以下标准化处理：
- 转换为小写
- 去除标点符号
- 去除冠词（如 "the", "a", "an"）
- 标准化空白字符

## 注意事项

1. 数据集文件应放在 `datasets/llm/frames/` 目录下，文件格式为 JSONL（每行一个JSON对象）
2. 该 benchmark 包含长上下文，需要模型具备良好的长文本理解能力
3. 建议使用 `--use_llm_judge` 选项以获得更准确的评估结果，特别是对于需要推理的问题
4. Judge 模型应该选择推理能力较强的模型（如 `deepseek-reasoner`）
5. 标准评估模式对答案格式要求较严格，模型应按照提示词格式输出答案
6. 建议使用 `--limit` 参数在开发阶段限制样本数量以加快测试速度
7. 该 benchmark 测试的是 RAG 能力，模型需要能够从多个文档片段中提取和整合信息

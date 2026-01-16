# General QA Benchmark

## 任务描述

General QA 是一个通用问答评测任务，用于评估大语言模型在问答任务上的表现。该 benchmark 支持多种问答格式，包括简单的查询-回答格式和对话格式。

## 数据集样例

数据集位于 `datasets/llm/qa/` 目录下，**文件格式为 JSONL（每行一个 JSON 对象）**。

### 数据格式示例

```jsonl
{"system": "你是一位地理学家，请回答问题。不要解释，直接回答是：[答案]。", "query": "中国的首都是哪里？", "response": "北京"}
{"query": "世界上最高的山是哪座山？不要解释，直接回答是：[答案]。", "response": "珠穆朗玛峰"}
```

### 字段说明

- `system`（可选）：系统提示词，用于设置模型的角色和行为
- `query`（可选）：用户的问题或查询，当使用 `messages` 格式时不需要此字段
- `messages`（可选）：对话消息列表，每个消息包含：
  - `role`: 角色（"system" 或 "user"）
  - `content`: 消息内容
- `response`（必选）：标准答案，用于评估模型输出的准确性

**注意**：每条数据必须包含 `response` 字段，输入可以使用 `query` 或 `messages` 格式之一。

## 启动命令

```bash
python benchmarks/general_qa/main.py --model <model_name>
```

### 参数说明

- `--model`: 模型名称（必选）
  - 可选值：`deepseek-chat`, `deepseek-reasoner`, `Qwen/Qwen3-Next-80B-A3B-Instruct-FP8`
- `--dataset`: 数据集名称（默认：`general_qa`）
- `--batch_size`: 批量大小（默认：1）
- `--max_tokens`: 最大token数（默认：2048）
- `--limit`: 样本限制数量（可选）

### 示例

```bash
# 使用 DeepSeek Chat 模型
python benchmarks/general_qa/main.py --model deepseek-chat

# 使用 Qwen3 模型，限制100个样本
python benchmarks/general_qa/main.py --model Qwen/Qwen3-Next-80B-A3B-Instruct-FP8 --limit 100
```

## 评价指标样例

评测结果会生成在 `results/general_qa/<model_name>_<params>/reports/` 目录下，示例结果：

```json
{
  "name": "deepseek-chat@general_qa",
  "dataset_name": "general_qa",
  "model_name": "deepseek-chat",
  "score": 0.5833,
  "metrics": [
    {
      "name": "mean_bleu-1",
      "num": 3,
      "score": 0.5833
    },
    {
      "name": "mean_bleu-2",
      "num": 3,
      "score": 0.0
    },
    {
      "name": "mean_bleu-3",
      "num": 3,
      "score": 0.0
    }
  ]
}
```

## 评价指标说明

### BLEU-1 (1-gram BLEU)
- **定义**：计算预测答案和参考答案之间1-gram（单词级别）的重叠度
- **范围**：0-1，值越高表示答案越准确
- **说明**：衡量答案中单词级别的匹配程度

### BLEU-2 (2-gram BLEU)
- **定义**：计算预测答案和参考答案之间2-gram（连续两个单词）的重叠度
- **范围**：0-1，值越高表示答案越准确
- **说明**：衡量答案中短语级别的匹配程度，比BLEU-1更严格

### BLEU-3 (3-gram BLEU)
- **定义**：计算预测答案和参考答案之间3-gram（连续三个单词）的重叠度
- **范围**：0-1，值越高表示答案越准确
- **说明**：衡量答案中更长短语的匹配程度，评估更严格

### 其他指标
根据数据集配置，还可能包含 ROUGE 系列指标（ROUGE-1, ROUGE-2, ROUGE-L）等。

## 注意事项

1. 数据集文件应放在 `datasets/llm/qa/` 目录下，文件格式为 JSONL（每行一个JSON对象）
2. 支持多种输入格式，系统会自动识别并处理
3. 评价指标基于文本相似度，对于语义相同但表达不同的答案可能得分较低
4. 建议使用 `--limit` 参数在开发阶段限制样本数量以加快测试速度

# HaluEval Benchmark

## 任务描述

HaluEval 是一个用于评估大语言模型识别幻觉（Hallucination）能力的大规模评测数据集。该 benchmark 测试模型是否能够准确判断给定文本是否包含幻觉信息。

**幻觉定义**：模型生成的内容与提供的知识库不一致，或者包含无法从知识库中推断出的信息。

该 benchmark 包含三个子任务：
1. **对话样本（dialogue_samples）**：评估对话回复中的幻觉
2. **问答样本（qa_samples）**：评估问答答案中的幻觉
3. **摘要样本（summarization_samples）**：评估摘要中的幻觉

## 数据集样例

数据集位于 `datasets/llm/halueval/` 目录下，**文件格式为 JSONL（每行一个 JSON 对象）**，包含三个子集文件：

### 1. 问答样本（qa_samples.jsonl）

```jsonl
{"knowledge": "新奥尔良泄洪运河大约长3.6英里。奥古斯塔运河大约长7英里。", "question": "新奥尔良泄洪运河与奥古斯塔运河的长度相同吗？", "answer": "不，新奥尔良泄洪运河长3.6英里，而奥古斯塔运河长7英里。", "hallucination": "NO"}
{"knowledge": "新奥尔良泄洪运河大约长3.6英里。奥古斯塔运河大约长7英里。", "question": "新奥尔良泄洪运河与奥古斯塔运河的长度相同吗？", "answer": "是的，两条运河长度相同。", "hallucination": "YES"}
```

**字段说明：**
- `knowledge`（必选）：提供的知识库内容
- `question`（必选）：需要回答的问题
- `answer`（必选）：需要判断是否包含幻觉的答案文本
- `hallucination`（必选）：标注结果，"YES" 表示包含幻觉，"NO" 表示不包含幻觉

### 2. 对话样本（dialogue_samples.jsonl）

```jsonl
{"knowledge": "克里斯托弗·诺兰执导了《黑暗骑士》。", "dialogue_history": "[用户]: 《黑暗骑士》的导演是谁？", "response": "克里斯托弗·诺兰执导了《黑暗骑士》。", "hallucination": "NO"}
{"knowledge": "克里斯托弗·诺兰执导了《黑暗骑士》。", "dialogue_history": "[用户]: 《黑暗骑士》的导演是谁？", "response": "史蒂文·斯皮尔伯格执导了《黑暗骑士》。", "hallucination": "YES"}
```

**字段说明：**
- `knowledge`（必选）：提供的知识库内容
- `dialogue_history`（必选）：对话历史记录
- `response`（必选）：需要判断是否包含幻觉的模型回复
- `hallucination`（必选）：标注结果，"YES" 表示包含幻觉，"NO" 表示不包含幻觉

### 3. 摘要样本（summarization_samples.jsonl）

```jsonl
{"document": "周一，一名遛狗者在马尔公园的树林区域发现了一只豹变色龙。X光检查显示它的所有腿都断了，脊柱畸形，因此不得不被安乐死。", "summary": "在马尔公园发现的一只变色龙因严重受伤而被安乐死。", "hallucination": "NO"}
{"document": "周一，一名遛狗者在马尔公园的树林区域发现了一只豹变色龙。X光检查显示它的所有腿都断了，脊柱畸形，因此不得不被安乐死。", "summary": "在公园发现的一只变色龙在被遗弃后被安乐死。", "hallucination": "YES"}
```

**字段说明：**
- `document`（必选）：原始文档内容
- `summary`（必选）：需要判断是否包含幻觉的摘要文本
- `hallucination`（必选）：标注结果，"YES" 表示包含幻觉，"NO" 表示不包含幻觉

## 启动命令

```bash
python benchmarks/halu_eval/main.py --model <model_name>
```

### 参数说明

- `--model`: 模型名称（必选）
  - 可选值：`deepseek-chat`, `deepseek-reasoner`, `Qwen/Qwen3-Next-80B-A3B-Instruct-FP8`
- `--dataset`: 数据集名称（默认：`halu_eval`）
- `--batch_size`: 批量大小（默认：1）
- `--max_tokens`: 最大token数（默认：2048）
- `--limit`: 样本限制数量（可选）

### 示例

```bash
# 使用 DeepSeek Chat 模型
python benchmarks/halu_eval/main.py --model deepseek-chat

# 使用 Qwen3 模型，限制50个样本
python benchmarks/halu_eval/main.py --model Qwen/Qwen3-Next-80B-A3B-Instruct-FP8 --limit 50
```

## 评价指标样例

评测结果会生成在 `results/halu_eval/<model_name>_<params>/reports/` 目录下，示例结果：

```json
{
  "name": "deepseek-chat@halu_eval",
  "dataset_name": "halu_eval",
  "model_name": "deepseek-chat",
  "score": 0.9167,
  "metrics": [
    {
      "name": "accuracy",
      "num": 12,
      "score": 0.9167,
      "subsets": [
        {
          "name": "dialogue_samples",
          "score": 1.0,
          "num": 4
        },
        {
          "name": "qa_samples",
          "score": 1.0,
          "num": 4
        },
        {
          "name": "summarization_samples",
          "score": 0.75,
          "num": 4
        }
      ]
    },
    {
      "name": "precision",
      "num": 12,
      "score": 0.8889
    },
    {
      "name": "recall",
      "num": 12,
      "score": 0.8571
    },
    {
      "name": "f1_score",
      "num": 12,
      "score": 0.8727
    },
    {
      "name": "yes_ratio",
      "num": 12,
      "score": 0.3333
    }
  ]
}
```

## 评价指标说明

### accuracy (准确率)
- **定义**：正确判断的样本数占总样本数的比例
- **公式**：`accuracy = (TP + TN) / (TP + TN + FP + FN)`
- **范围**：0-1，值越高表示模型判断越准确
- **说明**：综合衡量模型识别幻觉的整体能力

### precision (精确率)
- **定义**：在所有被判断为包含幻觉的样本中，真正包含幻觉的比例
- **公式**：`precision = TP / (TP + FP)`
- **范围**：0-1，值越高表示误报越少
- **说明**：衡量模型判断"包含幻觉"的准确性，避免将正常内容误判为幻觉

### recall (召回率)
- **定义**：在所有真正包含幻觉的样本中，被正确识别出的比例
- **公式**：`recall = TP / (TP + FN)`
- **范围**：0-1，值越高表示漏报越少
- **说明**：衡量模型发现幻觉的能力，避免遗漏真正的幻觉

### f1_score (F1分数)
- **定义**：精确率和召回率的调和平均数
- **公式**：`f1_score = 2 * (precision * recall) / (precision + recall)`
- **范围**：0-1，值越高表示模型在精确率和召回率之间平衡得越好
- **说明**：综合衡量模型性能的单一指标

### yes_ratio (肯定比例)
- **定义**：模型判断为"包含幻觉"（YES）的样本占总样本的比例
- **公式**：`yes_ratio = (TP + FP) / total`
- **范围**：0-1
- **说明**：反映模型的判断倾向，可用于分析模型的保守性或激进性

### 混淆矩阵说明

- **TP (True Positive)**：正确识别为包含幻觉
- **FP (False Positive)**：错误地将正常内容判断为包含幻觉
- **TN (True Negative)**：正确识别为不包含幻觉
- **FN (False Negative)**：错误地将幻觉内容判断为正常

## 注意事项

1. 数据集文件应放在 `datasets/llm/halueval/` 目录下，包含三个子集文件
2. 模型需要输出 "YES" 或 "NO" 来判断是否包含幻觉
3. 评价时会自动将模型输出转换为大写进行比较
4. 不同子任务（对话、问答、摘要）的难度可能不同，建议分别查看各子任务的指标
5. 建议使用 `--limit` 参数在开发阶段限制样本数量以加快测试速度
6. 该 benchmark 需要模型具备较强的推理和对比能力，以准确判断文本与知识库的一致性

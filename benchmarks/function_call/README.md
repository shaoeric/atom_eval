# Function Call Benchmark

## 任务描述

Function Call (函数调用) benchmark 用于评估大语言模型在函数调用任务上的表现。该任务测试模型是否能够：
1. 正确判断是否需要调用函数
2. 正确选择要调用的函数
3. 正确生成函数调用的参数

## 数据集样例

数据集位于 `datasets/llm/function_call/` 目录下，**文件格式为 JSONL（每行一个 JSON 对象）**。

### 数据格式示例

```jsonl
{"messages":[{"role":"system","content":"你是助手"},{"role":"user","content":"请把 2 和 3 相加"}],"tools":[{"type":"function","function":{"name":"add","description":"将两个数字相加","parameters":{"type":"object","properties":{"a":{"type":"number","description":"第一个数字"},"b":{"type":"number","description":"第二个数字"}},"required":["a","b"],"additionalProperties":false}}}],"should_call_tool":true}
{"messages":[{"role":"system","content":"你是助手"},{"role":"user","content":"今天天气不错，我们聊聊天"}],"tools":[{"type":"function","function":{"name":"add","description":"将两个数字相加","parameters":{"type":"object","properties":{"a":{"type":"number","description":"第一个数字"},"b":{"type":"number","description":"第二个数字"}},"required":["a","b"],"additionalProperties":false}}}],"should_call_tool":false}
```

### 字段说明

- `messages`（必选）：对话消息列表，每个消息包含：
  - `role`: 角色（"system" 或 "user"）
  - `content`: 消息内容
- `tools`（必选）：可用的工具/函数列表，每个工具包含：
  - `type`: 工具类型，固定为 "function"
  - `function`: 函数定义，包含：
    - `name`: 函数名称
    - `description`: 函数功能描述
    - `parameters`: 函数参数定义（JSON Schema 格式）
      - `type`: 参数类型，通常为 "object"
      - `properties`: 参数字典，每个参数包含类型和描述
      - `required`: 必需参数列表
- `should_call_tool`（必选）：布尔值，表示是否应该调用工具
  - `true`: 应该调用工具
  - `false`: 不应该调用工具（仅需文本回复）

## 启动命令

```bash
python benchmarks/function_call/main.py --model <model_name>
```

### 参数说明

- `--model`: 模型名称（必选）
  - 可选值：`deepseek-chat`, `deepseek-reasoner`, `Qwen/Qwen3-Next-80B-A3B-Instruct-FP8`
- `--dataset`: 数据集名称（默认：`general_fc`）
- `--batch_size`: 批量大小（默认：1）
- `--max_tokens`: 最大token数（默认：2048）
- `--limit`: 样本限制数量（可选）

### 示例

```bash
# 使用 DeepSeek Chat 模型
python benchmarks/function_call/main.py --model deepseek-chat

# 使用 Qwen3 模型，限制50个样本
python benchmarks/function_call/main.py --model Qwen/Qwen3-Next-80B-A3B-Instruct-FP8 --limit 50
```

## 评价指标样例

评测结果会生成在 `results/general_fc/<model_name>_<params>/reports/` 目录下，示例结果：

```json
{
  "name": "deepseek-chat@general_fc",
  "dataset_name": "general_fc",
  "model_name": "deepseek-chat",
  "score": 2.0,
  "metrics": [
    {
      "name": "count_finish_reason_tool_call",
      "num": 3,
      "score": 2.0
    },
    {
      "name": "count_successful_tool_call",
      "num": 3,
      "score": 2.0
    }
  ]
}
```

## 评价指标说明

### count_finish_reason_tool_call
- **定义**：统计模型正确判断需要调用工具的次数（即 `finish_reason` 为 `tool_calls` 的情况）
- **说明**：衡量模型是否能够正确识别需要调用工具的场景
- **计算方式**：统计 `should_call_tool=true` 且模型实际调用了工具的数量

### count_successful_tool_call
- **定义**：统计成功调用工具的次数（包括正确选择函数和正确生成参数）
- **说明**：衡量模型函数调用的整体成功率
- **计算方式**：统计函数调用成功且参数正确的样本数量

### 其他指标
根据 EvalScope 的默认配置，还可能包含：
- **工具调用准确率**：正确调用工具的比例
- **参数匹配度**：函数参数与期望参数的匹配程度

## 注意事项

1. 数据集文件应放在 `datasets/llm/function_call/` 目录下，文件格式为 JSONL（每行一个JSON对象）
2. 工具参数必须符合 JSON Schema 格式规范
3. 模型需要支持函数调用功能（tool calling）
4. `should_call_tool` 字段用于判断模型是否应该调用工具，这是评估的关键指标
5. 建议在开发阶段使用 `--limit` 参数限制样本数量以加快测试速度

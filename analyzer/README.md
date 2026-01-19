# 需求分析器 (Requirement Analyzer)

基于 AgentScope 和 DeepSeek API 的智能需求分析系统，用于将用户需求转换为适合的 benchmark 评测配置，并自动执行评测和生成对比报告。

## 功能特性

- **智能需求分析**: 使用 AgentScope 框架和 DeepSeek API 分析用户需求，自动提取关键能力标签
- **Benchmark 自动推荐**: 根据需求分析结果，自动推荐最合适的 benchmark 并生成选择理由
- **多模型批量评测**: 支持同时评测多个候选模型，自动生成所有 model 和 benchmark 的组合配置
- **自动执行评测**: 自动执行所有评测任务，无需手动干预
- **智能评估总结**: 使用 ReAct Agent 自动生成模型对比报告，包括能力总结、对比分析和评分排序
- **Markdown 报告**: 自动生成 Markdown 格式的对比报告，包含模型评分、优势劣势分析和推荐理由

## 使用方法

### 基本用法

```bash
# 分析需求并自动执行评测（使用默认模型）
python analyzer/main.py --requirement "我需要评估模型在长文本推理和RAG方面的能力"

# 指定多个模型进行评测
python analyzer/main.py --requirement "评估模型的工具调用能力" --models deepseek-chat deepseek-reasoner

# 使用 LLM judge 进行评估
python analyzer/main.py --requirement "评估模型幻觉检测能力" --models deepseek-chat --use_llm_judge --judge_model_name deepseek-reasoner
```

### 命令行参数

- `--requirement`: (必需) 用户需求描述
- `--models`: 要评测的模型名称列表（可以指定多个，默认：["Qwen/Qwen3-Next-80B-A3B-Instruct-FP8"]）
- `--batch_size`: 批量大小（默认：1）
- `--max_tokens`: 最大 token 数（默认：2048）
- `--limit`: 样本限制数量
- `--use_llm_judge`: 是否使用 LLM judge 进行评估
- `--judge_model_name`: LLM judge 模型名称
- `--work_dir`: 工作目录（默认：自动生成时间戳目录 `results/YYYYMMDD_HHMMSS`）
- `--output`: 输出 JSON 配置文件路径（默认：`work_dir/config.json`）

## 工作流程

1. **需求分析**: 使用 ReAct Agent 分析用户需求，提取能力标签并推荐合适的 benchmark
2. **配置生成**: 为所有 model 和 benchmark 的组合生成评测配置
3. **执行评测**: 自动执行所有评测任务
4. **生成总结**: 使用 ReAct Agent 分析评测结果，生成模型对比报告

## 输出格式

### 配置文件 (config.json)

系统会输出 JSON 格式的配置文件，包含：

```json
{
  "requirement": "用户原始需求",
  "analyzed_capabilities": ["REASONING", "LONG_CONTEXT"],
  "analyzed_description": "需求描述",
  "key_points": ["关键点1", "关键点2"],
  "recommended_benchmarks": [
    {
      "benchmark_name": "FRAMES",
      "pretty_name": "FRAMES",
      "match_score": 1.0,
      "reason": "该需求涉及推理能力、长上下文处理能力，而 FRAMES 专门评测这些能力...",
      "capabilities_covered": ["REASONING", "LONG_CONTEXT"],
      "source": "requirement_agent"
    }
  ],
  "evaluation_configs": [
    {
      "model": "deepseek-chat",
      "benchmark": "FRAMES",
      "config": {...}
    },
    {
      "model": "deepseek-chat",
      "benchmark": "text2sql",
      "config": {...}
    }
  ],
  "model_names": ["deepseek-chat"]
}
```

### 评估总结报告 (report.md)

评测完成后，系统会自动生成 Markdown 格式的对比报告，包含：

- **模型评分排序**: 根据用户需求对模型进行综合评分和排序
- **按 Benchmark 的能力总结**: 每个 benchmark 上各模型的表现总结
- **模型对比分析**: 不同模型在各 benchmark 上的对比
- **整体总结和建议**: 针对用户需求的推荐建议

## 支持的 Benchmark

- **FRAMES**: 长文本推理和 RAG 能力评测
- **text2sql**: 代码生成和 SQL 转换能力评测
- **halu_eval**: 幻觉检测和事实准确性评测
- **general_qa**: 通用知识问答能力评测
- **general_fc**: 函数调用能力评测

## 环境配置

确保在 `.env` 文件中配置了 DeepSeek API key：

```
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_URL=https://api.deepseek.com
DEEPSEEK_CHAT=deepseek-chat
```

## 依赖

- AgentScope
- evalscope
- Python 3.10+

## 输出文件结构

评测完成后，工作目录结构如下：

```
results/YYYYMMDD_HHMMSS/
├── config.json                    # 配置文件
├── report.md                       # 评估总结报告（Markdown）
├── {benchmark1}/
│   ├── {model1}_{params}/
│   │   ├── reports/               # 评测报告
│   │   └── reviews/               # 详细评测结果
│   └── {model2}_{params}/
│       └── ...
└── {benchmark2}/
    └── ...
```

## 架构

- `requirement_agent.py`: 使用 AgentScope ReAct Agent 分析用户需求，推荐 benchmark
- `summary_agent.py`: 使用 AgentScope ReAct Agent 生成模型对比总结报告
- `benchmark_registry.py`: Benchmark 元数据注册表
- `config_generator.py`: 评测配置生成器
- `main.py`: 主入口程序，协调整个流程

## 技术细节

- **需求分析**: 使用 ReAct Agent 和结构化输出（Pydantic BaseModel）确保输出格式规范
- **Benchmark 推荐**: Agent 直接从 benchmarks 目录中选择，并生成详细的选择理由
- **评估总结**: Agent 读取所有评测报告，进行综合分析并生成 Markdown 报告
- **工具支持**: Summary Agent 可以使用文件读写工具直接生成报告文件


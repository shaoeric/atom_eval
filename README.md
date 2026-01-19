# Atom Eval

基于 [EvalScope](https://github.com/modelscope/evalscope) 的 LLM 评估框架，支持多种任务和模型的自动化评估。

## 项目介绍

Atom Eval 是一个灵活、可扩展的大语言模型（LLM）评估框架，旨在帮助研究者和开发者快速构建和运行自定义的评估任务。项目基于 EvalScope 构建，提供了完整的评估流程，包括数据加载、模型调用、结果评估和报告生成。

### 核心特性

- 🎯 **多任务支持**：内置多种评估任务，支持快速扩展
- 🤖 **多模型支持**：支持 DeepSeek、Qwen 等多个主流 LLM 模型
- 📊 **灵活配置**：通过环境变量和配置文件轻松管理模型和数据集
- 📈 **详细报告**：自动生成评估结果、日志和可视化报告
- 🔧 **易于扩展**：清晰的代码结构，便于添加新的评估任务和模型
- 🤖 **智能需求分析**：基于 AgentScope 的智能需求分析系统，自动推荐合适的 benchmark 并生成对比报告

## 为什么需要自定义 Benchmark 评测？

### 1. 领域特定需求

通用评估数据集（如 MMLU、HellaSwag 等）虽然覆盖面广，但往往无法满足特定领域的评估需求。例如：
- **业务场景**：需要评估模型在特定业务逻辑下的表现
- **行业标准**：需要符合特定行业的标准和规范
- **本地化需求**：需要评估模型在特定语言、文化背景下的表现

### 2. 数据隐私和安全

使用自定义 benchmark 可以：
- 避免将敏感数据上传到公共平台
- 在本地环境中进行完整的评估流程
- 控制数据的访问和使用权限

### 3. 评估指标定制

自定义 benchmark 允许：
- 定义符合业务需求的评估指标
- 实现领域特定的评估逻辑
- 灵活调整评估标准和权重

### 4. 持续改进和迭代

自定义 benchmark 支持：
- 根据模型表现持续优化评估任务
- 快速添加新的测试用例
- 跟踪模型在不同版本间的性能变化

## 依赖安装

### 环境要求

- Python >= 3.8
- pip

### 安装步骤

1. 克隆项目：

```bash
git clone https://github.com/shaoeric/atom_eval.git
cd atom_eval
```

2. 安装依赖：

```bash
pip install -r requirement.txt
```

### 主要依赖

- `evalscope==1.4.1`: 评估框架核心库
- `openai==2.15.0`: OpenAI API 兼容接口
- `python-dotenv==1.2.1`: 环境变量管理
- `datasets==3.6.0`: 数据集处理
- `pandas==2.3.3`: 数据处理
- `numpy==2.4.1`: 数值计算
- `agentscope`: AgentScope 框架（用于智能需求分析）
- `pydantic`: 数据验证和结构化输出

完整依赖列表请参考 `requirement.txt`。

## 支持的任务

Atom Eval 目前支持以下评估任务，每个任务都有详细的 README 文档：

### 1. General QA（通用问答）

评估大语言模型在问答任务上的表现，支持多种问答格式。

- **任务描述**：测试模型回答问题的能力
- **评估指标**：BLEU-1/2/3、ROUGE 系列
- **详细文档**：[benchmarks/general_qa/README.md](benchmarks/general_qa/README.md)

### 2. Text2SQL（文本转SQL）

评估模型将自然语言问题转换为 SQL 查询语句的能力。

- **任务描述**：测试模型理解自然语言问题、数据库结构和生成 SQL 的能力
- **评估指标**：SQL AST 相似度（sql_ast_sim）
- **详细文档**：[benchmarks/text2sql/README.md](benchmarks/text2sql/README.md)

### 3. Function Call（函数调用）

评估模型在函数调用任务上的表现。

- **任务描述**：测试模型判断是否需要调用函数、选择正确函数和生成参数的能力
- **评估指标**：工具调用准确率、成功调用次数
- **详细文档**：[benchmarks/function_call/README.md](benchmarks/function_call/README.md)

### 4. HaluEval（幻觉检测）

评估模型识别幻觉（Hallucination）的能力。

- **任务描述**：测试模型判断文本是否包含与知识库不一致信息的能力
- **评估指标**：准确率（accuracy）、精确率（precision）、召回率（recall）、F1 分数、肯定比例（yes_ratio）
- **子任务**：对话样本、问答样本、摘要样本
- **详细文档**：[benchmarks/halu_eval/README.md](benchmarks/halu_eval/README.md)

### 5. FRAMES（RAG 系统评估）

评估检索增强生成（RAG）系统的综合能力。

- **任务描述**：测试 RAG 系统在事实性、检索准确性和推理能力方面的表现
- **评估指标**：准确率（acc），支持标准评估和 LLM Judge 评估
- **详细文档**：[benchmarks/frames/README.md](benchmarks/frames/README.md)

## 智能需求分析系统 (Analyzer)

Atom Eval 提供了基于 AgentScope 的智能需求分析系统，可以根据用户需求自动推荐合适的 benchmark，并执行多模型对比评测。

### 主要功能

- **智能需求分析**：使用 ReAct Agent 分析用户需求，自动提取关键能力标签
- **Benchmark 自动推荐**：根据需求分析结果，自动推荐最合适的 benchmark 并生成选择理由
- **多模型批量评测**：支持同时评测多个候选模型，自动生成所有 model 和 benchmark 的组合配置
- **自动执行评测**：自动执行所有评测任务，无需手动干预
- **智能评估总结**：使用 ReAct Agent 自动生成模型对比报告，包括能力总结、对比分析和评分排序


### 输出结果

评测完成后，系统会在工作目录生成：
- `config.json`: 配置文件，包含需求分析结果和评测配置
- `report.md`: Markdown 格式的模型对比报告，包含评分排序、能力总结和推荐建议
- 各 benchmark 的详细评测结果

详细文档请参考：[analyzer/README.md](analyzer/README.md)

## 自定义模型配置

Atom Eval 支持添加自定义模型进行评估。详细配置说明请参考：

📖 [自定义模型配置文档](docs/custom_model.md)


## 自定义 Benchmark 配置

Atom Eval 支持创建自定义评估任务（Benchmark）。详细配置说明请参考：

📖 [自定义 Benchmark 配置文档](docs/custom_benchmark.md)


## 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirement.txt

# 配置环境变量
cp .env_example .env
# 编辑 .env 文件，填写 API 密钥等信息
```

### 2. 运行评估

#### 方式一：使用智能需求分析系统（推荐）

```bash
# 分析需求并自动执行评测
python analyzer/main.py --requirement "我需要评估模型在长文本推理和RAG方面的能力"

# 指定多个模型进行对比评测
python analyzer/main.py --requirement "评估模型的代码生成能力" --models deepseek-chat deepseek-reasoner
```

#### 方式二：直接运行单个 Benchmark

```bash
# 运行 General QA 评估
python benchmarks/general_qa/main.py --model deepseek-chat

# 运行 Text2SQL 评估
python benchmarks/text2sql/main.py --model Qwen/Qwen3-Next-80B-A3B-Instruct-FP8

# 运行 Function Call 评估
python benchmarks/function_call/main.py --model deepseek-chat

# 运行 HaluEval 评估
python benchmarks/halu_eval/main.py --model deepseek-chat

# 运行 FRAMES 评估（使用 LLM Judge）
python benchmarks/frames/main.py --model deepseek-chat --use_llm_judge --judge_model_name deepseek-reasoner
```

### 3. 命令行参数

所有 benchmark 支持以下参数：

- `--model`: 模型名称（必选，或通过环境变量 `USE_LLM_NAME` 设置）
- `--dataset`: 数据集名称（默认与 benchmark 名称相同）
- `--batch_size`: 批量大小（默认：1）
- `--max_tokens`: 最大 token 数（默认：2048）
- `--limit`: 限制评估样本数量（可选）
- `--use_llm_judge`: 是否使用 LLM Judge 评估（部分 benchmark 支持）
- `--judge_model_name`: LLM Judge 模型名称（使用 `--use_llm_judge` 时必选）

示例：

```bash
# 限制评估前 10 个样本
python benchmarks/text2sql/main.py --model deepseek-chat --limit 10

# 自定义批量大小和最大 token 数
python benchmarks/text2sql/main.py --model deepseek-chat --batch_size 4 --max_tokens 4096
```

## 项目结构

```
atom_eval/
├── analyzer/             # 智能需求分析系统
│   ├── requirement_agent.py  # 需求分析 Agent
│   ├── summary_agent.py     # 评估总结 Agent
│   ├── benchmark_registry.py # Benchmark 元数据注册表
│   ├── config_generator.py   # 配置生成器
│   ├── matcher.py            # 需求匹配引擎
│   └── main.py               # 主入口程序
├── benchmarks/              # 评估任务实现
│   ├── general_qa/         # 通用问答任务
│   ├── text2sql/          # Text2SQL 任务
│   ├── function_call/     # 函数调用任务
│   ├── halu_eval/         # 幻觉检测任务
│   └── frames/            # FRAMES RAG 评估任务
├── datasets/              # 数据集目录
│   └── llm/              # LLM 数据集
│       ├── qa/          # 问答数据集
│       ├── text2sql/     # Text2SQL 数据集
│       ├── function_call/ # 函数调用数据集
│       ├── halueval/     # HaluEval 数据集
│       └── frames/       # FRAMES 数据集
├── results/              # 评估结果输出目录
│   └── {timestamp}/      # 时间戳目录（analyzer 生成）
│       ├── config.json   # 配置文件
│       ├── report.md      # 评估总结报告
│       └── {benchmark_name}/ # 各任务的评估结果
│           └── {model_name}_{params}/
│               ├── reviews/  # 详细评估结果
│               └── reports/  # 评估报告
├── docs/                 # 文档目录
│   ├── custom_model.md  # 自定义模型配置文档
│   └── custom_benchmark.md # 自定义 Benchmark 配置文档
├── config.py             # 配置文件
├── utils.py              # 工具函数
├── requirement.txt       # Python 依赖
└── .env_example         # 环境变量示例
```

## 评估结果

### 单个 Benchmark 评估结果

评估结果保存在 `results/{benchmark_name}/{model_name}_{params}/` 目录下，包括：

- `reviews/`: 每个样本的详细评估结果（JSONL 格式）
- `reports/`: 汇总评估报告（JSON 格式）
- `logs/`: 评估日志文件

### Analyzer 生成的评估结果

使用 analyzer 进行评测时，结果保存在 `results/{timestamp}/` 目录下，包括：

- `config.json`: 配置文件，包含需求分析结果、推荐的 benchmark 和所有评测配置
- `report.md`: Markdown 格式的模型对比报告，包含：
  - 模型评分排序表
  - 按 Benchmark 的能力总结
  - 模型对比分析
  - 整体总结和建议
- `{benchmark_name}/{model_name}_{params}/`: 各 benchmark 和 model 的详细评测结果

## 更新日志

详细的版本更新和变更记录请查看：

📋 [RELEASE_NOTES.md](RELEASE_NOTES.md)

## 许可证

请查看项目根目录的 LICENSE 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关链接

- [EvalScope](https://github.com/modelscope/evalscope): 底层评估框架
- [ModelScope](https://www.modelscope.cn/): 模型和数据集平台

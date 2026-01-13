# Atom Eval

基于 [EvalScope](https://github.com/modelscope/evalscope) 的 LLM 评估框架，支持多种任务和模型的自动化评估。

## 功能特性

- 🎯 **多任务支持**：支持 Text2SQL、通用问答等多种评估任务
- 🤖 **多模型支持**：支持 DeepSeek、Qwen 等多个主流 LLM 模型
- 📊 **灵活配置**：通过环境变量和配置文件轻松管理模型和数据集
- 📈 **详细报告**：自动生成评估结果和日志

## 支持的评估任务

### 1. Text2SQL
将自然语言问题转换为 SQL 查询语句，使用 SQL AST 相似度进行评估。

### 2. General QA
通用问答任务，使用 BLEU 和 Rouge 指标进行评估。

## 支持的模型

- **DeepSeek Chat** (`deepseek-chat`)
- **DeepSeek Reasoner** (`deepseek-reasoner`)
- **Qwen3-Next-80B** (`Qwen/Qwen3-Next-80B-A3B-Instruct-FP8`)

## 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirement.txt
```

### 2. 配置环境变量

复制 `.env_example` 为 `.env` 并填写相应的配置：

```bash
cp .env_example .env
```

编辑 `.env` 文件，配置模型 API 信息：

```bash
# DeepSeek 配置
DEEPSEEK_CHAT=deepseek-chat
DEEPSEEK_REASONER=deepseek-reasoner
DEEPSEEK_URL=https://api.deepseek.com
DEEPSEEK_API_KEY=your_deepseek_api_key

# Qwen3 配置
QWEN3_80B=Qwen/Qwen3-Next-80B-A3B-Instruct-FP8
QWEN3_80B_URL=http://localhost:5004/v1
QWEN3_80B_API_KEY=EMPTY
```

### 3. 运行评估

#### Text2SQL 任务

```bash
python benchmarks/text2sql/main.py --model Qwen/Qwen3-Next-80B-A3B-Instruct-FP8
```

#### General QA 任务

```bash
python benchmarks/general_qa/main.py --model deepseek-chat
```

### 4. 命令行参数

所有 benchmark 支持以下参数：

- `--model`: 模型名称（必选，或通过环境变量 `USE_LLM_NAME` 设置）
  - 可选值：`deepseek-chat`, `deepseek-reasoner`, `Qwen/Qwen3-Next-80B-A3B-Instruct-FP8`
- `--dataset`: 数据集名称（默认与 benchmark 名称相同）
- `--batch_size`: 批量大小（默认：1）
- `--max_tokens`: 最大 token 数（默认：2048）
- `--limit`: 限制评估样本数量（可选）

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
├── benchmarks/          # 评估任务实现
│   ├── text2sql/       # Text2SQL 任务
│   └── general_qa/      # 通用问答任务
├── datasets/           # 数据集目录
│   └── llm/           # LLM 数据集
│       ├── text2sql/  # Text2SQL 数据集
│       └── qa/        # 问答数据集
├── results/           # 评估结果输出目录
├── config.py          # 配置文件
├── utils.py           # 工具函数
├── requirement.txt    # Python 依赖
└── .env_example       # 环境变量示例
```

## 评估结果

评估结果保存在 `results/{benchmark_name}/{model_name}_{params}/` 目录下，包括：

- `eval_log.log`: 评估日志
- 其他评估报告文件

## 配置说明

### 模型配置

在 `config.py` 中的 `LLM_SERVER_CONFIG` 配置模型信息：

```python
LLM_SERVER_CONFIG = {
    'model_name': {
        'model': '模型名称',
        'url': 'API 地址',
        'api_key': 'API 密钥（从环境变量读取）',
        'params': '参数量标识'
    }
}
```

### 数据集配置

在 `config.py` 中的 `LLM_DATASET_CONFIG` 配置数据集信息：

```python
LLM_DATASET_CONFIG = {
    "benchmark_name": {
        "local_path": "数据集本地路径",
        "subset_list": ["子集列表"]
    }
}
```

## 添加新的评估任务

1. 在 `benchmarks/` 目录下创建新的任务目录
2. 实现对应的 adapter（参考 `benchmarks/text2sql/text2sql_adapter.py`）
3. 在 `config.py` 中添加数据集配置
4. 创建 `main.py` 入口文件（参考现有实现）

## 添加新的模型

1. 在 `.env` 文件中添加模型相关的环境变量
2. 在 `config.py` 的 `LLM_SERVER_CONFIG` 中添加模型配置

## 依赖说明

主要依赖：

- `evalscope`: 评估框架核心库
- `openai`: OpenAI API 兼容接口
- `python-dotenv`: 环境变量管理
- `datasets`: 数据集处理

完整依赖列表请参考 `requirement.txt`。

## 许可证

请查看项目根目录的 LICENSE 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！

# 更新日志

本文档记录了 Atom Eval 的所有版本更新和变更。

## [v1.0.0]

### 新增功能

- **内置 Benchmark**
  - 添加了 5 个内置 benchmark：General QA、Text2SQL、Function Call、HaluEval、FRAMES
  - 每个 benchmark 都有详细的 README 文档，包含任务描述、数据集样例、启动命令和评价指标说明

- **自定义配置支持**
  - 支持自定义模型配置，可轻松添加新的 LLM 模型
  - 支持自定义 benchmark 配置，可快速创建新的评估任务
  - 提供详细的配置文档和代码示例

- **评估模式**
  - 支持标准评估模式（基于规则匹配）
  - 支持 LLM Judge 评估模式（FRAMES benchmark），使用 LLM 进行更灵活的评估

### 改进

- **文档完善**
  - 完善了各 benchmark 的 README 文档
  - 统一了数据集格式说明（JSONL 格式）
  - 添加了自定义模型和 benchmark 的详细配置文档

- **代码优化**
  - 优化了评估结果输出格式
  - 改进了错误处理和日志记录
  - 统一了代码风格和项目结构

### 文档

- **主文档**
  - 重写了主 README，包含完整的项目介绍和使用指南
  - 添加了"为什么需要自定义 Benchmark 评测"章节
  - 完善了快速开始指南

- **Benchmark 文档**
  - 为每个 benchmark 添加了详细的 README 文档
  - 包含任务描述、数据集样例、启动命令、评价指标说明

- **配置文档**
  - 创建了 `docs/custom_model.md` - 自定义模型配置指南
  - 创建了 `docs/custom_benchmark.md` - 自定义 Benchmark 配置指南
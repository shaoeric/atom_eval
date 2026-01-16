# Text2SQL Benchmark

## 任务描述

Text2SQL benchmark 用于评估大语言模型将自然语言问题转换为 SQL 查询语句的能力。该任务测试模型是否能够：
1. 理解自然语言问题
2. 理解数据库表结构（Schema）
3. 生成正确的 SQL 查询语句

## 数据集样例

数据集位于 `datasets/llm/text2sql/` 目录下，**文件格式为 JSONL（每行一个 JSON 对象）**。

### 数据格式示例

```jsonl
{"question":"查询所有注册时间在2023年1月1日之后且年龄在25到35岁之间的用户，按注册时间降序排列，只显示前10条。","schema":["CREATE TABLE users (user_id INT PRIMARY KEY, username TEXT, email TEXT, age INT, gender TEXT, registration_date DATE, last_login_date DATE, status TEXT, city TEXT, phone TEXT);"],"ground_truth":"SELECT * FROM users WHERE registration_date > '2023-01-01' AND age BETWEEN 25 AND 35 ORDER BY registration_date DESC LIMIT 10;"}
{"question":"统计每个城市的用户数量，只显示用户数量大于100的城市，按用户数量降序排列。","schema":["CREATE TABLE users (user_id INT PRIMARY KEY, username TEXT, email TEXT, age INT, gender TEXT, registration_date DATE, last_login_date DATE, status TEXT, city TEXT, phone TEXT);"],"ground_truth":"SELECT city, COUNT(*) as user_count FROM users GROUP BY city HAVING COUNT(*) > 100 ORDER BY user_count DESC;"}
```

### 字段说明

- `question`（必选）：自然语言问题（中文），描述需要查询的内容
- `schema`（必选）：数据库表结构定义列表，每个元素是一个 CREATE TABLE 语句字符串，以及数据字段的解释，用于上下文中
- `ground_truth`（必选）：期望生成的 SQL 查询语句，作为标准答案用于评估

## 启动命令

```bash
python benchmarks/text2sql/main.py --model <model_name>
```

### 参数说明

- `--model`: 模型名称（必选）
  - 可选值：`deepseek-chat`, `deepseek-reasoner`, `Qwen/Qwen3-Next-80B-A3B-Instruct-FP8`
- `--dataset`: 数据集名称（默认：`text2sql`）
- `--batch_size`: 批量大小（默认：1）
- `--max_tokens`: 最大token数（默认：2048）
- `--limit`: 样本限制数量（可选）

### 示例

```bash
# 使用 DeepSeek Chat 模型
python benchmarks/text2sql/main.py --model deepseek-chat

# 使用 Qwen3 模型，限制100个样本
python benchmarks/text2sql/main.py --model Qwen/Qwen3-Next-80B-A3B-Instruct-FP8 --limit 100
```

## 评价指标样例

评测结果会生成在 `results/text2sql/<model_name>_<params>/reviews/` 目录下，单个样本的评分示例：

```json
{
  "index": 14,
  "input": "Convert the following question into a SQL query based on the provided schema.\nSchema: CREATE TABLE users (...)\nQuestion: 查询邮箱地址中包含公司域名的用户...\nSQL:",
  "target": "SELECT * FROM users WHERE email LIKE '%company%' OR email LIKE '%corp%' ORDER BY registration_date ASC;",
  "sample_score": {
    "score": {
      "value": {
        "sql_ast_sim": 1.0
      },
      "extracted_prediction": "SELECT * FROM users WHERE email LIKE '%company%' OR email LIKE '%corp%' ORDER BY registration_date ASC",
      "prediction": "```sql\nSELECT *\nFROM users\nWHERE email LIKE '%company%' OR email LIKE '%corp%'\nORDER BY registration_date ASC;\n```"
    }
  }
}
```

整体报告示例：

```json
{
  "name": "deepseek-chat@text2sql",
  "dataset_name": "text2sql",
  "model_name": "deepseek-chat",
  "score": 0.85,
  "metrics": [
    {
      "name": "mean_sql_ast_sim",
      "num": 80,
      "score": 0.85
    }
  ]
}
```

## 评价指标说明

### sql_ast_sim (SQL AST Similarity)
- **定义**：SQL 抽象语法树（AST）相似度，通过比较预测 SQL 和标准答案 SQL 的 AST 结构来计算相似度
- **范围**：0-1，值越高表示生成的 SQL 与标准答案越相似
- **优势**：
  - 不受 SQL 格式（空格、换行、大小写）影响
  - 关注 SQL 的逻辑结构而非表面形式
  - 能够识别语义等价但写法不同的 SQL
- **计算方式**：
  1. 将预测 SQL 和标准答案 SQL 解析为 AST
  2. 比较两个 AST 的结构相似度
  3. 返回 0-1 之间的相似度分数

### 指标特点

- **AST 相似度 vs 字符串匹配**：
  - 字符串匹配：`SELECT * FROM users` 和 `select * from users` 会被视为不同
  - AST 相似度：两者会被识别为相同，因为 AST 结构一致

- **语义等价识别**：
  - `COUNT(*)` 和 `COUNT(user_id)` 在某些情况下可能等价
  - AST 相似度能够更好地处理这类情况

## 注意事项

1. 数据集文件应放在 `datasets/llm/text2sql/` 目录下，文件格式为 JSONL（每行一个JSON对象）
2. Schema 可以是字符串或字符串列表，系统会自动处理
3. 模型生成的 SQL 会被自动提取（支持代码块格式和纯文本格式）
4. 评价指标基于 AST 相似度，对于逻辑正确但写法不同的 SQL 会有更好的容错性
5. 建议使用 `--limit` 参数在开发阶段限制样本数量以加快测试速度
6. 生成的 SQL 会自动去除尾部分号和换行符，以便更好地进行 AST 比较

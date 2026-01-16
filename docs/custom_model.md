# 自定义模型配置

本文档介绍如何在 Atom Eval 中添加和配置自定义模型。

## 1. 配置环境变量

复制 `.env_example` 为 `.env` 并填写相应的配置：

```bash
cp .env_example .env
```

编辑 `.env` 文件，添加模型 API 信息：

```bash
# 示例：添加新的模型配置
NEW_MODEL_NAME=your-model-name
NEW_MODEL_URL=https://api.example.com/v1
NEW_MODEL_API_KEY=your_api_key_here
```

## 2. 在 config.py 中添加模型配置

编辑 `config.py` 文件，在 `LLM_SERVER_CONFIG` 字典中添加新模型：

```python
LLM_SERVER_CONFIG = {
    # 现有模型配置...
    
    # 添加新模型
    'your-model-name': {
        'model': os.getenv('NEW_MODEL_NAME', 'your-model-name'),
        'url': os.getenv('NEW_MODEL_URL', 'https://api.example.com/v1'),
        'api_key': os.getenv('NEW_MODEL_API_KEY', ''),
        'params': '7B'  # 参数量标识，用于结果目录命名
    }
}
```

## 3. 使用新模型

配置完成后，可以在命令行中使用新模型：

```bash
python benchmarks/general_qa/main.py --model your-model-name
```

## 配置说明

### 字段说明

- `model`: 模型名称，用于 API 调用
- `url`: API 服务地址，需要兼容 OpenAI API 格式
- `api_key`: API 密钥，建议通过环境变量设置
- `params`: 参数量标识（如 "7B", "13B", "671B"），用于结果目录命名

### API 兼容性要求

自定义模型需要提供兼容 OpenAI API 格式的接口，包括：

- **端点**: `/v1/chat/completions`
- **请求格式**: 符合 OpenAI Chat Completions API 规范
- **响应格式**: 符合 OpenAI API 响应格式

### 示例：添加本地部署的模型

```python
# .env 文件
LOCAL_MODEL_NAME=local-llama3
LOCAL_MODEL_URL=http://localhost:8000/v1
LOCAL_MODEL_API_KEY=EMPTY

# config.py
LLM_SERVER_CONFIG = {
    'local-llama3': {
        'model': os.getenv('LOCAL_MODEL_NAME', 'local-llama3'),
        'url': os.getenv('LOCAL_MODEL_URL', 'http://localhost:8000/v1'),
        'api_key': os.getenv('LOCAL_MODEL_API_KEY', ''),
        'params': '8B'
    }
}
```

### 示例：添加云服务模型

```python
# .env 文件
CLOUD_MODEL_NAME=cloud-gpt4
CLOUD_MODEL_URL=https://api.cloud-service.com/v1
CLOUD_MODEL_API_KEY=sk-xxxxxxxxxxxxx

# config.py
LLM_SERVER_CONFIG = {
    'cloud-gpt4': {
        'model': os.getenv('CLOUD_MODEL_NAME', 'cloud-gpt4'),
        'url': os.getenv('CLOUD_MODEL_URL', 'https://api.cloud-service.com/v1'),
        'api_key': os.getenv('CLOUD_MODEL_API_KEY', ''),
        'params': 'GPT4'
    }
}
```

## 验证配置

配置完成后，可以通过运行简单的评估任务来验证模型配置是否正确：

```bash
# 使用新模型运行评估（限制少量样本）
python benchmarks/general_qa/main.py --model your-model-name --limit 1
```

如果配置正确，应该能够成功调用模型并生成评估结果。

## 常见问题

### Q: 模型调用失败怎么办？

A: 检查以下几点：
1. 确认 `.env` 文件中的环境变量已正确设置
2. 确认 `config.py` 中的模型配置与 `.env` 中的变量名一致
3. 确认 API URL 和密钥是否正确
4. 确认 API 服务是否正常运行
5. 查看日志文件 `results/{benchmark_name}/{model_name}_{params}/logs/eval_log.log`

### Q: 如何测试 API 兼容性？

A: 可以使用 curl 命令测试：

```bash
curl -X POST https://api.example.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "model": "your-model-name",
    "messages": [{"role": "user", "content": "Hello"}],
    "temperature": 0.7
  }'
```

### Q: 参数量标识有什么作用？

A: 参数量标识用于：
1. 结果目录命名：`results/{benchmark_name}/{model_name}_{params}/`
2. 区分同一模型的不同参数量版本
3. 便于结果管理和对比

建议使用简洁的标识，如 "7B", "13B", "70B", "671B" 等。

import argparse
import os
import config

def parse_args(benchmark_name):
    parser = argparse.ArgumentParser(description=f"Parse arguments for {benchmark_name}")
    parser.add_argument("--model", type=str, default=None, choices=config.LLM_SERVER_CONFIG.keys(), help="模型名称")
    parser.add_argument("--dataset", type=str, default=benchmark_name, help="数据集名称")
    parser.add_argument("--batch_size", type=int, default=1, help="批量大小")
    parser.add_argument("--max_tokens", type=int, default=2048, help="最大token数")
    parser.add_argument("--limit", type=int, default=None, help="样本限制数量")
    args = parser.parse_args()
    return args


def get_task_config(args: argparse.Namespace):
    if args.model:
        model_name = args.model
    else:
        model_name = os.environ['USE_LLM_NAME']
    model_config = config.LLM_SERVER_CONFIG[model_name]
    params = model_config['params']  # 参数量

    dataset_config = config.LLM_DATASET_CONFIG[args.dataset]

    cleaned_model_name = model_name.replace('/', '-')
    work_dir = os.path.join(config.PROJECT_ROOT, "results", args.dataset, cleaned_model_name + "_" + params)

    task_config = {
        "model": model_config['model'],
        "api_url": model_config['url'],
        "api_key": model_config['api_key'],
        "eval_type": "openai_api",
        "datasets": [args.dataset],
        "limit": args.limit,
        "dataset_args": {
            args.dataset: dataset_config
        },
        "generation_config": {
            "batch_size": args.batch_size,
            "temperature": 0.0,
            "max_tokens": args.max_tokens,
        },
        "work_dir": work_dir,
        "no_timestamp": True,
        "timeout": 600,
    }
    return task_config
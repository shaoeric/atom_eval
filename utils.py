import argparse
import os
import config

def parse_args(benchmark_name):
    parser = argparse.ArgumentParser(description=f"Parse arguments for {benchmark_name}")
    parser.add_argument("--model", type=str, default=os.getenv('USE_LLM_NAME', None), choices=config.LLM_SERVER_CONFIG.keys(), help="模型名称")
    parser.add_argument("--dataset", type=str, default=benchmark_name, help="数据集名称")
    parser.add_argument("--batch_size", type=int, default=1, help="批量大小")
    parser.add_argument("--max_tokens", type=int, default=2048, help="最大token数")
    parser.add_argument("--limit", type=int, default=None, help="样本限制数量")
    parser.add_argument("--use_llm_judge", action="store_true", help="是否使用LLM judge进行评估")
    parser.add_argument("--judge_model_name", type=str, default=os.getenv('USE_JUDGE_LLM_NAME', None), choices=config.LLM_SERVER_CONFIG.keys(), help="LLM judge模型名称")
    args = parser.parse_args()
    return args


def get_task_config(args: argparse.Namespace):
    assert args.model is not None, "模型名称不能为空"
    model_name = args.model
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
    
    # 如果指定了使用LLM judge，添加到dataset_args中
    if args.use_llm_judge:
        assert args.judge_model_name is not None, "LLM judge模型名称不能为空"
        judge_llm_config = config.LLM_SERVER_CONFIG[args.judge_model_name]
        task_config["judge_strategy"] = "auto"
        task_config["judge_model_args"] = {
            "api_key": judge_llm_config['api_key'],
            "api_url": judge_llm_config['url'],
            "model_id": judge_llm_config['model'],
        }
    
    return task_config
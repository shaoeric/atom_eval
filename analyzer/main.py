"""主入口程序，整合所有组件，支持命令行参数和 JSON 输出。"""
import argparse
import json
import os
import sys
import logging
from typing import Dict, Any, List
from datetime import datetime
import glob

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer.requirement_agent import RequirementAnalyzer
from analyzer.config_generator import ConfigGenerator
from analyzer.summary_agent import SummaryAgent
import config
import benchmarks

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

current_time = f'results/{datetime.now().strftime("%Y%m%d_%H%M%S")}'
os.makedirs(current_time, exist_ok=True)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="基于 AgentScope 的需求到 Benchmark 映射系统"
    )
    parser.add_argument(
        "--requirement",
        type=str,
        required=True,
        help="用户需求描述"
    )
    parser.add_argument(
        "--models",
        type=str,
        nargs='+',
        default=["Qwen/Qwen3-Next-80B-A3B-Instruct-FP8"],
        choices=list(config.LLM_SERVER_CONFIG.keys()),
        help="要评测的模型名称列表（可以指定多个）"
    )
    # parser.add_argument(
    #     "--top_k",
    #     type=int,
    #     default=5,
    #     help="返回前 k 个最匹配的 benchmark（默认：5）"
    # )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=1,
        help="批量大小（默认：1）"
    )
    parser.add_argument(
        "--max_tokens",
        type=int,
        default=2048,
        help="最大 token 数（默认：2048）"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="样本限制数量"
    )
    parser.add_argument(
        "--use_llm_judge",
        action="store_true",
        help="是否使用 LLM judge 进行评估"
    )
    parser.add_argument(
        "--judge_model_name",
        type=str,
        default=os.getenv('USE_JUDGE_LLM_NAME', None),
        choices=list(config.LLM_SERVER_CONFIG.keys()) + [None],
        help="LLM judge 模型名称"
    )
    parser.add_argument(
        "--work_dir",
        type=str,
        default=current_time,
        help="工作目录"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=os.path.join(current_time, "config.json"),
        help="输出 JSON 文件路径（如果不指定则输出到标准输出）"
    )
    
    return parser.parse_args()


def analyze_requirement(requirement: str) -> Dict[str, Any]:
    """
    分析用户需求
    
    Args:
        requirement: 用户需求描述
        
    Returns:
        分析结果
    """
    logger.info("开始分析用户需求...")
    analyzer = RequirementAnalyzer()
    result = analyzer.analyze(requirement)
    logger.info(f"需求分析完成，识别出能力标签: {result.get('capabilities', [])}")
    return result


# def match_benchmarks(
#     analyzed_result: Dict[str, Any],
#     top_k: int = 5
# ) -> list:
#     """
#     匹配 benchmark
    
#     Args:
#         analyzed_result: 需求分析结果
#         top_k: 返回前 k 个
        
#     Returns:
#         匹配结果列表
#     """
#     logger.info("开始匹配 benchmark...")
#     matcher = BenchmarkMatcher()
    
#     capabilities = analyzed_result.get("capabilities", [])
#     description = analyzed_result.get("description", "")
    
#     matches = matcher.match(capabilities, description, top_k)
#     logger.info(f"匹配完成，找到 {len(matches)} 个推荐的 benchmark")
    
#     return matches


def generate_config(
    requirement: str,
    analyzed_result: Dict[str, Any],
    recommended_benchmarks: list,
    model_names: list = None,
    args: argparse.Namespace = None
) -> Dict[str, Any]:
    """
    生成完整的分析报告
    
    Args:
        requirement: 原始需求
        analyzed_result: 分析结果
        recommended_benchmarks: 推荐的 benchmark 列表
        model_name: 模型名称
        args: 命令行参数
        
    Returns:
        完整的报告字典
    """
    report = {
        "requirement": requirement,
        "analyzed_capabilities": analyzed_result.get("capabilities", []),
        "analyzed_description": analyzed_result.get("description", ""),
        "key_points": analyzed_result.get("key_points", []),
        "recommended_benchmarks": recommended_benchmarks,
    }
    
    # 如果指定了模型列表，生成评测配置
    if model_names:
        logger.info(f"为模型列表 {model_names} 生成评测配置...")
        config_generator = ConfigGenerator()
        
        # 为每个 model 和每个 benchmark 的组合生成配置
        evaluation_configs = []
        for model_name in model_names:
            for benchmark_info in recommended_benchmarks:
                benchmark_name = benchmark_info["benchmark_name"]
                
                config_dict = config_generator.generate_single_config(
                    benchmark_name=benchmark_name,
                    model_name=model_name,
                    batch_size=args.batch_size if args else 1,
                    max_tokens=args.max_tokens if args else 2048,
                    limit=args.limit if args else None,
                    use_llm_judge=args.use_llm_judge if args else False,
                    judge_model_name=args.judge_model_name if args else None,
                    work_dir=args.work_dir if args else None,
                )
                evaluation_configs.append({
                    "model": model_name,
                    "benchmark": benchmark_name,
                    "config": config_dict
                })
        
        report["evaluation_configs"] = evaluation_configs
        report["model_names"] = model_names
    else:
        report["evaluation_configs"] = []
        report["model_names"] = []
    
    return report


def run_evaluation(config_dict: Dict[str, Any]):
    """
    执行评测
    
    Args:
        config_dict: 评测配置字典
    """

    from evalscope.run import run_task
    
    logger.info("开始执行评测...")
    run_task(config_dict)
    logger.info("评测任务圆满完成。")
    


def main():
    """主函数"""
    args = parse_args()
    
    # 1. 分析需求
    analyzed_result = analyze_requirement(args.requirement)
    
    # 2. 获取推荐的 benchmark（使用 requirement_agent 返回的）
    if "recommended_benchmarks" not in analyzed_result or not analyzed_result["recommended_benchmarks"]:
        raise ValueError("需求分析未返回推荐的 benchmark，请检查需求描述或重试")
    
    # 使用 requirement_agent 直接返回的 benchmark 推荐
    agent_benchmarks = analyzed_result["recommended_benchmarks"]
    recommended_benchmarks = []
    for bench_rec in agent_benchmarks:
        recommended_benchmarks.append({
            "benchmark_name": bench_rec["benchmark"],
            "pretty_name": bench_rec["benchmark"],  # 可以从 registry 获取
            "match_score": 1.0,  # agent 推荐的默认高分
            "reason": bench_rec["reason"],
            "capabilities_covered": analyzed_result.get("capabilities", []),
            "source": "requirement_agent"
        })
    
    if not recommended_benchmarks:
        raise ValueError("没有找到推荐的 benchmark")
    
    
    # 3. 生成报告
    model_names = args.models if args.models else []
    config = generate_config(
        requirement=args.requirement,
        analyzed_result=analyzed_result,
        recommended_benchmarks=recommended_benchmarks,
        model_names=model_names,
        args=args
    )
    
    # 4. 输出报告
    config_json = json.dumps(config, ensure_ascii=False, indent=2)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(config_json)
        logger.info(f"报告已保存到: {args.output}")
    else:
        print(config_json)
    
    # 5. 执行评测（循环执行所有 model 和 benchmark 的组合）
    for config_item in config["evaluation_configs"]:
        model_name = config_item.get("model")
        benchmark_name = config_item.get("benchmark")
        
        config_dict = config_item.get("config")
        
        run_evaluation(config_dict)
        logger.info(f"Model {model_name} 和 Benchmark {benchmark_name} 评测完成")
    
    # 6. 生成评估总结报告
    logger.info("开始生成评估总结报告...")
    evaluation_reports = collect_evaluation_reports(args.work_dir, model_names, recommended_benchmarks)
    
    if evaluation_reports:
        summary_agent = SummaryAgent()
        summary_agent.generate_summary(
            requirement=args.requirement,
            evaluation_reports=evaluation_reports,
            work_dir=args.work_dir
        )
        
       
        # # 生成 Markdown 报告
        # summary_agent.write_markdown_report(
        #     requirement=args.requirement,
        #     summary_data=summary_data,
        #     model_names=model_names,
        #     benchmark_names=[b["benchmark_name"] for b in recommended_benchmarks],
        #     work_dir=args.work_dir
        # )
        
        


def collect_evaluation_reports(
    work_dir: str,
    model_names: List[str],
    recommended_benchmarks: List[Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """
    收集所有评测报告
    
    Args:
        work_dir: 工作目录
        model_names: 模型名称列表
        recommended_benchmarks: 推荐的 benchmark 列表
        
    Returns:
        评测报告字典，格式为 {benchmark_name: {model_name: report_data}}
    """
    evaluation_reports = {}
    
    for benchmark_info in recommended_benchmarks:
        benchmark_name = benchmark_info["benchmark_name"]
        evaluation_reports[benchmark_name] = {}
        
        for model_name in model_names:
            # 构建报告文件路径
            # 格式: work_dir/{benchmark}/{model}_{params}/reports/{model}/{benchmark}.json
            model_config = config.LLM_SERVER_CONFIG.get(model_name)
            if not model_config:
                continue
            
            params = model_config.get('params', '')
            cleaned_model_name = model_name.replace('/', '-')
            
            report_path = os.path.join(work_dir, benchmark_name, f"{cleaned_model_name}_{params}", "reports")
            report_file = glob.glob(os.path.join(report_path, "*", "*.json"), recursive=True)[0]
            with open(report_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            evaluation_reports[benchmark_name][model_name] = report_data

    return evaluation_reports


if __name__ == "__main__":
    main()


"""
对比报告生成脚本
================

生成Markdown格式的评测结果对比报告

使用方法:
    python scripts/generate_report.py \
        --files results/llm/rag_qa/qwen2.5-7b_7B_20260111.json \
                results/llm/rag_qa/qwen2.5-32b_32B_20260111.json \
        --output reports/comparison_rag_qa.md
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

import orjson

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import REPORTS_DIR


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="生成评测对比报告")
    parser.add_argument(
        "--files",
        type=str,
        nargs="+",
        required=True,
        help="评测结果文件路径列表",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="输出报告路径 (默认: reports/comparison_{timestamp}.md)",
    )
    parser.add_argument(
        "--title",
        type=str,
        default="模型评测对比报告",
        help="报告标题",
    )
    return parser.parse_args()


def load_result_file(file_path: str) -> Dict[str, Any]:
    """加载评测结果文件"""
    path = Path(file_path)
    if not path.exists():
        print(f"警告: 文件不存在 {file_path}")
        return {}
    
    with open(path, "r", encoding="utf-8") as f:
        return orjson.loads(f.read())


def generate_markdown_report(
    results: List[Dict[str, Any]],
    title: str,
) -> str:
    """
    生成Markdown格式的对比报告
    
    Args:
        results: 评测结果列表
        title: 报告标题
        
    Returns:
        Markdown格式的报告内容
    """
    lines = []
    
    # 标题
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # 汇总信息
    lines.append("## 📊 评测概览")
    lines.append("")
    lines.append("| 模型 | 参数量 | 类型 | 数据集 | 样本数 |")
    lines.append("|------|--------|------|--------|--------|")
    
    for result in results:
        model_name = result.get("model_name", "未知")
        param_size = result.get("param_size", "未知")
        model_type = result.get("model_type", "未知")
        dataset = result.get("dataset", "未知")
        sample_count = len(result.get("details", []))
        
        lines.append(f"| {model_name} | {param_size} | {model_type} | {dataset} | {sample_count} |")
    
    lines.append("")
    
    # 指标对比表
    lines.append("## 📈 指标对比")
    lines.append("")
    
    # 收集所有指标
    all_metrics = set()
    for result in results:
        all_metrics.update(result.get("metrics", {}).keys())
    
    if all_metrics:
        # 表头
        header = "| 模型 | 参数量 |"
        separator = "|------|--------|"
        for metric in sorted(all_metrics):
            header += f" {metric} |"
            separator += "--------|"
        
        lines.append(header)
        lines.append(separator)
        
        # 数据行
        for result in results:
            model_name = result.get("model_name", "未知")
            param_size = result.get("param_size", "未知")
            metrics = result.get("metrics", {})
            
            row = f"| {model_name} | {param_size} |"
            for metric in sorted(all_metrics):
                value = metrics.get(metric, "-")
                if isinstance(value, float):
                    row += f" {value:.4f} |"
                else:
                    row += f" {value} |"
            
            lines.append(row)
        
        lines.append("")
    
    # 最佳模型
    lines.append("## 🏆 最佳表现")
    lines.append("")
    
    for metric in sorted(all_metrics):
        best_model = None
        best_score = -1
        
        for result in results:
            score = result.get("metrics", {}).get(metric, -1)
            if isinstance(score, (int, float)) and score > best_score:
                best_score = score
                best_model = result.get("model_name", "未知")
        
        if best_model:
            lines.append(f"- **{metric}**: {best_model} ({best_score:.4f})")
    
    lines.append("")
    
    # 配置信息
    lines.append("## ⚙️ 评测配置")
    lines.append("")
    
    for result in results:
        model_name = result.get("model_name", "未知")
        config = result.get("config", {})
        timestamp = result.get("timestamp", "未知")
        
        lines.append(f"### {model_name}")
        lines.append("")
        lines.append(f"- 评测时间: {timestamp}")
        
        for key, value in config.items():
            lines.append(f"- {key}: {value}")
        
        lines.append("")
    
    # 详细结果样例
    lines.append("## 📝 结果样例")
    lines.append("")
    lines.append("以下展示每个模型的前3条结果样例：")
    lines.append("")
    
    for result in results:
        model_name = result.get("model_name", "未知")
        details = result.get("details", [])[:3]  # 取前3条
        
        lines.append(f"### {model_name}")
        lines.append("")
        
        for i, detail in enumerate(details, 1):
            lines.append(f"**样例 {i}** (ID: {detail.get('id', '未知')})")
            lines.append("")
            
            # 显示分数
            scores = detail.get("scores", {})
            scores_str = ", ".join([f"{k}={v:.4f}" if isinstance(v, float) else f"{k}={v}" for k, v in scores.items()])
            lines.append(f"- 分数: {scores_str}")
            
            # 显示预测和参考 (如果有)
            if "prediction" in detail:
                pred = detail["prediction"]
                if len(pred) > 200:
                    pred = pred[:200] + "..."
                lines.append(f"- 预测: {pred}")
            
            if "reference" in detail:
                ref = detail["reference"]
                if len(ref) > 200:
                    ref = ref[:200] + "..."
                lines.append(f"- 参考: {ref}")
            
            lines.append("")
    
    return "\n".join(lines)


def main():
    args = parse_args()
    
    # 加载所有结果文件
    results = []
    for file_path in args.files:
        result = load_result_file(file_path)
        if result:
            results.append(result)
    
    if not results:
        print("错误: 没有有效的结果文件")
        sys.exit(1)
    
    print(f"已加载 {len(results)} 个结果文件")
    
    # 生成报告
    report = generate_markdown_report(results, args.title)
    
    # 确定输出路径
    if args.output:
        output_path = Path(args.output)
    else:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = REPORTS_DIR / f"comparison_{timestamp}.md"
    
    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 写入报告
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"报告已生成: {output_path}")


if __name__ == "__main__":
    main()


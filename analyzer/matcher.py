"""需求匹配引擎，将需求分析结果与 benchmark 能力标签匹配，生成推荐理由。"""
from typing import List, Dict, Any
from .benchmark_registry import get_all_benchmarks, BenchmarkInfo


class BenchmarkMatcher:
    """Benchmark 匹配器"""
    
    def __init__(self):
        self.benchmarks = get_all_benchmarks()
    
    def match(
        self,
        analyzed_capabilities: List[str],
        analyzed_description: str = "",
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        将需求分析结果与 benchmark 匹配
        
        Args:
            analyzed_capabilities: 分析得到的能力标签列表
            analyzed_description: 分析得到的需求描述
            top_k: 返回前 k 个最匹配的 benchmark
            
        Returns:
            匹配结果列表，每个结果包含 benchmark_name, match_score, reason, capabilities_covered
        """
        scores = []
        
        for benchmark_name, benchmark_info in self.benchmarks.items():
            score = self._calculate_match_score(
                benchmark_info,
                analyzed_capabilities,
                analyzed_description
            )
            
            if score > 0:  # 只返回有匹配的
                reason = self._generate_reason(
                    benchmark_info,
                    analyzed_capabilities,
                    score
                )
                
                # 找出匹配的能力标签
                matched_tags = [
                    tag for tag in analyzed_capabilities
                    if tag in benchmark_info.tags
                ]
                
                scores.append({
                    "benchmark_name": benchmark_name,
                    "pretty_name": benchmark_info.pretty_name,
                    "match_score": score,
                    "reason": reason,
                    "capabilities_covered": matched_tags,
                    "all_tags": benchmark_info.tags,
                    "description": benchmark_info.description,
                })
        
        # 按匹配分数排序
        scores.sort(key=lambda x: x["match_score"], reverse=True)
        
        # 返回前 top_k 个
        return scores[:top_k]
    
    def _calculate_match_score(
        self,
        benchmark: BenchmarkInfo,
        analyzed_capabilities: List[str],
        analyzed_description: str
    ) -> float:
        """
        计算匹配分数
        
        Args:
            benchmark: Benchmark 信息
            analyzed_capabilities: 分析得到的能力标签
            analyzed_description: 分析得到的需求描述
            
        Returns:
            匹配分数 (0-1)
        """
        if not analyzed_capabilities:
            return 0.0
        
        # 计算标签匹配度
        matched_tags = [tag for tag in analyzed_capabilities if tag in benchmark.tags]
        tag_score = len(matched_tags) / len(analyzed_capabilities) if analyzed_capabilities else 0.0
        
        # 计算描述匹配度（简单的关键词匹配）
        description_score = 0.0
        if analyzed_description:
            # 从 benchmark 的描述和使用场景中提取关键词
            benchmark_text = (
                benchmark.description + " " +
                " ".join(benchmark.use_cases)
            ).lower()
            
            # 简单的关键词匹配
            description_lower = analyzed_description.lower()
            common_words = set(benchmark_text.split()) & set(description_lower.split())
            if len(common_words) > 0:
                description_score = min(len(common_words) / 10.0, 0.3)  # 最多贡献 0.3 分
        
        # 综合分数：标签匹配度占 70%，描述匹配度占 30%
        total_score = tag_score * 0.7 + description_score * 0.3
        
        return round(total_score, 3)
    
    def _generate_reason(
        self,
        benchmark: BenchmarkInfo,
        analyzed_capabilities: List[str],
        match_score: float
    ) -> str:
        """
        生成推荐理由
        
        Args:
            benchmark: Benchmark 信息
            analyzed_capabilities: 分析得到的能力标签
            match_score: 匹配分数
            
        Returns:
            推荐理由文本
        """
        matched_tags = [tag for tag in analyzed_capabilities if tag in benchmark.tags]
        
        reason_parts = []
        
        # 添加匹配的能力标签说明
        if matched_tags:
            tag_names = {
                "REASONING": "推理能力",
                "LONG_CONTEXT": "长上下文处理能力",
                "CODING": "代码生成能力",
                "KNOWLEDGE": "知识理解能力",
                "QA": "问答能力",
                "FUNCTION_CALLING": "函数调用能力",
                "RETRIEVAL": "检索能力",
                "HALLUCINATION": "幻觉检测能力",
                "YES_NO": "是/否判断能力",
            }
            matched_names = [tag_names.get(tag, tag) for tag in matched_tags]
            reason_parts.append(
                f"该需求涉及 {', '.join(matched_names)}，"
                f"而 {benchmark.pretty_name} 专门评测这些能力。"
            )
        
        # 添加 benchmark 描述
        reason_parts.append(benchmark.description)
        
        # 添加适用场景
        if benchmark.use_cases:
            reason_parts.append(f"适用场景：{benchmark.use_cases[0]}")
        
        # 添加匹配度说明
        if match_score >= 0.8:
            reason_parts.append("匹配度很高，强烈推荐使用此 benchmark。")
        elif match_score >= 0.5:
            reason_parts.append("匹配度较高，建议使用此 benchmark。")
        else:
            reason_parts.append("匹配度一般，可作为备选方案。")
        
        return " ".join(reason_parts)


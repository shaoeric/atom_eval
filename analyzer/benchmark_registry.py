"""Benchmark 元数据注册表，包含所有 benchmark 的能力标签、描述和适用场景。"""
from typing import List, Dict, Any
from evalscope.constants import Tags


class BenchmarkInfo:
    """Benchmark 信息类"""
    def __init__(
        self,
        name: str,
        pretty_name: str,
        tags: List[str],
        description: str,
        use_cases: List[str],
        metrics: List[str],
    ):
        self.name = name
        self.pretty_name = pretty_name
        self.tags = tags
        self.description = description
        self.use_cases = use_cases
        self.metrics = metrics


# 所有可用的 benchmark 元数据
BENCHMARK_REGISTRY: Dict[str, BenchmarkInfo] = {
    "FRAMES": BenchmarkInfo(
        name="FRAMES",
        pretty_name="FRAMES",
        tags=[Tags.REASONING, Tags.LONG_CONTEXT],
        description="FRAMES 是一个全面的评估数据集，旨在测试检索增强生成（RAG）系统在事实性、检索准确性和推理方面的能力。",
        use_cases=[
            "需要评估模型在长文本上下文中的推理能力",
            "需要评估 RAG 系统的检索和生成能力",
            "需要评估模型处理复杂多步骤推理任务的能力",
            "需要评估模型在知识密集型任务中的表现",
        ],
        metrics=["acc"],
    ),
    "text2sql": BenchmarkInfo(
        name="text2sql",
        pretty_name="Text2SQL",
        tags=[Tags.CODING],
        description="Text2SQL 评测数据集用于评估模型将自然语言问题转换为 SQL 查询的能力。",
        use_cases=[
            "需要评估模型理解数据库模式的能力",
            "需要评估模型将自然语言转换为数据库查询的能力",
            "需要评估模型处理 SQL 相关任务的能力",
        ],
        metrics=["sql_ast_sim"],
    ),
    "halu_eval": BenchmarkInfo(
        name="halu_eval",
        pretty_name="HaluEval",
        tags=[Tags.KNOWLEDGE, Tags.HALLUCINATION, Tags.YES_NO],
        description="HaluEval 是一个大型的生成和人工标注的幻觉样本集合，用于评估 LLM 识别幻觉的性能。",
        use_cases=[
            "需要评估模型识别幻觉的能力",
            "需要评估模型的事实准确性",
            "需要评估模型在对话、问答和摘要任务中的真实性",
            "需要评估模型区分真实信息和虚假信息的能力",
        ],
        metrics=["accuracy", "precision", "recall", "f1_score", "yes_ratio"],
    ),
    "general_qa": BenchmarkInfo(
        name="general_qa",
        pretty_name="General QA",
        tags=[Tags.QA, Tags.KNOWLEDGE],
        description="通用问答评测数据集，用于评估模型在一般知识问答任务中的表现。",
        use_cases=[
            "需要评估模型的通用知识问答能力",
            "需要评估模型回答事实性问题的能力",
            "需要评估模型在开放域问答中的表现",
            "需要评估模型的基础知识理解能力",
        ],
        metrics=["acc"],
    ),
    "general_fc": BenchmarkInfo(
        name="general_fc",
        pretty_name="General Function Call",
        tags=[Tags.FUNCTION_CALLING],
        description="通用函数调用评测数据集，用于评估模型理解和执行函数调用的能力。",
        use_cases=[
            "需要评估agent的函数调用能力",
            "需要评估agent使用工具的能力",
            "需要评估模型理解 API 调用的能力",
            "需要评估模型在工具使用场景中的表现",
        ],
        metrics=["acc"],
    ),
}


def get_all_benchmarks() -> Dict[str, BenchmarkInfo]:
    """获取所有 benchmark 信息"""
    return BENCHMARK_REGISTRY


def get_benchmark(name: str) -> BenchmarkInfo:
    """根据名称获取 benchmark 信息"""
    if name not in BENCHMARK_REGISTRY:
        raise ValueError(f"Unknown benchmark: {name}")
    return BENCHMARK_REGISTRY[name]


def get_benchmarks_by_tags(tags: List[str]) -> List[BenchmarkInfo]:
    """根据标签获取匹配的 benchmark"""
    results = []
    for benchmark in BENCHMARK_REGISTRY.values():
        if any(tag in benchmark.tags for tag in tags):
            results.append(benchmark)
    return results


def get_all_tags() -> List[str]:
    """获取所有可用的标签"""
    all_tags = set()
    for benchmark in BENCHMARK_REGISTRY.values():
        all_tags.update(benchmark.tags)
    return sorted(list(all_tags))


"""使用 AgentScope 和 DeepSeek API 分析用户需求，提取关键能力点。"""
import os
import json
import asyncio
from typing import List, Dict, Any
import sys
from enum import Enum

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic import BaseModel, Field
from agentscope.agent import ReActAgent
from agentscope.model import OpenAIChatModel
from agentscope.formatter import DeepSeekChatFormatter, OpenAIChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.tool import Toolkit
from analyzer.benchmark_registry import get_all_benchmarks
import config


class BenchmarkRecommendation(BaseModel):
    """Benchmark 推荐的结构化输出模型"""
    
    benchmark: str = Field(
        description="推荐的 benchmark 名称，从可用的 benchmark 中选择",
        enum=list(get_all_benchmarks().keys()),
    )
    
    reason: str = Field(
        description="选择该 benchmark 的理由",
    )


class RequirementAnalysisResult(BaseModel):
    """需求分析结果的结构化输出模型"""
    
    capabilities: List[str] = Field(
        description="识别出的能力标签列表",
    )
    
    description: str = Field(
        description="需求描述",
    )
    
    key_points: List[str] = Field(
        description="关键需求点列表",
    )
    
    recommended_benchmarks: List[BenchmarkRecommendation] = Field(
        description="推荐的 benchmark 列表，每个包含 benchmark 名称和选择理由",
    )


class RequirementAnalyzer:
    """需求分析器，使用 AgentScope 分析用户需求"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        """
        初始化需求分析器
        
        Args:
            api_key: DeepSeek API key，如果为 None 则从环境变量或 config 读取
            base_url: DeepSeek API base URL，如果为 None 则从 config 读取
        """
        # 从 config 获取 DeepSeek 配置
        deepseek_config = config.LLM_SERVER_CONFIG.get('deepseek-chat', {})
        
        self.api_key = api_key or deepseek_config.get('api_key') or os.getenv('DEEPSEEK_API_KEY', '')
        self.base_url = base_url or deepseek_config.get('url', 'https://api.deepseek.com')
        self.model_name = deepseek_config.get('model', 'deepseek-chat')
        
        # 初始化 AgentScope 模型
        self.model = OpenAIChatModel(
            model_name=self.model_name,
            api_key=self.api_key,
            client_kwargs={"base_url": self.base_url},
            stream=False,
        )
        
        # 创建空的工具包（ReActAgent 需要，但我们不需要工具）
        toolkit = Toolkit()
        
        # 创建 ReActAgent
        self.agent = ReActAgent(
            name="RequirementAnalyzer",
            sys_prompt=self._get_system_prompt(),
            model=self.model,
            formatter=DeepSeekChatFormatter(),
            toolkit=toolkit,
            memory=InMemoryMemory(),
        )
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        # 获取所有可用的 benchmark 信息
        benchmarks = get_all_benchmarks()
        
        # 构建 benchmark 信息字符串
        benchmark_info_lines = []
        for name, info in benchmarks.items():
            tags_str = ", ".join(info.tags)
            benchmark_info_lines.append(
                f"- {name} ({info.pretty_name}): {info.description}\n"
                f"  能力标签: {tags_str}\n"
                f"  适用场景: {', '.join(info.use_cases[:2])}"
            )
        
        benchmark_info = "\n".join(benchmark_info_lines)
        
        return f"""你是一个专业的 AI 模型能力评估专家。你的任务是分析用户的需求，识别出需要评测的模型基础能力，并从可用的 benchmark 中选择最合适的进行评测。

可用的能力标签包括：
- REASONING: 推理能力
- LONG_CONTEXT: 长上下文处理能力
- CODING: 代码生成能力
- KNOWLEDGE: 知识理解能力
- QA: 问答能力
- FUNCTION_CALLING: 函数调用能力
- RETRIEVAL: 检索能力
- HALLUCINATION: 幻觉检测能力

可用的 Benchmark 列表（必须从以下列表中选择）：
{benchmark_info}

请仔细分析用户需求，提取出关键的能力标签和需求描述，并从上述 benchmark 列表中选择最合适的 benchmark（可以选多个），并为每个选择的 benchmark 提供详细的选择理由。

输出格式要求：
- capabilities: 能力标签列表
- description: 需求描述
- key_points: 关键需求点列表
- recommended_benchmarks: benchmark 推荐列表，每个包含 benchmark 名称和选择理由"""
    
    async def analyze_async(self, requirement: str) -> Dict[str, Any]:
        """
        异步分析用户需求
        
        Args:
            requirement: 用户需求描述
            
        Returns:
            包含能力标签、描述、关键点和推荐 benchmark 的字典
        """
        from agentscope.message import Msg
        
        # 创建用户消息
        user_msg = Msg(name="user", role="user", content=f"请分析以下需求：{requirement}")
        
        # 使用 ReActAgent 生成结构化输出
        response = await self.agent(user_msg, structured_model=RequirementAnalysisResult)

        # 从 metadata 中提取结构化输出
        if hasattr(response, 'metadata') and response.metadata:
            try:
                # 结构化输出可能在 metadata 的 structured_output 字段中
                structured_data = response.metadata
                if isinstance(structured_data, dict) and "structured_output" in structured_data:
                    structured_data = structured_data["structured_output"]
                
                # 解析结构化输出
                result = RequirementAnalysisResult(**structured_data)
                return {
                    "capabilities": result.capabilities,
                    "description": result.description,
                    "key_points": result.key_points,
                    "recommended_benchmarks": [
                        {
                            "benchmark": b.benchmark,
                            "reason": b.reason
                        }
                        for b in result.recommended_benchmarks
                    ]
                }
            except Exception as e:
                raise ValueError(f"Failed to parse structured output: {e}")
                # # 如果解析失败，尝试从文本中提取
                # import logging
                # logger = logging.getLogger(__name__)
                # logger.warning(f"Failed to parse structured output: {e}, falling back to text parsing")
                # response_text = response.get_text_content()
                # return self._parse_text_response(response_text, requirement)
        else:
            raise ValueError("No structured output found")
            # # 如果没有结构化输出，尝试从文本中提取
            # response_text = response.get_text_content()
            # return self._parse_text_response(response_text, requirement)
    
    # def _parse_text_response(self, response_text: str, requirement: str) -> Dict[str, Any]:
    #     """从文本响应中解析结果（备用方法）"""
    #     # 简单的文本解析逻辑
    #     capabilities = []
    #     description = requirement
    #     key_points = []
    #     benchmarks = []
    #     reasons = []
        
    #     # 获取所有可用的 benchmark 名称
    #     available_benchmarks = list(get_all_benchmarks().keys())
        
    #     # 尝试从响应中提取能力标签
    #     capability_keywords = {
    #         "推理": "REASONING",
    #         "长上下文": "LONG_CONTEXT",
    #         "代码": "CODING",
    #         "知识": "KNOWLEDGE",
    #         "问答": "QA",
    #         "函数调用": "FUNCTION_CALLING",
    #         "检索": "RETRIEVAL",
    #         "幻觉": "HALLUCINATION",
    #     }
        
    #     for keyword, tag in capability_keywords.items():
    #         if keyword in response_text:
    #             capabilities.append(tag)
        
    #     # 如果没有找到能力标签，使用默认的
    #     if not capabilities:
    #         capabilities = ["KNOWLEDGE", "QA"]
        
    #     # 尝试从响应中提取 benchmark 名称
    #     for bench_name in available_benchmarks:
    #         if bench_name.lower() in response_text.lower() or bench_name in response_text:
    #             benchmarks.append(bench_name)
    #             reasons.append(f"需求涉及 {bench_name} 相关的能力")
        
    #     # 如果没有找到 benchmark，使用默认的
    #     if not benchmarks:
    #         benchmarks = ["general_qa"]
    #         reasons = ["通用问答能力评测"]
        
    #     return {
    #         "capabilities": capabilities,
    #         "description": description,
    #         "key_points": key_points if key_points else [requirement],
    #         "recommended_benchmarks": {
    #             "benchmarks": benchmarks,
    #             "reasons": reasons,
    #         }
    #     }
    
    def analyze(self, requirement: str) -> Dict[str, Any]:
        """
        同步分析用户需求（包装异步方法）
        
        Args:
            requirement: 用户需求描述
            
        Returns:
            包含能力标签、描述和关键点的字典
        """
        return asyncio.run(self.analyze_async(requirement))


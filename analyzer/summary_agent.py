"""评估总结 Agent，用于生成模型对比报告。"""
import os
import json
import asyncio
from typing import List, Dict, Any
import sys
from pydantic import BaseModel, Field
from agentscope.agent import ReActAgent
from agentscope.model import OpenAIChatModel
from agentscope.formatter import DeepSeekChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.tool import Toolkit, view_text_file, write_text_file
from agentscope.message import Msg

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

class ModelScore(BaseModel):
    """模型评分"""
    
    model: str = Field(description="模型名称")
    score: float = Field(description="综合评分（0-100）")
    ranking: int = Field(description="排名（1表示最好）")
    strengths: List[str] = Field(description="优势列表")
    weaknesses: List[str] = Field(description="劣势列表")
    recommendation: str = Field(description="针对用户需求的推荐理由")


class SummaryReport(BaseModel):
    """总结报告的结构化输出模型"""
    
    benchmark_summaries: List[Dict[str, Any]] = Field(
        description="按 benchmark 分组的模型能力总结，每个元素包含 benchmark 名称和各个模型的表现"
    )
    
    model_comparison: str = Field(
        description="模型对比分析，包括各模型在不同 benchmark 上的表现对比"
    )
    
    model_scores: List[ModelScore] = Field(
        description="根据用户需求对候选模型的打分排序"
    )
    
    overall_summary: str = Field(
        description="整体总结和建议"
    )


class SummaryAgent:
    """评估总结 Agent"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        """
        初始化总结 Agent
        
        Args:
            api_key: DeepSeek API key
            base_url: DeepSeek API base URL
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
        
        # 创建空的工具包
        toolkit = Toolkit()
        toolkit.register_tool_function(view_text_file)
        toolkit.register_tool_function(write_text_file)
        
        # 创建 ReActAgent
        self.agent = ReActAgent(
            name="SummaryAgent",
            sys_prompt=self._get_system_prompt(),
            model=self.model,
            formatter=DeepSeekChatFormatter(),
            toolkit=toolkit,
            memory=InMemoryMemory(),
        )
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的 AI 模型评估专家。你的任务是分析评测报告，对模型能力进行总结、对比，并根据用户需求对模型进行打分排序。

你需要：
1. 按照 benchmark 对每个模型的能力进行总结
2. 对比不同模型在各个 benchmark 上的表现
3. 根据用户需求对候选模型进行综合打分（0-100分）和排序
4. 指出每个模型的优势和劣势
5. 给出针对用户需求的推荐理由

输出格式要求：
- benchmark_summaries: 按 benchmark 分组的总结列表
- model_comparison: 模型对比分析
- model_scores: 模型评分排序列表
- overall_summary: 整体总结和建议"""
    
    async def generate_summary_async(
        self,
        requirement: str,
        evaluation_reports: Dict[str, Dict[str, Any]],
        work_dir: str
    ) -> Dict[str, Any]:
        """
        异步生成总结报告
        
        Args:
            requirement: 用户原始需求
            evaluation_reports: 评测报告字典，格式为 {benchmark_name: {model_name: report_data}}
            
        Returns:
            总结报告字典
        """
        
        
        # 构建分析提示
        work_dir_path = os.path.join(work_dir, "report.md")
        with open(work_dir_path, 'w', encoding='utf-8') as f:
            f.write('')
            
        reports_json = json.dumps(evaluation_reports, ensure_ascii=False, indent=2)
        prompt = f"""请分析以下评测报告，生成模型对比总结报告。

用户需求：{requirement}

评测报告数据：
{reports_json}

请按照以下要求进行分析：
1. 按 benchmark 总结每个模型的表现
2. 对比不同模型的能力
3. 根据用户需求对模型打分排序
4. 给出推荐理由
5. 将分析结果写到{work_dir_path}文件中"""
        
        # 创建用户消息
        user_msg = Msg(name="user", role="user", content=prompt)
        
        # 使用 ReActAgent 生成结构化输出
        response = await self.agent(user_msg)
        
        # # 从 metadata 中提取结构化输出
        # if hasattr(response, 'metadata') and response.metadata:
        #     try:
        #         # 结构化输出可能在 metadata 的 structured_output 字段中
        #         structured_data = response.metadata
        #         if isinstance(structured_data, dict) and "structured_output" in structured_data:
        #             structured_data = structured_data["structured_output"]
                
        #         # 解析结构化输出
        #         result = SummaryReport(**structured_data)
        #         return {
        #             "benchmark_summaries": result.benchmark_summaries,
        #             "model_comparison": result.model_comparison,
        #             "model_scores": [
        #                 {
        #                     "model": score.model,
        #                     "score": score.score,
        #                     "ranking": score.ranking,
        #                     "strengths": score.strengths,
        #                     "weaknesses": score.weaknesses,
        #                     "recommendation": score.recommendation
        #                 }
        #                 for score in result.model_scores
        #             ],
        #             "overall_summary": result.overall_summary
        #         }
        #     except Exception as e:
        #         raise ValueError(f"Failed to parse structured output: {e}")
        # else:
        #     raise ValueError("No structured output found")
    
    def generate_summary(
        self,
        requirement: str,
        evaluation_reports: Dict[str, Dict[str, Any]],
        work_dir: str
    ) -> Dict[str, Any]:
        """
        同步生成总结报告（包装异步方法）
        
        Args:
            requirement: 用户原始需求
            evaluation_reports: 评测报告字典
            
        Returns:
            总结报告字典
        """
        asyncio.run(self.generate_summary_async(requirement, evaluation_reports, work_dir))
    
    # async def write_markdown_report_async(
    #     self,
    #     requirement: str,
    #     summary_data: Dict[str, Any],
    #     model_names: List[str],
    #     benchmark_names: List[str],
    #     work_dir: str
    # ) -> str:
    #     """
    #     agent 将总结数据格式化为 Markdown 报告, 并保存到工作目录
    #     """
    #     report_path = os.path.join(work_dir, "report.md")
    #     prompt = f"""请将用户需求、模型所需基础能力、模型名称、benchmark评估报告整理成Markdown文件, 保存至: {report_path}
        
    #     总结数据:
    #     {json.dumps(summary_data, ensure_ascii=False, indent=2)}
    #     """
    #     user_msg = Msg(name="user", role="user", content=prompt)
    #     response = await self.agent(user_msg)
    #     return response.content
    
    # def write_markdown_report(
    #     self,
    #     summary_data: Dict[str, Any],
    #     work_dir: str
    # ) -> str:
    #     """
    #     agent 将总结数据格式化为 Markdown 报告, 并保存到工作目录
    #     """
    #     return asyncio.run(self.write_markdown_report_async(summary_data, work_dir))
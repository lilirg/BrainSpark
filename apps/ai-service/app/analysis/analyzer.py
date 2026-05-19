import json
from typing import Any
from langchain_openai import ChatOpenAI
from app.core.config import settings


class CognitiveAnalyzer:
    """分析测评数据，生成认知维度评分"""
    
    def __init__(self):
        self.dimensions = ["记忆", "注意", "逻辑", "创造", "观察", "想象"]
    
    def analyze(self, events: list[dict]) -> dict[str, float]:
        """分析测评事件数据"""
        # 简化的统计分析
        analysis = {}
        for dim in self.dimensions:
            # 实际应从事件中提取对应维度的分数
            analysis[dim] = 75.0
        return analysis
    
    def generate_suggestions(self, dimensions: dict[str, float]) -> list[str]:
        """生成改进建议"""
        suggestions = []
        sorted_dims = sorted(dimensions.items(), key=lambda x: x[1])
        
        # 找出最低的两个维度
        for dim, score in sorted_dims[:2]:
            if score < 70:
                suggestions.append(f"建议加强{dim}能力训练")
        
        if not suggestions:
            suggestions.append("各维度发展均衡，建议保持当前训练计划")
        
        return suggestions
    
    async def generate_report(self, assessment_data: dict, 
                               knowledge_context: list[dict]) -> str:
        """调用 LLM 生成详细 AI 报告"""
        llm = ChatOpenAI(
            model=settings.DEFAULT_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_BASE_URL
        )
        
        prompt = f"""你是一位儿童心理教育学专家。请根据以下测评数据和教育知识库，为学生生成一份详细的能力评估报告。
        
测评数据: {json.dumps(assessment_data, ensure_ascii=False)}
参考知识: {json.dumps(knowledge_context, ensure_ascii=False)[:1000]}

请按照以下格式输出：
1. 综合评估
2. 能力维度分析
3. 个性化建议"""
        
        try:
            response = await llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            return f"生成报告失败: {str(e)}"
"""
认知维度分析引擎
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import math


class CognitiveAnalyzer:
    """认知维度分析器"""

    # 认知维度定义
    DIMENSIONS = {
        "ATTENTION": {
            "name": "注意力",
            "description": "注意力的集中程度和持久性",
            "min_age": 6,
            "max_age": 18,
        },
        "MEMORY": {
            "name": "记忆力",
            "description": "工作记忆的容量和准确性",
            "min_age": 6,
            "max_age": 18,
        },
        "LOGIC": {
            "name": "逻辑推理",
            "description": "逻辑推理和问题解决能力",
            "min_age": 6,
            "max_age": 18,
        },
        "SPATIAL": {
            "name": "空间认知",
            "description": "空间想象和视觉感知能力",
            "min_age": 6,
            "max_age": 18,
        },
        "LANGUAGE": {
            "name": "语言能力",
            "description": "语言理解和表达能力",
            "min_age": 6,
            "max_age": 18,
        },
        "EXECUTIVE": {
            "name": "执行功能",
            "description": "计划、组织和自我调控能力",
            "min_age": 6,
            "max_age": 18,
        },
    }

    # 常模数据（基于年龄分组）
    NORMS = {
        "6-8": {
            "ATTENTION": {"mean": 60.0, "std": 15.0},
            "MEMORY": {"mean": 55.0, "std": 12.0},
            "LOGIC": {"mean": 50.0, "std": 10.0},
            "SPATIAL": {"mean": 65.0, "std": 14.0},
            "LANGUAGE": {"mean": 70.0, "std": 16.0},
            "EXECUTIVE": {"mean": 45.0, "std": 11.0},
        },
        "9-11": {
            "ATTENTION": {"mean": 70.0, "std": 14.0},
            "MEMORY": {"mean": 65.0, "std": 13.0},
            "LOGIC": {"mean": 60.0, "std": 12.0},
            "SPATIAL": {"mean": 72.0, "std": 13.0},
            "LANGUAGE": {"mean": 75.0, "std": 14.0},
            "EXECUTIVE": {"mean": 55.0, "std": 12.0},
        },
        "12+": {
            "ATTENTION": {"mean": 78.0, "std": 12.0},
            "MEMORY": {"mean": 72.0, "std": 11.0},
            "LOGIC": {"mean": 70.0, "std": 12.0},
            "SPATIAL": {"mean": 78.0, "std": 11.0},
            "LANGUAGE": {"mean": 80.0, "std": 12.0},
            "EXECUTIVE": {"mean": 65.0, "std": 13.0},
        },
    }

    def __init__(self):
        self.analysis_history: List[Dict[str, Any]] = []

    def analyze_assessment(
        self,
        assessment_type: str,
        raw_scores: Dict[str, float],
        student_age: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        分析测评结果

        Args:
            assessment_type: 测评类型 (SCHULTER, DIGITAL_SPAN, PATTERN_REASONING)
            raw_scores: 原始分数
            student_age: 学生年龄
            metadata: 额外元数据

        Returns:
            分析结果
        """
        age_group = self._get_age_group(student_age)
        dimensions = self._map_to_dimensions(assessment_type, raw_scores)

        # 计算百分位和等级
        for dim in dimensions:
            norm = self.NORMS.get(age_group, {}).get(dim["code"], {})
            if norm:
                dim["percentile"] = self._calculate_percentile(
                    dim["score"], norm["mean"], norm["std"]
                )
                dim["level"] = self._get_level(dim["percentile"])
                dim["description"] = self.DIMENSIONS[dim["code"]]["description"]
                dim["suggestion"] = self._generate_suggestion(
                    dim["code"], dim["level"], student_age
                )

        # 计算综合得分
        overall_score = sum(d["score"] for d in dimensions) / len(dimensions)

        result = {
            "assessment_type": assessment_type,
            "student_age": student_age,
            "age_group": age_group,
            "overall_score": round(overall_score, 1),
            "dimensions": dimensions,
            "analyzed_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }

        self.analysis_history.append(result)
        return result

    def _get_age_group(self, age: int) -> str:
        """获取年龄分组"""
        if age <= 8:
            return "6-8"
        elif age <= 11:
            return "9-11"
        else:
            return "12+"

    def _map_to_dimensions(
        self, assessment_type: str, raw_scores: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """将原始分数映射到认知维度"""
        mapping = {
            "SCHULTER": [
                {"code": "ATTENTION", "score": raw_scores.get("reaction_time", 0)},
                {"code": "EXECUTIVE", "score": raw_scores.get("accuracy", 0)},
            ],
            "DIGITAL_SPAN": [
                {"code": "MEMORY", "score": raw_scores.get("span_length", 0)},
                {"code": "ATTENTION", "score": raw_scores.get("focus_score", 0)},
            ],
            "PATTERN_REASONING": [
                {"code": "LOGIC", "score": raw_scores.get("reasoning_score", 0)},
                {"code": "SPATIAL", "score": raw_scores.get("spatial_score", 0)},
            ],
        }
        return mapping.get(assessment_type, [])

    def _calculate_percentile(
        self, score: float, mean: float, std: float
    ) -> float:
        """计算百分位（基于正态分布）"""
        if std == 0:
            return 50.0
        z_score = (score - mean) / std
        # 使用误差函数近似计算百分位
        percentile = 0.5 * (1 + math.erf(z_score / math.sqrt(2)))
        return round(percentile * 100, 1)

    def _get_level(self, percentile: float) -> str:
        """根据百分位获取等级"""
        if percentile >= 85:
            return "HIGH"
        elif percentile >= 50:
            return "AVERAGE"
        elif percentile >= 16:
            return "LOW"
        else:
            return "VERY_LOW"

    def _generate_suggestion(
        self, dimension: str, level: str, age: int
    ) -> str:
        """生成个性化建议"""
        suggestions = {
            "ATTENTION": {
                "HIGH": "注意力集中能力优秀，建议继续保持现有的学习习惯。",
                "AVERAGE": "注意力水平正常，可以通过舒尔特方格等游戏进一步提升。",
                "LOW": "注意力需要加强，建议每天进行10分钟专注力训练。",
                "VERY_LOW": "注意力明显不足，建议咨询专业教育顾问。",
            },
            "MEMORY": {
                "HIGH": "记忆力出色，适合进行复杂的学习任务。",
                "AVERAGE": "记忆力正常，可以通过数字游戏提升工作记忆容量。",
                "LOW": "记忆力需要提升，建议多进行记忆类游戏训练。",
                "VERY_LOW": "记忆力明显偏弱，建议进行系统性的记忆训练。",
            },
            "LOGIC": {
                "HIGH": "逻辑推理能力强，适合学习编程和数学。",
                "AVERAGE": "逻辑推理能力正常，可以通过图形推理游戏提升。",
                "LOW": "逻辑推理需要加强，建议多玩策略类游戏。",
                "VERY_LOW": "逻辑推理能力明显不足，建议从基础开始训练。",
            },
            "SPATIAL": {
                "HIGH": "空间认知能力优秀，适合学习几何和艺术。",
                "AVERAGE": "空间认知能力正常，可以通过拼图游戏提升。",
                "LOW": "空间认知需要加强，建议多进行空间想象训练。",
                "VERY_LOW": "空间认知能力明显偏弱，建议进行专项训练。",
            },
            "LANGUAGE": {
                "HIGH": "语言能力出色，适合阅读和写作。",
                "AVERAGE": "语言能力正常，可以通过阅读更多书籍提升。",
                "LOW": "语言能力需要加强，建议多进行语言交流。",
                "VERY_LOW": "语言能力明显不足，建议咨询语言教育专家。",
            },
            "EXECUTIVE": {
                "HIGH": "执行功能优秀，具有良好的自我管理能力。",
                "AVERAGE": "执行功能正常，可以通过制定计划提升。",
                "LOW": "执行功能需要加强，建议学习时间管理技巧。",
                "VERY_LOW": "执行功能明显偏弱，建议进行结构化训练。",
            },
        }
        return suggestions.get(dimension, {}).get(
            level, "建议保持规律的学习和训练。"
        )

    def get_growth_trend(
        self, student_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取成长趋势"""
        history = [
            h for h in self.analysis_history
            if h.get("metadata", {}).get("student_id") == student_id
        ]
        return history[-limit:]

    def compare_with_norm(
        self, analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """与常模对比"""
        age_group = analysis_result["age_group"]
        comparison = []

        for dim in analysis_result["dimensions"]:
            norm = self.NORMS.get(age_group, {}).get(dim["code"], {})
            comparison.append({
                "dimension": dim["code"],
                "name": self.DIMENSIONS[dim["code"]]["name"],
                "student_score": dim["score"],
                "norm_mean": norm.get("mean", 0),
                "norm_std": norm.get("std", 0),
                "difference": round(dim["score"] - norm.get("mean", 0), 1),
            })

        return {
            "age_group": age_group,
            "comparison": comparison,
            "analyzed_at": datetime.utcnow().isoformat(),
        }
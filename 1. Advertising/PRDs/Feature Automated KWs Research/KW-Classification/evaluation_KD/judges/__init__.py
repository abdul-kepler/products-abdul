"""
LLM-as-a-Judge Evaluation System for KW Classification
======================================================

Based on academic research:
- PoLL (Panel of LLM Judges): https://arxiv.org/abs/2404.18796
- FLASK (Skill Decomposition): https://arxiv.org/abs/2307.10928

Usage:
    from judges import JudgeSystem

    judge = JudgeSystem()
    result = judge.evaluate("M02", module_output, expected_output, input_data)
"""

from .rubric_loader import RubricLoader
from .judge_system import JudgeSystem
from .poll_aggregator import PoLLAggregator

__all__ = ["JudgeSystem", "RubricLoader", "PoLLAggregator"]

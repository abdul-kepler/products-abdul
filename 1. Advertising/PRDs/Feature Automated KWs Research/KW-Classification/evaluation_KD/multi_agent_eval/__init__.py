"""
Multi-Agent Evaluation Framework

Adversarial debate + Likert scoring (0-5) for LLM output evaluation.

Pipeline: InputFilter -> Critic -> Defender -> Judge -> MetaJudge -> Aggregate
"""

from .pipeline.orchestrator import Orchestrator
from .pipeline.aggregator import Aggregator

__all__ = ['Orchestrator', 'Aggregator']
__version__ = '1.0.0'

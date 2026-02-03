"""
Error Analysis Package

Analysis modules:
A) error_analyzer.py - Automated analysis with metrics
B) pattern_detector.py - Pattern detection & clustering
C) llm_judge_analyzer.py - LLM-as-Judge evaluation
D) cohens_kappa.py - Inter-rater reliability calculation
E) braintrust_uploader.py - Upload results to Braintrust
F) path_comparator.py - Path A vs Path B comparison
G) baseline_report.py - Comprehensive baseline report generation
"""

from .error_analyzer import ErrorAnalyzer, BinaryClassifierAnalyzer, ListExtractorAnalyzer
from .pattern_detector import PatternDetector
from .llm_judge_analyzer import LLMJudgeAnalyzer
from .cohens_kappa import calculate_cohens_kappa, KappaResult
from .path_comparator import compare_paths, ComparisonResult
from .baseline_report import BaselineReportGenerator

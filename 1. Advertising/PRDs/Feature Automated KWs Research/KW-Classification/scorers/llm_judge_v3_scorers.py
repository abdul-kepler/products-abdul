"""
LLM Judge v3 Scorers for Braintrust Integration

Universal scorers that use v3 specialized judges for different modules.
Can be used directly in Braintrust experiments.

Usage:
    from llm_judge_v3_scorers import judge_m12b_v3, judge_m08_v3, judge_m07_v3
    
    # In Braintrust experiment
    scorers=[judge_m12b_v3, judge_m08_v3]
"""

import json
import sys
from pathlib import Path
from typing import Optional

import openai
from braintrust import Score

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from run_judge import build_judge_input, _get_predicted_class, _normalize_expected_class

# Judge configuration
JUDGE_MODEL = "gpt-4o"
JUDGE_TEMPERATURE = 0.1
JUDGES_DIR = Path(__file__).parent.parent / "prompts" / "judges"


def _load_judge_prompt(module: str, version: str = "v3") -> str:
    """Load judge prompt from file."""
    judge_files = {
        "m07_v3": "judge_m07_attribute_extraction_v3.md",
        "m08_v3": "judge_m08_attribute_ranks_v3.md",
        "m12b_v3": "judge_m12b_classification_v3.md",
    }
    
    key = f"{module.lower()}_{version}"
    if key not in judge_files:
        raise ValueError(f"No judge found for {module} {version}")
    
    judge_file = JUDGES_DIR / judge_files[key]
    if not judge_file.exists():
        raise FileNotFoundError(f"Judge file not found: {judge_file}")
    
    return judge_file.read_text()


def _run_judge(prompt: str) -> dict:
    """Call LLM judge and return result."""
    client = openai.OpenAI()
    
    response = client.chat.completions.create(
        model=JUDGE_MODEL,
        temperature=JUDGE_TEMPERATURE,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": prompt}]
    )
    
    return json.loads(response.choices[0].message.content)


def _build_record(input: dict, output: dict, expected: dict, metadata: dict = None) -> dict:
    """Build record in format expected by build_judge_input."""
    return {
        "input": input,
        "output": output,
        "expected": expected,
        "metadata": metadata or {}
    }


# =============================================================================
# M12b Classification Judge v3
# =============================================================================

def judge_m12b_v3(
    input: dict,
    output: dict, 
    expected: dict,
    metadata: dict = None
) -> Score:
    """
    LLM Judge v3 scorer for M12b Classification.
    Uses decision tree evaluation based on R/S/C/N workflow.
    
    Returns:
        Score with normalized score (0-1) and detailed metadata
    """
    try:
        # Load judge prompt
        judge_prompt = _load_judge_prompt("m12b", "v3")
        
        # Build judge input
        record = _build_record(input, output, expected, metadata)
        judge_input = build_judge_input(judge_prompt, record, "m12b")
        
        # Run judge
        result = _run_judge(judge_input)
        
        total_score = result.get("total_score", 0)
        verdict = result.get("verdict", "FAIL")
        
        return Score(
            name="judge_m12b_v3",
            score=total_score / 100.0,
            metadata={
                "verdict": verdict,
                "total_score": total_score,
                "summary": result.get("summary", ""),
                "correctness": result.get("evaluation", {}).get("correctness", {}),
                "decision_tree": result.get("evaluation", {}).get("decision_tree", {}),
                "reasoning_quality": result.get("evaluation", {}).get("reasoning_quality", {}),
                "root_cause": result.get("root_cause"),
                "improvement_suggestions": result.get("improvement_suggestions", []),
                "predicted": _get_predicted_class(output),
                "expected": _normalize_expected_class(expected),
            }
        )
        
    except Exception as e:
        # Fallback to simple accuracy
        predicted = _get_predicted_class(output)
        expected_val = _normalize_expected_class(expected)
        is_correct = predicted.upper() == expected_val.upper()
        
        return Score(
            name="judge_m12b_v3",
            score=1.0 if is_correct else 0.0,
            metadata={
                "error": str(e),
                "fallback": True,
                "predicted": predicted,
                "expected": expected_val,
            }
        )


# =============================================================================
# M08 Attribute Ranks Judge v3
# =============================================================================

def judge_m08_v3(
    input: dict,
    output: dict,
    expected: dict,
    metadata: dict = None
) -> Score:
    """
    LLM Judge v3 scorer for M08 Attribute Ranks.
    Uses conversion criticality and per-type ranking evaluation.
    
    Returns:
        Score with normalized score (0-1) and detailed metadata
    """
    try:
        judge_prompt = _load_judge_prompt("m08", "v3")
        record = _build_record(input, output, expected, metadata)
        judge_input = build_judge_input(judge_prompt, record, "m08")
        result = _run_judge(judge_input)
        
        total_score = result.get("total_score", 0)
        verdict = result.get("verdict", "FAIL")
        
        return Score(
            name="judge_m08_v3",
            score=total_score / 100.0,
            metadata={
                "verdict": verdict,
                "total_score": total_score,
                "summary": result.get("summary", ""),
                "correctness": result.get("evaluation", {}).get("correctness", {}),
                "rule_compliance": result.get("evaluation", {}).get("rule_compliance", {}),
                "reasoning_quality": result.get("evaluation", {}).get("reasoning_quality", {}),
                "improvement_suggestions": result.get("improvement_suggestions", []),
            }
        )
        
    except Exception as e:
        return Score(
            name="judge_m08_v3",
            score=0.0,
            metadata={"error": str(e), "fallback": True}
        )


# =============================================================================
# M07 Attribute Extraction Judge v3
# =============================================================================

def judge_m07_v3(
    input: dict,
    output: dict,
    expected: dict,
    metadata: dict = None
) -> Score:
    """
    LLM Judge v3 scorer for M07 Attribute Extraction.
    Uses attribute type categorization evaluation.
    
    Returns:
        Score with normalized score (0-1) and detailed metadata
    """
    try:
        judge_prompt = _load_judge_prompt("m07", "v3")
        record = _build_record(input, output, expected, metadata)
        judge_input = build_judge_input(judge_prompt, record, "m07")
        result = _run_judge(judge_input)
        
        total_score = result.get("total_score", 0)
        verdict = result.get("verdict", "FAIL")
        
        return Score(
            name="judge_m07_v3",
            score=total_score / 100.0,
            metadata={
                "verdict": verdict,
                "total_score": total_score,
                "summary": result.get("summary", ""),
                "correctness": result.get("evaluation", {}).get("correctness", {}),
                "categorization": result.get("evaluation", {}).get("categorization", {}),
                "reasoning_quality": result.get("evaluation", {}).get("reasoning_quality", {}),
                "improvement_suggestions": result.get("improvement_suggestions", []),
            }
        )
        
    except Exception as e:
        return Score(
            name="judge_m07_v3",
            score=0.0,
            metadata={"error": str(e), "fallback": True}
        )


# =============================================================================
# Composite Scorer (runs all applicable judges)
# =============================================================================

def judge_all_v3(
    input: dict,
    output: dict,
    expected: dict,
    metadata: dict = None,
    module: str = None
) -> list[Score]:
    """
    Run appropriate v3 judge based on module type.
    
    Args:
        module: Which module to judge (m07, m08, m12b)
        
    Returns:
        List of Score objects
    """
    scores = []
    
    if module:
        module_lower = module.lower()
        if module_lower == "m12b":
            scores.append(judge_m12b_v3(input, output, expected, metadata))
        elif module_lower == "m08":
            scores.append(judge_m08_v3(input, output, expected, metadata))
        elif module_lower == "m07":
            scores.append(judge_m07_v3(input, output, expected, metadata))
    
    return scores


# Export scorers
__all__ = [
    "judge_m12b_v3",
    "judge_m08_v3", 
    "judge_m07_v3",
    "judge_all_v3",
]

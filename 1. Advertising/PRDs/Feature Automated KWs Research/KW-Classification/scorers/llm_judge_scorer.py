"""
LLM Judge Scorer for M12b Classification Evaluation

This scorer uses an LLM to evaluate whether keyword classifications are correct,
providing detailed rubric-based scoring and chain-of-thought reasoning.
"""

import json
from pathlib import Path
from braintrust import Score
import openai

# Load judge prompt
PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "judge_m12b_classification.md"
JUDGE_PROMPT = PROMPT_PATH.read_text() if PROMPT_PATH.exists() else ""

# Judge model configuration
JUDGE_MODEL = "gpt-4o"  # Use strong model for judging
JUDGE_TEMPERATURE = 0.1  # Low temp for consistency


def llm_judge_m12b(
    input: dict,
    output: dict,
    expected: dict,
    metadata: dict = None
) -> Score:
    """
    LLM Judge scorer for M12b classification.

    Args:
        input: The input data (keyword, title, validated_use, etc.)
        output: Model's output (classification, confidence, reasoning)
        expected: Ground truth (relevancy)
        metadata: Optional metadata

    Returns:
        Score object with name, score (0-1), and metadata
    """
    # Extract values
    keyword = input.get("keyword", "")
    title = input.get("title", "")
    validated_use = input.get("validated_use", "")
    hard_constraints = input.get("hard_constraints", [])

    predicted_classification = output.get("classification", "N")
    predicted_confidence = output.get("confidence", 0.5)

    # Build reasoning from output steps
    reasoning_parts = []
    if output.get("step1_hard_constraint"):
        reasoning_parts.append(f"Step 1: {output['step1_hard_constraint'].get('reasoning', '')}")
    if output.get("step2_product_type"):
        reasoning_parts.append(f"Step 2: {output['step2_product_type'].get('reasoning', '')}")
    if output.get("step3_primary_use"):
        reasoning_parts.append(f"Step 3: {output['step3_primary_use'].get('reasoning', '')}")
    if output.get("step4_complementary"):
        reasoning_parts.append(f"Step 4: {output['step4_complementary'].get('reasoning', '')}")
    predicted_reasoning = "\n".join(reasoning_parts) if reasoning_parts else "No reasoning provided"

    expected_classification = expected.get("relevancy", expected.get("classification", "N"))

    # Format hard constraints
    if isinstance(hard_constraints, list):
        hard_constraints_str = ", ".join(hard_constraints) if hard_constraints else "None"
    else:
        hard_constraints_str = str(hard_constraints)

    # Build judge prompt
    judge_input = JUDGE_PROMPT.replace("{{keyword}}", keyword)
    judge_input = judge_input.replace("{{title}}", title[:200])  # Truncate for context
    judge_input = judge_input.replace("{{validated_use}}", validated_use)
    judge_input = judge_input.replace("{{hard_constraints}}", hard_constraints_str)
    judge_input = judge_input.replace("{{predicted_classification}}", predicted_classification)
    judge_input = judge_input.replace("{{predicted_confidence}}", str(predicted_confidence))
    judge_input = judge_input.replace("{{predicted_reasoning}}", predicted_reasoning)
    judge_input = judge_input.replace("{{expected_classification}}", expected_classification)

    try:
        # Call judge model
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=JUDGE_MODEL,
            temperature=JUDGE_TEMPERATURE,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": judge_input}
            ]
        )

        judge_result = json.loads(response.choices[0].message.content)

        # Extract scores
        total_score = judge_result.get("total_score", 0)
        verdict = judge_result.get("verdict", "FAIL")
        judge_confidence = judge_result.get("judge_confidence", 0.5)
        summary = judge_result.get("summary", "")

        # Normalize score to 0-1 range
        normalized_score = total_score / 100.0

        return Score(
            name="llm_judge_m12b",
            score=normalized_score,
            metadata={
                "verdict": verdict,
                "total_score": total_score,
                "judge_confidence": judge_confidence,
                "summary": summary,
                "classification_accuracy": judge_result.get("evaluation", {}).get("classification_accuracy", {}),
                "decision_tree_adherence": judge_result.get("evaluation", {}).get("decision_tree_adherence", {}),
                "reasoning_quality": judge_result.get("evaluation", {}).get("reasoning_quality", {}),
                "confidence_calibration": judge_result.get("evaluation", {}).get("confidence_calibration", {}),
                "improvement_suggestions": judge_result.get("improvement_suggestions", []),
                "predicted": predicted_classification,
                "expected": expected_classification,
                "correct": predicted_classification == expected_classification
            }
        )

    except Exception as e:
        # Fallback to simple accuracy if judge fails
        is_correct = predicted_classification == expected_classification
        return Score(
            name="llm_judge_m12b",
            score=1.0 if is_correct else 0.0,
            metadata={
                "error": str(e),
                "fallback": True,
                "predicted": predicted_classification,
                "expected": expected_classification,
                "correct": is_correct
            }
        )


def simple_accuracy_scorer(
    input: dict,
    output: dict,
    expected: dict,
    metadata: dict = None
) -> Score:
    """Simple accuracy scorer - checks if classification matches expected."""
    predicted = output.get("classification", "N")
    expected_val = expected.get("relevancy", expected.get("classification", "N"))
    is_correct = predicted == expected_val

    return Score(
        name="classification_accuracy",
        score=1.0 if is_correct else 0.0,
        metadata={
            "predicted": predicted,
            "expected": expected_val,
            "correct": is_correct
        }
    )


def confidence_calibration_scorer(
    input: dict,
    output: dict,
    expected: dict,
    metadata: dict = None
) -> Score:
    """
    Measures if model's confidence is calibrated.
    High confidence should correlate with correctness.
    """
    predicted = output.get("classification", "N")
    expected_val = expected.get("relevancy", expected.get("classification", "N"))
    confidence = output.get("confidence", 0.5)
    is_correct = predicted == expected_val

    # Calibration: confidence should match accuracy
    # If correct, high confidence is good. If wrong, high confidence is bad.
    if is_correct:
        calibration_score = confidence  # Higher confidence = better when correct
    else:
        calibration_score = 1 - confidence  # Lower confidence = better when wrong

    return Score(
        name="confidence_calibration",
        score=calibration_score,
        metadata={
            "confidence": confidence,
            "correct": is_correct,
            "interpretation": "well_calibrated" if calibration_score > 0.6 else "needs_calibration"
        }
    )


def per_class_scorer(
    input: dict,
    output: dict,
    expected: dict,
    metadata: dict = None
) -> list[Score]:
    """Returns separate scores for each class (R, S, C, N)."""
    predicted = output.get("classification", "N")
    expected_val = expected.get("relevancy", expected.get("classification", "N"))
    is_correct = predicted == expected_val

    scores = []
    for cls in ["R", "S", "C", "N"]:
        if expected_val == cls:
            scores.append(Score(
                name=f"accuracy_{cls}",
                score=1.0 if is_correct else 0.0,
                metadata={"predicted": predicted, "expected": expected_val}
            ))

    return scores


# Export all scorers
__all__ = [
    "llm_judge_m12b",
    "simple_accuracy_scorer",
    "confidence_calibration_scorer",
    "per_class_scorer"
]

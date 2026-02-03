#!/usr/bin/env python3
"""
LLM-as-Judge Evaluator for GEPA optimization.

Uses GPT-4o to semantically evaluate text generation outputs.
"""

import json
import os
import statistics
from typing import Any, Iterable, Tuple

from litellm import completion
from gepa.adapters.default_adapter.default_adapter import (
    DefaultDataInst,
    EvaluationResult,
    Evaluator,
)


JUDGE_SYSTEM_PROMPT = """You are an expert evaluator for product description analysis tasks.

Your job is to compare the MODEL OUTPUT with the EXPECTED OUTPUT and determine semantic similarity.

Scoring Guidelines:
- 1.0: Semantically identical (same meaning, possibly different words)
- 0.8-0.9: Same core meaning, minor differences in scope/detail
- 0.6-0.7: Partially overlapping meaning, captures main idea
- 0.4-0.5: Weak relationship, some relevant elements
- 0.2-0.3: Mostly different, minimal overlap
- 0.0-0.1: Completely different meaning or invalid output

Focus on MEANING and PURPOSE, not exact wording.

Respond in JSON format:
{
  "score": <float 0.0-1.0>,
  "feedback": "<brief explanation of score, what was good/bad>"
}
"""

JUDGE_USER_TEMPLATE = """## Task Context
{context}

## Expected Output
{expected}

## Model Output
{actual}

Evaluate the semantic similarity between Expected and Model outputs.
"""


def _parse_json_obj(value: Any) -> Any:
    """Parse JSON from a string if possible; otherwise return the value."""
    if isinstance(value, (dict, list)):
        return value
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    s = value.strip()
    if not s:
        return None
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        # Attempt to extract a JSON substring
        for open_c, close_c in (("{", "}"), ("[", "]")):
            if open_c in s and close_c in s:
                start = s.find(open_c)
                end = s.rfind(close_c)
                if start >= 0 and end > start:
                    try:
                        return json.loads(s[start:end + 1])
                    except json.JSONDecodeError:
                        continue
    return None


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).lower().strip().split())


def _list_f1(expected: Iterable[str], actual: Iterable[str]) -> Tuple[float, set, set, set]:
    exp_set = {e for e in expected if e}
    act_set = {a for a in actual if a}
    if not exp_set and not act_set:
        return 1.0, set(), set(), set()
    overlap = exp_set & act_set
    prec = len(overlap) / len(act_set) if act_set else 0.0
    rec = len(overlap) / len(exp_set) if exp_set else 0.0
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
    missing = exp_set - act_set
    extra = act_set - exp_set
    return f1, overlap, missing, extra


def _ordered_match(expected: list[str], actual: list[str]) -> float:
    if not expected and not actual:
        return 1.0
    n = max(len(expected), len(actual))
    if n == 0:
        return 0.0
    matches = sum(1 for i, e in enumerate(expected) if i < len(actual) and e == actual[i])
    return matches / n


def _taxonomy_list(obj: Any) -> list[str]:
    if isinstance(obj, dict) and "taxonomy" in obj:
        obj = obj["taxonomy"]
    if not isinstance(obj, list):
        return []
    out = []
    for item in obj:
        if isinstance(item, dict):
            out.append(_normalize_text(item.get("product_type") or item.get("name") or ""))
        else:
            out.append(_normalize_text(item))
    return [x for x in out if x]


def _attribute_table(obj: Any) -> list[dict]:
    if isinstance(obj, dict) and "attribute_table" in obj:
        obj = obj["attribute_table"]
    if not isinstance(obj, list):
        return []
    items = []
    for item in obj:
        if not isinstance(item, dict):
            continue
        attr_type = _normalize_text(item.get("attribute_type") or item.get("type"))
        attr_value = _normalize_text(item.get("attribute_value") or item.get("value"))
        rank = item.get("rank")
        if not attr_type or not attr_value:
            continue
        items.append({"type": attr_type, "value": attr_value, "rank": rank})
    return items


def _list_from_key(obj: Any, key: str) -> list[str]:
    if isinstance(obj, dict):
        value = obj.get(key)
    else:
        value = None
    if value in (None, "-", "none", "n/a"):
        return []
    if isinstance(value, list):
        return [_normalize_text(v) for v in value if _normalize_text(v)]
    return [_normalize_text(value)] if value else []


class ClassifierEvaluator:
    """Rule-based evaluator for classifier modules (M12/M12B/M13/M14/M15/M16).

    Uses confusion matrix weights to give partial credit for semantically related misclassifications.
    Based on academic best practices: exact match + weighted confusion matrix.
    """

    # Confusion weights for M12/M12B: (expected, actual) -> score
    # R=Relevant, S=Substitute, C=Complementary, N=Not relevant
    RSCN_WEIGHTS = {
        # Exact matches
        ("R", "R"): 1.0, ("S", "S"): 1.0, ("C", "C"): 1.0, ("N", "N"): 1.0,
        # Partial credit: R and S are both "relevant family"
        ("R", "S"): 0.5, ("S", "R"): 0.5,
        # Partial credit: R and C both positive relevance
        ("R", "C"): 0.3, ("C", "R"): 0.3,
        # Partial credit: S and C both non-primary but useful
        ("S", "C"): 0.4, ("C", "S"): 0.4,
        # Severe errors: opposite classifications
        ("R", "N"): 0.0, ("N", "R"): 0.0,
        ("S", "N"): 0.1, ("N", "S"): 0.1,
        ("C", "N"): 0.1, ("N", "C"): 0.1,
        # null handling (M12 can return null for N)
        (None, "N"): 1.0, ("N", None): 1.0,
        (None, None): 1.0,
        (None, "R"): 0.0, ("R", None): 0.0,
        (None, "S"): 0.1, ("S", None): 0.1,
        (None, "C"): 0.1, ("C", None): 0.1,
    }

    # Binary classifier weights for M02/M04/M05/M14/M15/M16
    # These modules output a specific value or null/N
    BINARY_WEIGHTS = {
        # M02: OB (Own Brand) or null
        ("OB", "OB"): 1.0,
        ("OB", None): 0.0, (None, "OB"): 0.0,
        ("OB", "N"): 0.0, ("N", "OB"): 0.0,
        # M04: CB (Competitor Brand) or null
        ("CB", "CB"): 1.0,
        ("CB", None): 0.0, (None, "CB"): 0.0,
        ("CB", "N"): 0.0, ("N", "CB"): 0.0,
        # M05: NB (Non-Branded) or null
        ("NB", "NB"): 1.0,
        ("NB", None): 0.0, (None, "NB"): 0.0,
        ("NB", "N"): 0.0, ("N", "NB"): 0.0,
        # M14: R (Relevant) or N (Not Relevant)
        ("R", "R"): 1.0, ("N", "N"): 1.0,
        ("R", "N"): 0.0, ("N", "R"): 0.0,
        # Also handle null as equivalent to N for negative cases
        (None, None): 1.0, (None, "N"): 1.0, ("N", None): 1.0,
        ("R", None): 0.0, (None, "R"): 0.0,
        # M15: S (Substitute) or N (Not Substitute)
        ("S", "S"): 1.0,
        ("S", "N"): 0.0, ("N", "S"): 0.0,
        ("S", None): 0.0, (None, "S"): 0.0,
        # M16: C (Complementary) or N (Not Complementary)
        ("C", "C"): 1.0,
        ("C", "N"): 0.0, ("N", "C"): 0.0,
        ("C", None): 0.0, (None, "C"): 0.0,
    }

    # M13: true/false (same_type)
    BOOL_WEIGHTS = {
        ("true", "true"): 1.0, ("false", "false"): 1.0,
        ("true", "false"): 0.0, ("false", "true"): 0.0,
        # Handle variations
        (True, True): 1.0, (False, False): 1.0,
        (True, False): 0.0, (False, True): 0.0,
        ("yes", "yes"): 1.0, ("no", "no"): 1.0,
        ("yes", "no"): 0.0, ("no", "yes"): 0.0,
    }

    def __init__(
        self,
        module_id: str,
        judge_model: str,
        judge_rounds: int,
        judge_agg: str,
        hybrid_weight: float,
    ):
        self.module_id = module_id.lower()
        self.hybrid_weight = max(0.0, min(1.0, float(hybrid_weight)))
        config = MODULE_EVALUATORS.get(self.module_id, {})
        self.output_key = config.get("output_key", "relevancy")
        self.judge = LLMJudgeEvaluator(
            judge_model=judge_model,
            output_key=self.output_key,
            task_context=config.get("task_context", ""),
            judge_rounds=judge_rounds,
            judge_agg=judge_agg,
        )

    def __call__(self, data: DefaultDataInst, response: str) -> EvaluationResult:
        expected_obj = _parse_json_obj(data.get("answer"))
        actual_obj = _parse_json_obj(response)

        # Extract classification values
        expected_val = self._extract_class(expected_obj)
        actual_val = self._extract_class(actual_obj)

        # Get score from confusion matrix
        if self.module_id == "m13":
            score = self._score_boolean(expected_val, actual_val)
        elif self.module_id in {"m02", "m02b", "m04", "m04b", "m05", "m05b", "m14", "m15", "m16"}:
            score = self._score_binary(expected_val, actual_val)
        else:  # m12, m12b
            score = self._score_rscn(expected_val, actual_val)

        feedback = f"expected={expected_val}, actual={actual_val}, rule_score={score:.2f}"
        objective_scores = {"exact_match": 1.0 if expected_val == actual_val else 0.0}

        # Optional hybrid with LLM judge for edge cases
        if self.hybrid_weight > 0.0 and score < 1.0 and score > 0.0:
            # Only call judge for partial matches (ambiguous cases)
            try:
                judge_result = self.judge(data, response)
                combined = (1.0 - self.hybrid_weight) * score + self.hybrid_weight * judge_result.score
                feedback = f"{feedback} | judge={judge_result.score:.2f} | combined={combined:.2f}"
                objective_scores["judge_score"] = judge_result.score
                score = combined
            except Exception as e:
                feedback = f"{feedback} | judge_error={e}"

        return EvaluationResult(score=score, feedback=feedback, objective_scores=objective_scores)

    def _extract_class(self, obj: Any) -> Any:
        """Extract classification value from JSON object."""
        if obj is None:
            return None
        if isinstance(obj, dict):
            val = obj.get(self.output_key)
            if val is None or val in ("null", "none", "-", ""):
                return None
            # Handle boolean values (M13 same_type)
            if isinstance(val, bool):
                return "true" if val else "false"
            return str(val).upper() if isinstance(val, str) else val
        if isinstance(obj, str):
            s = obj.strip().lower()
            if s in ("null", "none", "-", ""):
                return None
            # Check if it's a boolean string
            if s in ("true", "false"):
                return s
            return obj.strip().upper()
        if isinstance(obj, bool):
            return "true" if obj else "false"
        return None

    def _score_rscn(self, expected: Any, actual: Any) -> float:
        """Score using R/S/C/N confusion matrix."""
        # Normalize to uppercase or None
        exp = expected.upper() if isinstance(expected, str) else expected
        act = actual.upper() if isinstance(actual, str) else actual
        return self.RSCN_WEIGHTS.get((exp, act), 0.0)

    def _score_binary(self, expected: Any, actual: Any) -> float:
        """Score binary classifier (R/S/C or N)."""
        # Handle lists (model sometimes outputs list instead of scalar)
        if isinstance(expected, list):
            expected = expected[0] if expected else None
        if isinstance(actual, list):
            actual = actual[0] if actual else None
        exp = expected.upper() if isinstance(expected, str) else expected
        act = actual.upper() if isinstance(actual, str) else actual
        # Try specific weight first
        score = self.BINARY_WEIGHTS.get((exp, act))
        if score is not None:
            return score
        # Fall back to RSCN weights for edge cases
        return self.RSCN_WEIGHTS.get((exp, act), 0.0)

    def _score_boolean(self, expected: Any, actual: Any) -> float:
        """Score boolean classifier (M13 same_type: true/false)."""
        # Normalize to lowercase string
        def norm(v):
            if v is None:
                return None
            if isinstance(v, bool):
                return "true" if v else "false"
            s = str(v).lower().strip()
            if s in ("true", "yes", "1"):
                return "true"
            if s in ("false", "no", "0"):
                return "false"
            return s

        exp = norm(expected)
        act = norm(actual)

        if exp == act:
            return 1.0
        return 0.0


class ListEvaluator:
    """Rule-based evaluator for list outputs (M01/M01a/M01b/M11).

    Uses F1-score for set comparison with optional count constraints.
    Based on academic best practices: set-based metrics + rubric validation.
    """

    # Module-specific constraints
    MODULE_CONSTRAINTS = {
        "m01": {
            "output_key": "brand_entities",
            "min_count": 1,
            "max_count": None,  # No upper limit
            "check_canonical_first": False,
        },
        "m01a": {
            "output_key": "variations",
            "min_count": 8,
            "max_count": 12,
            "check_canonical_first": True,  # First item must be canonical spelling
        },
        "m01b": {
            "output_key": "sub_brands",  # Primary field; also checks manufacturer
            "min_count": 0,  # Can be empty
            "max_count": None,
            "check_canonical_first": False,
            "multi_field": True,  # Has multiple output fields
        },
        "m11": {
            "output_key": "hard_constraints",
            "min_count": 0,  # Most products have 0 constraints
            "max_count": 3,  # Rarely more than 2-3
            "check_canonical_first": False,
            "expected_empty_rate": 0.9,  # 90% of products have 0 constraints
        },
    }

    def __init__(
        self,
        module_id: str,
        judge_model: str,
        judge_rounds: int,
        judge_agg: str,
        hybrid_weight: float,
    ):
        self.module_id = module_id.lower()
        self.hybrid_weight = max(0.0, min(1.0, float(hybrid_weight)))
        self.constraints = self.MODULE_CONSTRAINTS.get(self.module_id, {})
        self.output_key = self.constraints.get("output_key", "")

        config = MODULE_EVALUATORS.get(self.module_id, {})
        self.judge = LLMJudgeEvaluator(
            judge_model=judge_model,
            output_key=self.output_key,
            task_context=config.get("task_context", ""),
            judge_rounds=judge_rounds,
            judge_agg=judge_agg,
        )

    def __call__(self, data: DefaultDataInst, response: str) -> EvaluationResult:
        expected_obj = _parse_json_obj(data.get("answer"))
        actual_obj = _parse_json_obj(response)

        if self.module_id == "m01b":
            return self._score_m01b(expected_obj, actual_obj, data, response)

        return self._score_list(expected_obj, actual_obj, data, response)

    def _score_list(self, expected_obj: Any, actual_obj: Any, data: DefaultDataInst, response: str) -> EvaluationResult:
        """Score a simple list output."""
        exp_list = _list_from_key(expected_obj, self.output_key)
        act_list = _list_from_key(actual_obj, self.output_key)

        # Handle both empty case
        if not exp_list and not act_list:
            return EvaluationResult(score=1.0, feedback="Both lists empty (correct)", objective_scores={"f1": 1.0})

        # Calculate F1 score
        f1, overlap, missing, extra = _list_f1(exp_list, act_list)

        # Apply penalties for constraint violations
        penalty = 0.0
        penalty_reasons = []

        # Count constraints (M01a: 8-12, M11: 0-3)
        min_count = self.constraints.get("min_count", 0)
        max_count = self.constraints.get("max_count")
        actual_count = len(act_list)

        if actual_count < min_count:
            penalty += 0.2
            penalty_reasons.append(f"below_min_count({actual_count}<{min_count})")
        if max_count and actual_count > max_count:
            penalty += 0.2
            penalty_reasons.append(f"above_max_count({actual_count}>{max_count})")

        # Canonical first check (M01a)
        if self.constraints.get("check_canonical_first") and act_list:
            # Get brand name from input if available
            input_obj = _parse_json_obj(data.get("input", "{}"))
            brand_name = None
            if isinstance(input_obj, dict):
                brand_name = input_obj.get("brand_name", "")
            elif isinstance(input_obj, str):
                # Try to extract from template
                brand_name = input_obj.split("\n")[0] if input_obj else ""

            if brand_name:
                canonical = _normalize_text(brand_name)
                first_item = _normalize_text(act_list[0]) if act_list else ""
                if canonical and first_item != canonical:
                    penalty += 0.1
                    penalty_reasons.append(f"first_not_canonical({first_item}!={canonical})")

        # Final rule score
        rule_score = max(0.0, f1 - penalty)
        feedback = f"f1={f1:.2f}, missing={len(missing)}, extra={len(extra)}"
        if penalty_reasons:
            feedback += f", penalties=[{', '.join(penalty_reasons)}]"

        objective_scores = {"f1": f1, "precision": len(overlap)/len(act_list) if act_list else 0.0,
                           "recall": len(overlap)/len(exp_list) if exp_list else 0.0}

        return self._hybridize(rule_score, feedback, objective_scores, data, response)

    def _score_m01b(self, expected_obj: Any, actual_obj: Any, data: DefaultDataInst, response: str) -> EvaluationResult:
        """Score M01b multi-field output (sub_brands, searchable_standards, manufacturer)."""
        if not isinstance(expected_obj, dict):
            expected_obj = {}
        if not isinstance(actual_obj, dict):
            return EvaluationResult(score=0.0, feedback="Output is not JSON object", objective_scores=None)

        scores = []
        feedback_parts = []

        # Sub-brands (60% weight)
        exp_subs = _list_from_key(expected_obj, "sub_brands")
        act_subs = _list_from_key(actual_obj, "sub_brands")
        f1_subs, _, missing_subs, extra_subs = _list_f1(exp_subs, act_subs)
        scores.append(("sub_brands", f1_subs, 0.6))
        feedback_parts.append(f"sub_brands_f1={f1_subs:.2f}")

        # Searchable standards (10% weight) - should usually be empty
        exp_standards = _list_from_key(expected_obj, "searchable_standards")
        act_standards = _list_from_key(actual_obj, "searchable_standards")
        f1_standards, _, _, _ = _list_f1(exp_standards, act_standards)
        # Bonus if both empty (correct behavior per rubric)
        if not exp_standards and not act_standards:
            f1_standards = 1.0
        scores.append(("standards", f1_standards, 0.1))
        feedback_parts.append(f"standards_f1={f1_standards:.2f}")

        # Manufacturer (30% weight)
        exp_mfr = expected_obj.get("manufacturer")
        act_mfr = actual_obj.get("manufacturer")
        mfr_score = self._score_manufacturer(exp_mfr, act_mfr)
        scores.append(("manufacturer", mfr_score, 0.3))
        feedback_parts.append(f"mfr_score={mfr_score:.2f}")

        # Weighted average
        rule_score = sum(s * w for _, s, w in scores)
        feedback = ", ".join(feedback_parts)
        objective_scores = {name: score for name, score, _ in scores}

        return self._hybridize(rule_score, feedback, objective_scores, data, response)

    def _score_manufacturer(self, expected: Any, actual: Any) -> float:
        """Score manufacturer field (object or null)."""
        # Both null = correct (manufacturer == brand)
        if expected is None and actual is None:
            return 1.0
        # One null, other not = wrong
        if expected is None or actual is None:
            return 0.0
        # Both have values - compare name
        if isinstance(expected, dict) and isinstance(actual, dict):
            exp_name = _normalize_text(expected.get("name", ""))
            act_name = _normalize_text(actual.get("name", ""))
            if exp_name == act_name:
                return 1.0
            # Partial credit for similar names
            if exp_name and act_name and (exp_name in act_name or act_name in exp_name):
                return 0.7
            return 0.0
        return 0.0

    def _hybridize(
        self,
        rule_score: float,
        rule_feedback: str,
        objective_scores: dict,
        data: DefaultDataInst,
        response: str,
    ) -> EvaluationResult:
        """Optionally combine with LLM judge score."""
        if self.hybrid_weight <= 0.0:
            return EvaluationResult(
                score=rule_score,
                feedback=rule_feedback,
                objective_scores=objective_scores,
            )

        try:
            judge_result = self.judge(data, response)
            combined = (1.0 - self.hybrid_weight) * rule_score + self.hybrid_weight * judge_result.score
            feedback = f"{rule_feedback} | judge={judge_result.score:.2f} | combined={combined:.2f}"
            return EvaluationResult(
                score=combined,
                feedback=feedback,
                objective_scores={**objective_scores, "judge_score": judge_result.score},
            )
        except Exception as e:
            return EvaluationResult(
                score=rule_score,
                feedback=f"{rule_feedback} | judge_error={e}",
                objective_scores=objective_scores,
            )


class StructuredEvaluator:
    """Rule-based evaluator for structured JSON outputs (M06/M07/M08) with optional LLM fallback."""

    def __init__(
        self,
        module_id: str,
        judge_model: str,
        judge_rounds: int,
        judge_agg: str,
        hybrid_weight: float,
    ):
        self.module_id = module_id.lower()
        self.hybrid_weight = max(0.0, min(1.0, float(hybrid_weight)))
        config = MODULE_EVALUATORS.get(self.module_id, {})
        self.judge = LLMJudgeEvaluator(
            judge_model=judge_model,
            output_key=config.get("output_key", ""),
            task_context=config.get("task_context", ""),
            judge_rounds=judge_rounds,
            judge_agg=judge_agg,
        )

    def __call__(self, data: DefaultDataInst, response: str) -> EvaluationResult:
        expected_obj = _parse_json_obj(data.get("answer"))
        actual_obj = _parse_json_obj(response)

        if self.module_id == "m06":
            return self._score_m06(expected_obj, actual_obj, data, response)
        if self.module_id == "m07":
            return self._score_m07(expected_obj, actual_obj, data, response)
        if self.module_id == "m08":
            return self._score_m08(expected_obj, actual_obj, data, response)

        return EvaluationResult(score=0.0, feedback="Unsupported structured module", objective_scores=None)

    def _score_m06(self, expected_obj: Any, actual_obj: Any, data: DefaultDataInst, response: str) -> EvaluationResult:
        exp = _taxonomy_list(expected_obj)
        act = _taxonomy_list(actual_obj)
        if not exp and not act:
            return EvaluationResult(score=1.0, feedback="Both taxonomy lists empty", objective_scores=None)
        if not exp or not act:
            return EvaluationResult(score=0.0, feedback="Missing taxonomy list in expected or output", objective_scores=None)

        f1, overlap, missing, extra = _list_f1(exp, act)
        order = _ordered_match(exp, act)
        rule_score = 0.7 * f1 + 0.3 * order
        feedback = f"rule taxonomy_f1={f1:.2f}, order_match={order:.2f}, missing={len(missing)}, extra={len(extra)}"
        return self._hybridize(rule_score, feedback, {"taxonomy_f1": f1, "order_match": order}, data, response)

    def _score_m07(self, expected_obj: Any, actual_obj: Any, data: DefaultDataInst, response: str) -> EvaluationResult:
        if not isinstance(expected_obj, dict):
            return EvaluationResult(score=0.0, feedback="Expected output is not JSON object", objective_scores=None)
        if not isinstance(actual_obj, dict):
            return EvaluationResult(score=0.0, feedback="Output is not JSON object", objective_scores=None)

        dims = []
        scores = []
        for key in ["variants", "use_cases", "audiences"]:
            exp_list = _list_from_key(expected_obj, key)
            act_list = _list_from_key(actual_obj, key)
            f1, _, _, _ = _list_f1(exp_list, act_list)
            dims.append((key, f1))
            scores.append(f1)

        if not scores:
            return EvaluationResult(score=0.0, feedback="No comparable fields", objective_scores=None)

        rule_score = sum(scores) / len(scores)
        feedback = "rule " + "; ".join([f"{k}_f1={v:.2f}" for k, v in dims])
        return self._hybridize(
            rule_score,
            feedback,
            {f"{k}_f1": v for k, v in dims},
            data,
            response,
        )

    def _score_m08(self, expected_obj: Any, actual_obj: Any, data: DefaultDataInst, response: str) -> EvaluationResult:
        exp_items = _attribute_table(expected_obj)
        act_items = _attribute_table(actual_obj)
        if not exp_items and not act_items:
            return EvaluationResult(score=1.0, feedback="Both attribute tables empty", objective_scores=None)
        if not exp_items or not act_items:
            return EvaluationResult(score=0.0, feedback="Missing attribute table in expected or output", objective_scores=None)

        exp_keys = {(i["type"], i["value"]) for i in exp_items}
        act_keys = {(i["type"], i["value"]) for i in act_items}
        f1, overlap, missing, extra = _list_f1(
            [f"{t}:{v}" for t, v in exp_keys],
            [f"{t}:{v}" for t, v in act_keys],
        )

        # Rank match for overlapping keys
        # Note: overlap contains strings "type:value", convert back to tuples for rank lookup
        exp_rank = {(i["type"], i["value"]): i.get("rank") for i in exp_items}
        act_rank = {(i["type"], i["value"]): i.get("rank") for i in act_items}
        shared_tuples = exp_keys & act_keys  # Use tuple sets directly for rank comparison
        if shared_tuples:
            matches = 0
            for key in shared_tuples:
                if exp_rank.get(key) == act_rank.get(key):
                    matches += 1
            rank_match = matches / len(shared_tuples)
        else:
            rank_match = 0.0

        rule_score = 0.7 * f1 + 0.3 * rank_match
        feedback = f"rule attr_f1={f1:.2f}, rank_match={rank_match:.2f}, missing={len(missing)}, extra={len(extra)}"
        return self._hybridize(
            rule_score,
            feedback,
            {"attribute_f1": f1, "rank_match": rank_match},
            data,
            response,
        )

    def _hybridize(
        self,
        rule_score: float,
        rule_feedback: str,
        objective_scores: dict,
        data: DefaultDataInst,
        response: str,
    ) -> EvaluationResult:
        if self.hybrid_weight <= 0.0:
            return EvaluationResult(
                score=rule_score,
                feedback=rule_feedback,
                objective_scores=objective_scores,
            )

        judge_result = self.judge(data, response)
        combined = (1.0 - self.hybrid_weight) * rule_score + self.hybrid_weight * judge_result.score
        feedback = f"{rule_feedback} | judge={judge_result.score:.2f} | combined={combined:.2f}"
        return EvaluationResult(
            score=combined,
            feedback=feedback,
            objective_scores={
                **objective_scores,
                "judge_score": judge_result.score,
            },
        )


class LLMJudgeEvaluator:
    """Evaluator that uses LLM-as-Judge for semantic comparison."""

    def __init__(
        self,
        judge_model: str = "gpt-4o",
        output_key: str = "primary_use",
        task_context: str = "Identify the primary intended use of a product",
        judge_rounds: int = 1,
        judge_agg: str = "mean",
    ):
        """
        Initialize LLM-as-Judge evaluator.

        Args:
            judge_model: Model to use for judging (e.g., "gpt-4o")
            output_key: The key in expected output to compare
            task_context: Description of what the task is evaluating
        """
        self.judge_model = judge_model
        self.output_key = output_key
        self.task_context = task_context
        self.judge_rounds = max(1, int(judge_rounds))
        self.judge_agg = judge_agg.lower().strip()

        # Validate API key based on judge model
        if judge_model.startswith("gemini"):
            if not os.getenv("GEMINI_API_KEY"):
                raise RuntimeError("GEMINI_API_KEY not set for Gemini judge model")
        elif judge_model.startswith("claude") or judge_model.startswith("anthropic"):
            if not os.getenv("ANTHROPIC_API_KEY"):
                raise RuntimeError("ANTHROPIC_API_KEY not set for Anthropic judge model")
        else:
            # Default to OpenAI
            if not os.getenv("OPENAI_API_KEY"):
                raise RuntimeError("OPENAI_API_KEY not set for OpenAI judge model")

    def __call__(
        self,
        data: DefaultDataInst,
        response: str,
    ) -> EvaluationResult:
        """
        Evaluate model response against expected answer.

        Args:
            data: Input data with expected answer
            response: Model's response string

        Returns:
            EvaluationResult with score, feedback, and optional objective_scores
        """
        expected = data["answer"]
        actual = self._extract_output(response)

        # Quick exact match check
        if self._normalize(expected) == self._normalize(actual):
            return EvaluationResult(
                score=1.0,
                feedback="Exact match",
                objective_scores=None,
            )

        # LLM judge call (single or multi-round)
        try:
            score, feedback = self._call_judge_multi(expected, actual)
        except Exception as e:
            score = 0.0
            feedback = f"Judge error: {e}"

        return EvaluationResult(
            score=score,
            feedback=feedback,
            objective_scores=None,
        )

    def _call_judge_multi(self, expected: str, actual: str) -> tuple[float, str]:
        """Run judge multiple times and aggregate score."""
        if self.judge_rounds <= 1:
            return self._call_judge(expected, actual)

        scores = []
        feedbacks = []
        for _ in range(self.judge_rounds):
            score, feedback = self._call_judge(expected, actual)
            scores.append(score)
            feedbacks.append(feedback)

        if self.judge_agg == "median":
            agg = statistics.median(scores)
        else:
            agg = statistics.mean(scores)

        feedback = f"multi_round_{self.judge_agg}={agg:.2f}; scores={scores}; sample={feedbacks[0]}"
        return agg, feedback

    def _extract_output(self, response: str) -> str:
        """Extract the relevant output from model response."""
        # Try to parse as JSON
        try:
            data = json.loads(response)
            if isinstance(data, dict):
                # Look for our output key
                if self.output_key in data:
                    return str(data[self.output_key])
                # Common variations
                for key in ["output", "result", "answer", "response"]:
                    if key in data:
                        return str(data[key])
            return response
        except json.JSONDecodeError:
            return response

    def _normalize(self, text: str) -> str:
        """Normalize text for comparison."""
        if text is None:
            return ""
        # Handle boolean values (e.g., m13 same_type)
        if isinstance(text, bool):
            return str(text).lower()
        if not text:
            return ""
        return str(text).lower().strip()

    def _call_judge(self, expected: str, actual: str) -> tuple[float, str]:
        """Call LLM judge to evaluate semantic similarity."""
        user_prompt = JUDGE_USER_TEMPLATE.format(
            context=self.task_context,
            expected=expected,
            actual=actual,
        )

        # Use temperature > 0 for multi-round to get variance
        temp = 0.3 if self.judge_rounds > 1 else 0.0

        response = completion(
            model=self.judge_model,
            messages=[
                {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temp,
            max_tokens=200,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        result = json.loads(content)

        score = float(result.get("score", 0.0))
        score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
        feedback = result.get("feedback", "No feedback")

        return score, feedback


# Module-specific evaluators
MODULE_EVALUATORS = {
    # ============ TEXT GENERATION MODULES ============
    "m09": {
        "output_key": "primary_use",
        "task_context": "Identify the primary intended use of a product in 3-6 words. Focus on WHAT the product does, not features or marketing language.",
    },
    "m10": {
        "output_key": "validated_use",
        "task_context": "Validate and clean a primary intended use phrase. Remove adjectives, features, technologies, and marketing language. Keep 3-6 words.",
    },
    "m01": {
        "output_key": "brand_entities",
        "task_context": "Extract brand name entities from product listing. Return list of brand variations found in the text.",
    },
    "m01a": {
        "output_key": "variations",
        "task_context": "Generate brand name variations (with/without spaces, typos, abbreviations). Return list of plausible variations.",
    },
    "m01b": {
        "output_key": "sub_brands",
        "task_context": "Extract sub-brands, searchable standards, and manufacturer from product listing.",
    },
    "m03": {
        "output_key": "competitor_entities",
        "task_context": "Generate competitor brand entities for the product category. Return list of competitor brand names.",
    },
    "m06": {
        "output_key": "taxonomy",
        "task_context": "Generate product type taxonomy hierarchy. Return structured list with levels and product types.",
    },
    "m07": {
        "output_key": "variants",
        "task_context": "Extract product attributes: variants, use cases, and audiences from product listing.",
    },
    "m08": {
        "output_key": "attribute_table",
        "task_context": "Assign ranks to product attributes based on importance and relevance.",
    },
    "m11": {
        "output_key": "hard_constraints",
        "task_context": "Identify hard constraints for the product (size requirements, compatibility limits, material restrictions). Return list of constraints.",
    },

    # ============ CLASSIFIER MODULES ============
    "m02": {
        "output_key": "branding_scope_1",
        "task_context": "Classify if keyword matches own brand. Output: 'OB' (Own Brand match) or null (no match). OB means keyword contains brand name or clear brand reference.",
    },
    "m02b": {
        "output_key": "branding_scope_1",
        "task_context": "Classify if keyword matches own brand. Output: 'OB' (Own Brand match) or null (no match). OB means keyword contains brand name or clear brand reference.",
    },
    "m04": {
        "output_key": "branding_scope_2",
        "task_context": "Classify if keyword matches competitor brand. Output: 'CB' (Competitor Brand) or null (no match). CB means keyword contains competitor brand name.",
    },
    "m04b": {
        "output_key": "branding_scope_2",
        "task_context": "Classify if keyword matches competitor brand. Output: 'CB' (Competitor Brand) or null (no match). CB means keyword contains competitor brand name.",
    },
    "m05": {
        "output_key": "branding_scope_3",
        "task_context": "Classify if keyword is non-branded (generic). Output: 'NB' (Non-Branded) or null. NB means keyword has no brand references, only product type/features.",
    },
    "m05b": {
        "output_key": "branding_scope_3",
        "task_context": "Classify if keyword is non-branded (generic). Output: 'NB' (Non-Branded) or null. NB means keyword has no brand references, only product type/features.",
    },
    "m12": {
        "output_key": "relevancy",
        "task_context": "Classify keyword relevancy after hard constraint check. Output: 'R' (Relevant), 'S' (Substitute), 'C' (Complementary), or 'N' (Not relevant/violates constraint).",
    },
    "m12b": {
        "output_key": "relevancy",
        "task_context": "Classify keyword relevancy to product. Output: 'R' (Relevant - same use), 'S' (Substitute - different product, same use), 'C' (Complementary - used together), or 'N' (Not relevant).",
    },
    "m13": {
        "output_key": "same_type",
        "task_context": "Check if keyword and product are same type. Output: 'true' (same product type) or 'false' (different types).",
    },
    "m14": {
        "output_key": "relevancy",
        "task_context": "Check if keyword has same primary use as product (same type path). Output: 'R' (Relevant - same primary use) or null (different use).",
    },
    "m15": {
        "output_key": "relevancy",
        "task_context": "Check if keyword is substitute (different type path). Output: 'S' (Substitute - can replace product) or null (not substitute).",
    },
    "m16": {
        "output_key": "relevancy",
        "task_context": "Check if keyword is complementary. Output: 'C' (Complementary - used together with product) or null (not complementary).",
    },
}


def get_evaluator(
    module_id: str,
    judge_model: str = "gpt-4o",
    judge_rounds: int = 1,
    judge_agg: str = "mean",
    hybrid_weight: float = 0.3,
) -> Evaluator:
    """Get pre-configured evaluator for a module.

    Evaluator selection based on module type:
    - M01, M01a, M01b, M11: ListEvaluator (F1 + constraints)
    - M06, M07, M08: StructuredEvaluator (rule-based + hybrid)
    - M12, M12B, M13, M14, M15, M16: ClassifierEvaluator (confusion matrix)
    - M09, M10, others: LLMJudgeEvaluator (semantic similarity)
    """
    module_id = module_id.lower()

    if module_id not in MODULE_EVALUATORS:
        raise ValueError(f"Unknown module: {module_id}. Available: {list(MODULE_EVALUATORS.keys())}")

    # List output modules (brand extraction, constraints)
    if module_id in {"m01", "m01a", "m01b", "m11"}:
        return ListEvaluator(
            module_id=module_id,
            judge_model=judge_model,
            judge_rounds=judge_rounds,
            judge_agg=judge_agg,
            hybrid_weight=hybrid_weight,
        )

    # Classifier modules (OB/CB/NB, R/S/C/N, true/false)
    if module_id in {"m02", "m02b", "m04", "m04b", "m05", "m05b", "m12", "m12b", "m13", "m14", "m15", "m16"}:
        return ClassifierEvaluator(
            module_id=module_id,
            judge_model=judge_model,
            judge_rounds=judge_rounds,
            judge_agg=judge_agg,
            hybrid_weight=hybrid_weight,
        )

    # Structured output modules (taxonomy, attributes)
    if module_id in {"m06", "m07", "m08"}:
        return StructuredEvaluator(
            module_id=module_id,
            judge_model=judge_model,
            judge_rounds=judge_rounds,
            judge_agg=judge_agg,
            hybrid_weight=hybrid_weight,
        )

    # Default: LLM-as-Judge for semantic comparison (M09, M10, M02, M03, etc.)
    config = MODULE_EVALUATORS[module_id]
    return LLMJudgeEvaluator(
        judge_model=judge_model,
        output_key=config["output_key"],
        task_context=config["task_context"],
        judge_rounds=judge_rounds,
        judge_agg=judge_agg,
    )


if __name__ == "__main__":
    # Quick test
    print("Available module evaluators:")
    for module_id, config in MODULE_EVALUATORS.items():
        print(f"  {module_id}: {config['output_key']}")

#!/usr/bin/env python3
"""
LLM Judge Analyzer - Option A

Uses LLM-as-Judge to evaluate errors and categorize them:
- model_error: Model made a genuine mistake
- ground_truth_issue: Dataset label is wrong/debatable
- edge_case: Ambiguous case, both answers reasonable
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
from openai import OpenAI

# Load API key
env_file = Path(".env")
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if line.startswith("OPENAI_API_KEY="):
            os.environ["OPENAI_API_KEY"] = line.split("=", 1)[1].strip().strip('"')


@dataclass
class JudgeResult:
    """Result from LLM Judge evaluation."""
    error_id: str
    category: str  # model_error, ground_truth_issue, edge_case
    score: int  # 0-100
    explanation: str
    recommendation: str  # keep_label, fix_label, review_needed


JUDGE_PROMPT_TEMPLATE = """You are an expert evaluator assessing classification errors in an Amazon keyword classification system.

## Context
- **Module:** {module}
- **Task:** {task_description}

## The Error Case
- **Keyword:** {keyword}
- **Expected Label:** {expected}
- **Model Output:** {actual}
- **Model's Reasoning:** {reasoning}

## Your Task
Evaluate whether this is:
1. **model_error** - The model genuinely made a mistake. The expected label is clearly correct.
2. **ground_truth_issue** - The dataset label appears wrong. The model's output seems more reasonable.
3. **edge_case** - This is ambiguous. Both the expected and actual labels could be justified.

## Evaluation Criteria
- Consider the keyword semantically
- Evaluate if the model's reasoning is sound
- Check if the expected label follows the classification rules
- Consider real-world Amazon shopper intent

## Output Format (JSON)
{{
  "category": "model_error" | "ground_truth_issue" | "edge_case",
  "score": 0-100,  // How confident are you in this categorization?
  "explanation": "Detailed explanation of your assessment",
  "recommendation": "keep_label" | "fix_label" | "review_needed"
}}
"""

TASK_DESCRIPTIONS = {
    "m02": "Classify if keyword contains own brand name/variation (OB) or not (null)",
    "m02b": "Classify if keyword contains own brand name/variation (OB) or not (null)",
    "m04": "Classify if keyword contains competitor brand (CB) or not (null)",
    "m04b": "Classify if keyword contains competitor brand (CB) or not (null)",
    "m05": "Classify if keyword is non-branded/generic (NB) or branded (null)",
    "m05b": "Classify if keyword is non-branded/generic (NB) or branded (null)",
    "m12": "Check if keyword violates a hard constraint for the product",
    "m12b": "Classify keyword relationship: R (Relevant), S (Substitute), C (Complementary), N (Negative)",
    "m13": "Check if keyword matches product type",
    "m14": "Check if keyword shares primary intended use with product",
    "m15": "Check if keyword product is a substitute",
    "m16": "Check if keyword product is complementary",
}


class LLMJudgeAnalyzer:
    """Analyze errors using LLM-as-Judge."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.client = OpenAI()
        self.model = model
        self.results: list[JudgeResult] = []

    def judge_error(self, module: str, error: dict) -> JudgeResult:
        """Judge a single error case."""
        prompt = JUDGE_PROMPT_TEMPLATE.format(
            module=module.upper(),
            task_description=TASK_DESCRIPTIONS.get(module, "Classification task"),
            keyword=error.get("keyword", str(error.get("input", ""))),
            expected=error.get("expected"),
            actual=error.get("actual"),
            reasoning=error.get("reasoning", "No reasoning provided")
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )

        result_json = json.loads(response.choices[0].message.content)

        result = JudgeResult(
            error_id=error.get("record_id", "unknown"),
            category=result_json.get("category", "unknown"),
            score=result_json.get("score", 0),
            explanation=result_json.get("explanation", ""),
            recommendation=result_json.get("recommendation", "review_needed")
        )

        self.results.append(result)
        return result

    def judge_errors_batch(self, module: str, errors: list[dict],
                           max_errors: int = 50) -> list[JudgeResult]:
        """Judge multiple errors."""
        results = []
        for i, error in enumerate(errors[:max_errors]):
            print(f"  Judging error {i+1}/{min(len(errors), max_errors)}...")
            result = self.judge_error(module, error)
            results.append(result)
        return results

    def get_summary(self) -> dict:
        """Get summary of judge results."""
        if not self.results:
            return {}

        categories = {"model_error": 0, "ground_truth_issue": 0, "edge_case": 0}
        recommendations = {"keep_label": 0, "fix_label": 0, "review_needed": 0}
        total_score = 0

        for r in self.results:
            categories[r.category] = categories.get(r.category, 0) + 1
            recommendations[r.recommendation] = recommendations.get(r.recommendation, 0) + 1
            total_score += r.score

        return {
            "total_judged": len(self.results),
            "categories": categories,
            "recommendations": recommendations,
            "avg_confidence": total_score / len(self.results) if self.results else 0
        }

    def export_results(self, output_file: str):
        """Export results to JSON."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.get_summary(),
            "results": [
                {
                    "error_id": r.error_id,
                    "category": r.category,
                    "score": r.score,
                    "explanation": r.explanation,
                    "recommendation": r.recommendation
                }
                for r in self.results
            ]
        }

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)


def main():
    """Example usage."""
    import argparse

    parser = argparse.ArgumentParser(description="LLM Judge error analysis")
    parser.add_argument("--errors-file", "-e", required=True, help="JSON file with errors")
    parser.add_argument("--module", "-m", required=True, help="Module name")
    parser.add_argument("--max-errors", "-n", type=int, default=20, help="Max errors to judge")
    parser.add_argument("--output", "-o", help="Output file for results")

    args = parser.parse_args()

    # Load errors
    with open(args.errors_file) as f:
        errors = json.load(f)

    print(f"Loaded {len(errors)} errors from {args.errors_file}")
    print(f"Judging up to {args.max_errors} errors for module {args.module}...")

    judge = LLMJudgeAnalyzer()
    results = judge.judge_errors_batch(args.module, errors, args.max_errors)

    summary = judge.get_summary()
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total judged: {summary['total_judged']}")
    print(f"Categories: {summary['categories']}")
    print(f"Recommendations: {summary['recommendations']}")
    print(f"Avg confidence: {summary['avg_confidence']:.1f}")

    if args.output:
        judge.export_results(args.output)
        print(f"\nResults exported to: {args.output}")


if __name__ == "__main__":
    main()

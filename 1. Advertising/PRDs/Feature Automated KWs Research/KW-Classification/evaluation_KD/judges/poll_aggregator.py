"""
PoLL Aggregator - Simple majority voting for binary Pass/Fail judgments.

Based on: https://arxiv.org/abs/2404.18796
- Majority vote for Pass/Fail labels
- Agreement tracking for quality control
"""

from collections import Counter
from typing import Any


class PoLLAggregator:
    """Aggregate binary Pass/Fail results from multiple LLM judges."""

    def aggregate(self, results: list[dict]) -> dict:
        """
        Aggregate judge results using majority voting.

        Args:
            results: List of judge results, each with {"label": "Pass"|"Fail", "reasoning": "..."}

        Returns:
            {
                "label": "Pass" | "Fail",
                "reasoning": str (from majority),
                "agreement": bool (all judges agreed),
                "poll_votes": {"Pass": n, "Fail": m},
                "poll_results": [...]
            }
        """
        if not results:
            return {
                "label": "Fail",
                "reasoning": "No results to aggregate",
                "error": True
            }

        # Filter out errors
        valid_results = [r for r in results if "error" not in r]
        if not valid_results:
            return {
                "label": "Fail",
                "reasoning": "All judges failed",
                "error": True,
                "poll_results": results
            }

        # Count votes
        pass_count = sum(1 for r in valid_results if r.get("label") == "Pass")
        fail_count = len(valid_results) - pass_count

        # Majority wins
        final_label = "Pass" if pass_count > fail_count else "Fail"

        # Get reasoning from majority side
        majority_results = [r for r in valid_results if r.get("label") == final_label]
        reasoning = majority_results[0].get("reasoning", "No reasoning provided") if majority_results else "No reasoning"

        # Calculate agreement
        total = len(valid_results)
        agreement = (pass_count == total) or (fail_count == total)
        agreement_rate = max(pass_count, fail_count) / total if total > 0 else 0

        return {
            "label": final_label,
            "reasoning": reasoning,
            "agreement": agreement,
            "agreement_rate": round(agreement_rate, 2),
            "poll_votes": {"Pass": pass_count, "Fail": fail_count},
            "poll_results": results,
            "needs_review": not agreement  # Flag for human review if judges disagreed
        }


def compute_inter_judge_agreement(batch_results: list[dict]) -> dict:
    """
    Compute inter-judge agreement statistics across a batch of evaluations.

    Args:
        batch_results: List of aggregated results from PoLLAggregator

    Returns:
        {
            "total_evaluations": int,
            "unanimous_count": int,
            "unanimous_rate": float,
            "split_decisions": int,
            "avg_agreement_rate": float
        }
    """
    if not batch_results:
        return {"error": "No results"}

    total = len(batch_results)
    unanimous = sum(1 for r in batch_results if r.get("agreement", False))
    agreement_rates = [r.get("agreement_rate", 0) for r in batch_results]

    return {
        "total_evaluations": total,
        "unanimous_count": unanimous,
        "unanimous_rate": round(unanimous / total, 3) if total > 0 else 0,
        "split_decisions": total - unanimous,
        "avg_agreement_rate": round(sum(agreement_rates) / len(agreement_rates), 3) if agreement_rates else 0
    }

"""
Aggregator - Runs multiple evaluation runs and aggregates results.

Responsibilities:
- Execute pipeline multiple times
- Calculate median scores
- Compute confidence based on variance
"""

import statistics
from typing import Any, Optional

from .orchestrator import Orchestrator


class Aggregator:
    """
    Runs multiple evaluation iterations and aggregates results.

    Default: 3 runs with median aggregation
    """

    CONFIDENCE_THRESHOLDS = {
        "high": 0.5,    # Variance <= 0.5
        "medium": 1.0,  # Variance <= 1.0
    }

    def __init__(
        self,
        orchestrator: Optional[Orchestrator] = None,
        num_runs: int = 3,
        verbose: bool = False,
        model: Optional[str] = None,
    ):
        """
        Initialize the aggregator.

        Args:
            orchestrator: Orchestrator instance (creates new one if None)
            num_runs: Number of evaluation runs to aggregate
            verbose: Enable verbose logging
            model: Override model for orchestrator
        """
        self.num_runs = num_runs
        self.verbose = verbose

        if orchestrator:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = Orchestrator(model=model, verbose=verbose)

    def evaluate(
        self,
        module_id: str,
        input_data: Any,
        output_data: Any,
        expected_data: Any = None,
        context: str = "",
        skip_filter: bool = False,
    ) -> dict:
        """
        Run multiple evaluations and aggregate results.

        Args:
            module_id: Module identifier
            input_data: Input data
            output_data: Module output
            expected_data: Expected output
            context: Additional context
            skip_filter: Skip input validation

        Returns:
            Aggregated evaluation result
        """
        all_runs = []
        errors = []

        if self.verbose:
            print(f"[Aggregator] Starting {self.num_runs} evaluation runs...")

        for run_num in range(self.num_runs):
            if self.verbose:
                print(f"\n[Aggregator] === Run {run_num + 1}/{self.num_runs} ===")

            try:
                result = self.orchestrator.evaluate(
                    module_id=module_id,
                    input_data=input_data,
                    output_data=output_data,
                    expected_data=expected_data,
                    context=context,
                    skip_filter=skip_filter if run_num == 0 else True,  # Only filter on first run
                )

                if result.get("error") or result.get("rejected"):
                    errors.append(result)
                else:
                    all_runs.append(result)

            except Exception as e:
                errors.append({
                    "error": True,
                    "error_message": str(e),
                    "run": run_num + 1,
                })

        # If all runs failed, return error
        if not all_runs:
            return {
                "overall": 0,
                "scores": {},
                "summary": "All evaluation runs failed",
                "confidence": "NONE",
                "runs_completed": 0,
                "errors": errors,
            }

        # Aggregate results
        return self._aggregate_results(all_runs, errors)

    def _aggregate_results(self, runs: list, errors: list) -> dict:
        """
        Aggregate multiple run results using median.

        Args:
            runs: List of successful run results
            errors: List of failed runs

        Returns:
            Aggregated result
        """
        # Collect all scores by criterion
        criteria = ["accuracy", "relevance", "completeness", "clarity", "reasoning"]
        score_lists = {c: [] for c in criteria}
        overall_scores = []

        for run in runs:
            overall_scores.append(run.get("overall", 0))
            scores = run.get("scores", {})
            for c in criteria:
                if c in scores:
                    score_lists[c].append(scores[c])

        # Calculate medians
        aggregated_scores = {}
        variances = {}

        for c in criteria:
            if score_lists[c]:
                aggregated_scores[c] = int(statistics.median(score_lists[c]))
                variances[c] = statistics.variance(score_lists[c]) if len(score_lists[c]) > 1 else 0
            else:
                aggregated_scores[c] = 0
                variances[c] = 0

        # Calculate overall median
        if overall_scores:
            overall = round(statistics.median(overall_scores), 1)
            overall_variance = statistics.variance(overall_scores) if len(overall_scores) > 1 else 0
        else:
            overall = 0
            overall_variance = 0

        # Determine confidence
        avg_variance = statistics.mean(variances.values()) if variances else 0
        confidence = self._calculate_confidence(avg_variance)

        # Aggregate debate summary
        debate_summary = self._aggregate_debate(runs)

        # Get the full debate from the first run (for display purposes)
        first_run_debate = runs[0].get("debate", {}) if runs else {}

        # Collect all summaries
        summaries = [r.get("summary", "") for r in runs if r.get("summary")]

        # Collect other fields from first run for display
        first_run = runs[0] if runs else {}

        return {
            "overall": overall,
            "scores": aggregated_scores,
            "summary": summaries[0] if summaries else "No summary available",
            "confidence": confidence,
            "runs_completed": len(runs),
            "runs_failed": len(errors),
            "debate": first_run_debate,  # Full debate from first run
            "debate_summary": debate_summary,
            "judge_debate_summary": first_run.get("judge_debate_summary", {}),
            "point_judgments": first_run.get("point_judgments", []),
            "justifications": first_run.get("justifications", {}),
            "meta_judge": first_run.get("meta_judge", {}),
            "aggregation_details": {
                "variances": variances,
                "overall_variance": overall_variance,
                "all_overalls": overall_scores,
            },
            "individual_runs": self._sanitize_runs(runs) if self.verbose else None,
            "errors": errors if errors else None,
        }

    def _sanitize_runs(self, runs: list) -> list:
        """
        Create sanitized copies of runs for JSON serialization.

        Removes any keys that might cause circular references.
        """
        import copy

        sanitized = []
        for run in runs:
            try:
                # Deep copy to avoid modifying original
                run_copy = copy.deepcopy(run)
                # Remove internal keys that might cause issues
                run_copy.pop("_critic_output", None)
                run_copy.pop("_defender_output", None)
                run_copy.pop("_judge_output", None)
                sanitized.append(run_copy)
            except Exception:
                # If deep copy fails, create a minimal summary
                sanitized.append({
                    "overall": run.get("overall", 0),
                    "scores": run.get("scores", {}),
                    "summary": run.get("summary", ""),
                    "copy_error": True,
                })
        return sanitized

    def _calculate_confidence(self, variance: float) -> str:
        """
        Calculate confidence level based on variance.

        Returns:
            "HIGH", "MEDIUM", or "LOW"
        """
        if variance <= self.CONFIDENCE_THRESHOLDS["high"]:
            return "HIGH"
        elif variance <= self.CONFIDENCE_THRESHOLDS["medium"]:
            return "MEDIUM"
        else:
            return "LOW"

    def _aggregate_debate(self, runs: list) -> dict:
        """
        Aggregate debate statistics across runs.

        Returns:
            Summary of debate across all runs
        """
        total_weaknesses = []
        total_valid = []
        total_retries = 0

        for run in runs:
            debate = run.get("debate", {})
            total_weaknesses.append(debate.get("weaknesses_found", 0))
            total_valid.append(debate.get("weaknesses_valid", 0))

            retry_info = run.get("retry_info", {})
            total_retries += retry_info.get("total_attempts", 1) - 1

        return {
            "weaknesses_found": round(statistics.mean(total_weaknesses)) if total_weaknesses else 0,
            "weaknesses_valid": round(statistics.mean(total_valid)) if total_valid else 0,
            "retries": total_retries,
        }


class SingleRunEvaluator:
    """
    Convenience class for single-run evaluation (development/testing).

    Skips aggregation and meta-judge for faster, cheaper evaluation.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        verbose: bool = False,
    ):
        self.orchestrator = Orchestrator(model=model, verbose=verbose)

    def evaluate(
        self,
        module_id: str,
        input_data: Any,
        output_data: Any,
        expected_data: Any = None,
        context: str = "",
    ) -> dict:
        """Run a single evaluation without aggregation."""
        return self.orchestrator.evaluate(
            module_id=module_id,
            input_data=input_data,
            output_data=output_data,
            expected_data=expected_data,
            context=context,
            single_run=True,
        )

"""
Orchestrator - Coordinates the full multi-agent evaluation pipeline.

Pipeline: InputFilter -> Critic -> Defender -> Judge -> MetaJudge -> [Retry?]
"""

import time
from typing import Any, Optional
from pathlib import Path

import yaml

from ..agents import (
    InputFilter,
    CriticAgent,
    DefenderAgent,
    JudgeAgent,
    MetaJudge,
)
from .retry_handler import RetryHandler


class Orchestrator:
    """
    Coordinates the full adversarial debate evaluation pipeline.

    Pipeline flow:
    1. InputFilter: Validate input, detect injection
    2. CriticAgent: Find weaknesses in output
    3. DefenderAgent: Rebut weaknesses
    4. JudgeAgent: Score on 0-5 Likert scale
    5. MetaJudge: Check for sycophancy
    6. Retry if sycophantic (up to max_retries)
    """

    def __init__(
        self,
        model: Optional[str] = None,
        verbose: bool = False,
        max_retries: int = 2,
    ):
        """
        Initialize the orchestrator.

        Args:
            model: Override model for all agents (uses config defaults if None)
            verbose: Enable verbose logging
            max_retries: Maximum retry attempts if sycophantic
        """
        self.verbose = verbose
        self.model = model

        # Initialize agents
        self.input_filter = InputFilter(verbose=verbose)
        self.critic = CriticAgent(model=model, verbose=verbose)
        self.defender = DefenderAgent(model=model, verbose=verbose)
        self.judge = JudgeAgent(model=model, verbose=verbose)
        self.meta_judge = MetaJudge(model=model, verbose=verbose)

        # Initialize retry handler
        self.retry_handler = RetryHandler(max_retries=max_retries)

        # Load config
        config_path = Path(__file__).parent.parent / "config" / "agent_config.yaml"
        if config_path.exists():
            with open(config_path) as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}

    def evaluate(
        self,
        module_id: str,
        input_data: Any,
        output_data: Any,
        expected_data: Any = None,
        context: str = "",
        skip_filter: bool = False,
        single_run: bool = False,
    ) -> dict:
        """
        Run the full evaluation pipeline.

        Args:
            module_id: Module identifier (e.g., "M01")
            input_data: Input that was given to the module
            output_data: Module's output to evaluate
            expected_data: Expected/ground truth output
            context: Additional context for evaluation
            skip_filter: Skip input validation (for trusted inputs)
            single_run: Skip retry logic (for development/cost saving)

        Returns:
            Evaluation result with scores, debate transcript, and metadata
        """
        start_time = time.time()
        self.retry_handler.reset()

        # Step 0: Input validation
        if not skip_filter:
            filter_result = self._run_input_filter(input_data, output_data, expected_data)
            if not filter_result["is_valid"]:
                return self._build_rejection_result(filter_result, start_time)
        else:
            filter_result = {"is_valid": True, "skipped": True}

        # Run evaluation with retry logic
        while True:
            result = self._run_single_evaluation(
                module_id=module_id,
                input_data=input_data,
                output_data=output_data,
                expected_data=expected_data,
                context=context,
            )

            if single_run:
                # Skip meta-judge and retry in single-run mode
                result["meta_judge_skipped"] = True
                break

            # Step 5: Meta-judge for sycophancy check
            meta_result = self._run_meta_judge(
                result=result,
                critic_output=result.get("_critic_output"),
                defender_output=result.get("_defender_output"),
                judge_output=result.get("_judge_output"),
            )
            result["meta_judge"] = meta_result

            # Remove internal outputs after meta-judge processing
            result.pop("_critic_output", None)
            result.pop("_defender_output", None)
            result.pop("_judge_output", None)

            # Record attempt
            was_successful = not meta_result.get("is_sycophantic", False)
            self.retry_handler.record_attempt(result, meta_result, was_successful)

            # Check if we should retry
            if self.retry_handler.should_retry(meta_result):
                if self.verbose:
                    print(f"[Orchestrator] Sycophancy detected, retrying ({self.retry_handler.attempts + 1}/{self.retry_handler.max_retries})")
                self.retry_handler.wait()
                continue
            else:
                break

        # Finalize result
        result["filter_result"] = filter_result
        result["retry_info"] = self.retry_handler.get_summary()
        result["elapsed_time"] = time.time() - start_time
        result["module_id"] = module_id

        # Remove internal outputs before returning (prevent circular references)
        result.pop("_critic_output", None)
        result.pop("_defender_output", None)
        result.pop("_judge_output", None)

        return result

    def _run_input_filter(
        self,
        input_data: Any,
        output_data: Any,
        expected_data: Any,
    ) -> dict:
        """Run input validation."""
        if self.verbose:
            print("[Orchestrator] Running input filter...")

        return self.input_filter.execute(
            input_data=input_data,
            output_data=output_data,
            expected_data=expected_data,
        )

    def _run_single_evaluation(
        self,
        module_id: str,
        input_data: Any,
        output_data: Any,
        expected_data: Any,
        context: str,
        critic_retry_count: int = 0,
    ) -> dict:
        """Run a single evaluation iteration (critic -> defender -> judge)."""

        # Step 1: Critic finds weaknesses (with retry if < 3 found)
        max_critic_retries = 2
        min_weaknesses = 3

        if self.verbose:
            print("[Orchestrator] Running critic agent...")

        critic_result = self.critic.execute(
            module_id=module_id,
            input_data=input_data,
            output_data=output_data,
            expected_data=expected_data,
            context=context,
        )

        if critic_result.get("error"):
            return self._build_error_result("Critic", critic_result)

        weaknesses = critic_result.get("weaknesses", [])

        # Retry if Critic found fewer than minimum weaknesses
        if len(weaknesses) < min_weaknesses and critic_retry_count < max_critic_retries:
            if self.verbose:
                print(f"[Orchestrator] Critic found only {len(weaknesses)} weaknesses (min: {min_weaknesses}), retrying ({critic_retry_count + 1}/{max_critic_retries})...")
            return self._run_single_evaluation(
                module_id=module_id,
                input_data=input_data,
                output_data=output_data,
                expected_data=expected_data,
                context=context,
                critic_retry_count=critic_retry_count + 1,
            )

        # Log if still below minimum after retries
        if len(weaknesses) < min_weaknesses and self.verbose:
            print(f"[Orchestrator] WARNING: Critic found only {len(weaknesses)} weaknesses after {max_critic_retries} retries")

        # Step 2: Defender rebuts weaknesses
        if self.verbose:
            print("[Orchestrator] Running defender agent...")

        defender_result = self.defender.execute(
            module_id=module_id,
            input_data=input_data,
            output_data=output_data,
            expected_data=expected_data,
            weaknesses=weaknesses,
            context=context,
        )

        if defender_result.get("error"):
            return self._build_error_result("Defender", defender_result)

        defenses = defender_result.get("defenses", [])
        rebuttals = defenses  # Backward compatibility alias

        # Step 3: Judge evaluates the debate and scores the output
        if self.verbose:
            print("[Orchestrator] Running judge agent...")

        judge_result = self.judge.execute(
            module_id=module_id,
            input_data=input_data,
            output_data=output_data,
            expected_data=expected_data,
            weaknesses=weaknesses,
            rebuttals=rebuttals,
            critic_output=critic_result,  # Full critic output for pairwise evaluation
            defender_output=defender_result,  # Full defender output for pairwise evaluation
            context=context,
        )

        if judge_result.get("error"):
            return self._build_error_result("Judge", judge_result)

        # Build result with full critic, defender, and judge output
        return {
            # Judge final output
            "overall": judge_result.get("final_score", judge_result.get("overall", 0)),
            "final_score": judge_result.get("final_score", 0),
            "dimension_average": judge_result.get("dimension_average", 0),
            "debate_adjustment": judge_result.get("debate_adjustment", 0),
            "scores": judge_result.get("scores", {}),
            "rubric_scores": judge_result.get("rubric_scores", {}),
            "justifications": judge_result.get("justifications", {}),
            "summary": judge_result.get("summary", ""),
            # Judge pairwise evaluation
            "point_judgments": judge_result.get("point_judgments", []),
            "judge_debate_summary": judge_result.get("debate_summary", {}),
            # Full debate transcript
            "debate": {
                # Critic output (Agent A)
                "chain_of_thought": critic_result.get("chain_of_thought", ""),
                "weaknesses": weaknesses,
                "strengths": critic_result.get("strengths", []),
                "initial_score": critic_result.get("initial_score", 0),
                "overall_assessment": critic_result.get("overall_assessment", ""),
                # Defender output (Agent B)
                "defenses": defenses,
                "rebuttals": rebuttals,  # Backward compatibility
                "overall_argument": defender_result.get("overall_argument", ""),
                # Summary stats
                "weaknesses_found": len(weaknesses),
                "weaknesses_accepted": defender_result.get("weaknesses_accepted", 0),
                "weaknesses_partially_accepted": defender_result.get("weaknesses_partially_accepted", 0),
                "weaknesses_rejected": defender_result.get("weaknesses_rejected", 0),
                "weaknesses_valid": defender_result.get("weaknesses_accepted", 0),  # Backward compat
                "strength_count": critic_result.get("strength_count", 0),
                "avg_severity": critic_result.get("avg_severity", 0),
            },
            "agent_meta": {
                "critic": critic_result.get("_meta", {}),
                "defender": defender_result.get("_meta", {}),
                "judge": judge_result.get("_meta", {}),
            },
            # Full agent outputs for meta-judge
            "_critic_output": critic_result,
            "_defender_output": defender_result,
            "_judge_output": judge_result,
        }

    def _run_meta_judge(
        self,
        result: dict,
        critic_output: dict = None,
        defender_output: dict = None,
        judge_output: dict = None,
    ) -> dict:
        """Run meta-judge for sycophancy detection.

        Args:
            result: The evaluation result dict
            critic_output: Full critic agent output
            defender_output: Full defender agent output
            judge_output: Full judge agent output
        """
        if self.verbose:
            print("[Orchestrator] Running meta-judge...")

        # Quick heuristic check first
        quick_check = self.meta_judge.quick_check(
            scores=result.get("scores", {}),
            justifications=result.get("justifications", {}),
            weaknesses_count=result.get("debate", {}).get("weaknesses_found", 0),
            weaknesses_valid=result.get("debate", {}).get("weaknesses_valid", 0),
            point_judgments=result.get("point_judgments", []),
            judge_debate_summary=result.get("judge_debate_summary", {}),
        )

        # If quick check doesn't trigger, accept without full meta-judge call
        if not quick_check["likely_sycophantic"]:
            return {
                "is_sycophantic": False,
                "judgment_quality": quick_check.get("estimated_quality", 4),
                "confidence": quick_check.get("estimated_confidence", 0.8),
                "should_retry": False,
                "recommendation": "accept",
                "quick_check": quick_check,
                "full_check_skipped": True,
            }

        # Run full meta-judge evaluation with all agent outputs
        meta_result = self.meta_judge.execute(
            critic_output=critic_output or {},
            defender_output=defender_output or {},
            judge_output=judge_output or {},
            # Legacy parameters for backward compatibility
            scores=result.get("scores", {}),
            justifications=result.get("justifications", {}),
            weaknesses=result.get("debate", {}).get("weaknesses", []),
            rebuttals=result.get("debate", {}).get("rebuttals", []),
            summary=result.get("summary", ""),
        )

        meta_result["quick_check"] = quick_check
        return meta_result

    def _build_rejection_result(self, filter_result: dict, start_time: float) -> dict:
        """Build result for rejected input."""
        return {
            "overall": 0,
            "scores": {},
            "summary": f"Input rejected: {filter_result.get('rejection_reason', 'Unknown reason')}",
            "filter_result": filter_result,
            "rejected": True,
            "elapsed_time": time.time() - start_time,
        }

    def _build_error_result(self, agent_name: str, error_result: dict) -> dict:
        """Build result for agent error."""
        return {
            "overall": 0,
            "scores": {},
            "summary": f"Error in {agent_name}: {error_result.get('error_message', 'Unknown error')}",
            "error": True,
            "error_agent": agent_name,
            "error_details": error_result,
        }

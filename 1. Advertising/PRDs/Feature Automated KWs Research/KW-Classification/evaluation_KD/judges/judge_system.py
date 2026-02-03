"""
Judge System - Binary Pass/Fail evaluation with reasoning-first structure.

Based on LLM Evals course best practices:
- Binary labels only (Pass/Fail)
- Reasoning-first (CoT before label)
- Narrow failure modes (split instead of weight)
- Few-shot hard examples
"""

import json
from typing import Any, Optional
from pathlib import Path

import openai
from dotenv import load_dotenv

from .rubric_loader import RubricLoader

load_dotenv()


class JudgeSystem:
    """
    LLM-as-a-Judge evaluation system using binary Pass/Fail rubrics.

    Usage:
        judge = JudgeSystem()
        result = judge.evaluate("M02_correct_classification", output, expected, input_data)
    """

    def __init__(
        self,
        rubric_config: str = None,
        use_poll: bool = True,
        verbose: bool = False
    ):
        self.loader = RubricLoader(rubric_config)
        self.use_poll = use_poll
        self.verbose = verbose
        self.client = openai.OpenAI()

    def evaluate(
        self,
        rubric_id: str,
        module_output: dict,
        expected_output: dict,
        input_data: dict
    ) -> dict:
        """
        Evaluate a module's output using a specific binary rubric.

        Args:
            rubric_id: Rubric identifier (e.g., "M02_correct_classification")
            module_output: The actual output from the module
            expected_output: Ground truth / expected output
            input_data: Input that was given to the module

        Returns:
            {
                "rubric_id": str,
                "label": "Pass" | "Fail",
                "reasoning": str,
                "judge_model": str
            }
        """
        rubric = self.loader.get_rubric(rubric_id)
        if not rubric:
            return {
                "rubric_id": rubric_id,
                "label": "Fail",
                "reasoning": f"Rubric '{rubric_id}' not found",
                "error": True
            }

        prompt = self._build_judge_prompt(
            rubric=rubric,
            module_output=module_output,
            expected_output=expected_output,
            input_data=input_data
        )

        if self.use_poll:
            result = self._run_poll_evaluation(prompt, rubric_id)
        else:
            result = self._run_single_judge(prompt, "gpt-4o-mini")

        result["rubric_id"] = rubric_id
        result["module"] = rubric.get("module", "unknown")
        result["criterion"] = rubric.get("criterion", "unknown")

        return result

    def _build_judge_prompt(
        self,
        rubric: dict,
        module_output: dict,
        expected_output: dict,
        input_data: dict
    ) -> str:
        """Build the judge prompt with reasoning-first structure."""

        # Format examples
        examples_text = ""
        if rubric.get("examples"):
            examples_text = "\n## EXAMPLES\n"
            for i, ex in enumerate(rubric["examples"], 1):
                examples_text += f"""
### Example {i}
Input: {json.dumps(ex.get('input', {}), indent=2)}
Output: {json.dumps(ex.get('output', {}), indent=2)}
Label: {ex.get('label', 'N/A')}
Reasoning: {ex.get('reasoning', 'N/A')}
"""

        prompt = f"""You are an expert evaluator. Your job is to determine if the module output PASSES or FAILS based on one specific criterion.

## CRITERION: {rubric.get('criterion', 'Unknown')}

## CHECK
{rubric.get('check', rubric.get('task', 'Evaluate the output'))}

## FAIL DEFINITION (output FAILS if ANY of these are true)
{rubric.get('fail_definition', 'No fail definition provided')}

## PASS DEFINITION (output PASSES if ALL of these are true)
{rubric.get('pass_definition', 'No pass definition provided')}
{examples_text}
---

## INPUT DATA
```json
{json.dumps(input_data, indent=2, default=str)}
```

## MODULE OUTPUT (Evaluate This)
```json
{json.dumps(module_output, indent=2, default=str)}
```

## EXPECTED OUTPUT (Ground Truth)
```json
{json.dumps(expected_output, indent=2, default=str)}
```

---

## YOUR RESPONSE

IMPORTANT: You MUST provide your reasoning FIRST, then your label.

Return ONLY this JSON (no other text):
{{
  "reasoning": "<explain your evaluation - what did you check, what did you find>",
  "label": "Pass" or "Fail"
}}"""

        return prompt

    def _run_single_judge(self, prompt: str, model: str) -> dict:
        """Run evaluation with a single judge model."""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            result = json.loads(response.choices[0].message.content)
            result["judge_model"] = model

            # Normalize label
            if "label" in result:
                result["label"] = "Pass" if result["label"].lower() == "pass" else "Fail"

            return result
        except Exception as e:
            return {
                "error": str(e),
                "judge_model": model,
                "label": "Fail",
                "reasoning": f"Judge error: {str(e)}"
            }

    def _run_poll_evaluation(self, prompt: str, rubric_id: str) -> dict:
        """Run PoLL evaluation with 3 diverse judges, using majority vote."""
        panel = self.loader.get_poll_panel()
        results = []

        for judge_config in panel:
            model = judge_config["model"]
            if self.verbose:
                print(f"  Running judge: {model}")

            result = self._run_single_judge(prompt, model)
            results.append(result)

        # Majority vote for binary Pass/Fail
        pass_count = sum(1 for r in results if r.get("label") == "Pass")
        fail_count = sum(1 for r in results if r.get("label") == "Fail")

        final_label = "Pass" if pass_count > fail_count else "Fail"

        # Collect reasoning from all judges
        reasonings = [r.get("reasoning", "") for r in results if r.get("reasoning")]

        return {
            "label": final_label,
            "reasoning": reasonings[0] if reasonings else "No reasoning provided",
            "poll_votes": {"Pass": pass_count, "Fail": fail_count},
            "poll_results": results,
            "agreement": pass_count == 3 or fail_count == 3
        }

    def evaluate_module(
        self,
        module_id: str,
        module_output: dict,
        expected_output: dict,
        input_data: dict
    ) -> dict:
        """
        Evaluate ALL rubrics for a specific module.

        Args:
            module_id: Module identifier (e.g., "M02")
            module_output: The actual output from the module
            expected_output: Ground truth
            input_data: Input data

        Returns:
            {
                "module_id": str,
                "passed": bool (all rubrics passed),
                "rubric_results": [...],
                "pass_count": int,
                "fail_count": int,
                "failed_criteria": [...]
            }
        """
        rubric_ids = self.loader.get_rubrics_for_module(module_id)

        results = []
        failed_criteria = []

        for rubric_id in rubric_ids:
            if self.verbose:
                print(f"Evaluating {rubric_id}...")

            result = self.evaluate(
                rubric_id=rubric_id,
                module_output=module_output,
                expected_output=expected_output,
                input_data=input_data
            )
            results.append(result)

            if result.get("label") == "Fail":
                failed_criteria.append({
                    "rubric_id": rubric_id,
                    "criterion": result.get("criterion"),
                    "reasoning": result.get("reasoning")
                })

        pass_count = sum(1 for r in results if r.get("label") == "Pass")
        fail_count = len(results) - pass_count

        return {
            "module_id": module_id,
            "passed": fail_count == 0,
            "rubric_results": results,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "failed_criteria": failed_criteria
        }

    def evaluate_batch(
        self,
        module_id: str,
        test_cases: list[dict]
    ) -> dict:
        """
        Evaluate a batch of test cases for a module.

        Args:
            module_id: Module identifier
            test_cases: List of {"input": ..., "output": ..., "expected": ...}

        Returns:
            Batch results with summary statistics
        """
        results = []
        passed = 0
        failed = 0

        for i, case in enumerate(test_cases):
            if self.verbose:
                print(f"Evaluating case {i+1}/{len(test_cases)}...")

            result = self.evaluate_module(
                module_id=module_id,
                module_output=case["output"],
                expected_output=case["expected"],
                input_data=case["input"]
            )
            results.append(result)

            if result.get("passed", False):
                passed += 1
            else:
                failed += 1

        # Aggregate failure reasons
        failure_buckets = {}
        for r in results:
            for fc in r.get("failed_criteria", []):
                criterion = fc.get("criterion", "unknown")
                failure_buckets[criterion] = failure_buckets.get(criterion, 0) + 1

        return {
            "module_id": module_id,
            "total": len(test_cases),
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / len(test_cases) if test_cases else 0,
            "failure_buckets": failure_buckets,
            "results": results
        }

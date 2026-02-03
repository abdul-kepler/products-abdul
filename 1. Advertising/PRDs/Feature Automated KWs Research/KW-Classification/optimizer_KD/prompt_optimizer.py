"""
Prompt Optimization Agent for KW-Classification Pipeline
=========================================================

This module provides iterative prompt optimization using:
1. Local evaluation (no E2B sandbox)
2. LLM-as-a-judge scoring with existing Braintrust scorers
3. Failure analysis and suggestion generation
4. Reasoning model (o3-mini) for prompt rewriting

Usage:
    from optimizer.prompt_optimizer import PromptOptimizer

    optimizer = PromptOptimizer(module="m02")
    result = optimizer.optimize(
        prompt_path="prompts/modules/m02_own_brand.md",
        dataset_path="datasets/m02_dataset.jsonl",
        max_iterations=3,
        target_accuracy=0.85
    )
"""

import json
import os
import re
import difflib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field

import openai
from dotenv import load_dotenv

# Load environment
load_dotenv()


@dataclass
class IterationResult:
    """Result of a single optimization iteration."""
    iteration: int
    accuracy: float
    pass_rate: float
    prompt_text: str
    prompt_length: int
    prompt_diff: Optional[str]
    test_results: List[Dict[str, Any]]
    aggregate_scores: Dict[str, float]
    failures: List[Dict[str, Any]]
    improvements: List[Dict[str, Any]]
    improvements_applied: List[Dict[str, Any]]
    timestamp: str


@dataclass
class OptimizationResult:
    """Final result of prompt optimization."""
    success: bool
    best_iteration: int
    total_iterations: int
    original_prompt: str
    improved_prompt: str
    original_accuracy: float
    best_accuracy: float
    iteration_results: List[IterationResult]
    scorers_used: List[str]
    criteria_with_rubrics: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class PromptOptimizer:
    """
    Iterative prompt optimizer using LLM-as-a-judge evaluation.

    Flow:
    1. Load prompt and dataset
    2. Run classification on all test cases
    3. Score each result with LLM judges
    4. Analyze failures by rule
    5. Generate improvement suggestions (GPT-4o)
    6. Rewrite prompt (o3-mini reasoning model)
    7. Repeat until target accuracy or max iterations
    """

    def __init__(
        self,
        module: str = "m02",
        model: str = "gpt-4o",
        judge_model: str = "gpt-4o",
        optimizer_model: str = "o3-mini",
        temperature: float = 0.0,
        verbose: bool = True
    ):
        self.module = module
        self.model = model
        self.judge_model = judge_model
        self.optimizer_model = optimizer_model
        self.temperature = temperature
        self.verbose = verbose
        self.client = openai.OpenAI()

        # Project paths
        self.project_root = Path(__file__).parent.parent
        self.prompts_dir = self.project_root / "prompts"
        self.datasets_dir = self.project_root / "datasets"
        self.results_dir = self.project_root / "experiment_results"

    def log(self, message: str):
        """Print message if verbose mode enabled."""
        if self.verbose:
            print(message)

    def load_prompt(self, prompt_path: str) -> str:
        """Load prompt from file."""
        path = Path(prompt_path)
        if not path.is_absolute():
            path = self.project_root / prompt_path
        return path.read_text()

    def load_dataset(self, dataset_path: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load dataset from JSONL file."""
        path = Path(dataset_path)
        if not path.is_absolute():
            path = self.project_root / dataset_path

        dataset = []
        with open(path) as f:
            for line in f:
                if line.strip():
                    dataset.append(json.loads(line))
                    if limit and len(dataset) >= limit:
                        break
        return dataset

    def format_prompt(self, prompt_template: str, input_data: Dict[str, Any]) -> str:
        """Format prompt template with input variables."""
        result = prompt_template
        for key, value in input_data.items():
            # Handle both {{key}} and {key} placeholders
            result = result.replace(f"{{{{{key}}}}}", str(value))
            result = result.replace(f"{{{key}}}", str(value))
        return result

    def run_classification(
        self,
        prompt_text: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run classification on a single test case."""
        formatted_prompt = self.format_prompt(prompt_text, input_data)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": formatted_prompt}],
                response_format={"type": "json_object"},
                temperature=self.temperature
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": str(e), "classification": "ERROR"}

    def extract_criteria_with_rubrics(self, prompt_text: str) -> List[Dict[str, Any]]:
        """Extract evaluation criteria with multi-dimensional rubrics from the prompt using LLM."""
        extraction_prompt = f"""Analyze this classification prompt and extract evaluation CRITERIA with MULTI-DIMENSIONAL RUBRICS.

PROMPT:
{prompt_text[:4000]}

For EACH criterion, create a proper RUBRIC with MULTIPLE DIMENSIONS.
Each dimension should have detailed level descriptors for scores 1.0, 0.5, and 0.0.

Return JSON:
{{
  "criteria": [
    {{
      "criterion_id": "ob_exact_match",
      "criterion_type": "OB",
      "name": "Exact Brand Match Detection",
      "description": "Evaluates if the model correctly identifies exact brand name matches from the variations list",
      "dimensions": [
        {{
          "dimension_id": "classification_accuracy",
          "name": "Classification Accuracy",
          "weight": 0.4,
          "levels": {{
            "1.0": "Classification (OB/null) exactly matches the expected output for this keyword",
            "0.5": "Classification direction is correct but confidence is miscalibrated",
            "0.0": "Classification is incorrect - either false positive (claimed OB when should be null) or false negative (claimed null when should be OB)"
          }}
        }},
        {{
          "dimension_id": "evidence_quality",
          "name": "Evidence Quality",
          "weight": 0.3,
          "levels": {{
            "1.0": "Cites the exact matching term from variations_own and explains the match clearly",
            "0.5": "Mentions a match but doesn't cite the specific term or is vague about which variation matched",
            "0.0": "No evidence provided, or cites wrong/non-existent terms"
          }}
        }},
        {{
          "dimension_id": "reasoning_quality",
          "name": "Reasoning Quality",
          "weight": 0.3,
          "levels": {{
            "1.0": "Clear step-by-step reasoning showing character-by-character or substring verification",
            "0.5": "Reasoning present but skips verification steps or makes unsupported claims",
            "0.0": "No reasoning, circular logic, or reasoning contradicts the classification"
          }}
        }}
      ],
      "examples": {{
        "score_1.0": "keyword 'jbl headphones' → OB, matched_term='jbl', reasoning shows 'j-b-l' matches 'JBL' in variations",
        "score_0.5": "keyword 'jbl headphones' → OB, but reasoning just says 'contains brand' without showing the match",
        "score_0.0": "keyword 'jbl headphones' → null, despite 'JBL' being in variations_own"
      }}
    }},
    ...
  ]
}}

Extract 5-8 key criteria. For EACH criterion include 2-4 evaluation dimensions from:
- classification_accuracy: Did it get the right answer?
- evidence_quality: Did it cite specific terms/matches?
- reasoning_quality: Is the chain-of-thought logical and complete?
- boundary_handling: Did it correctly handle word boundaries and partial matches?
- confidence_calibration: Is the confidence score appropriate for the certainty level?

Be specific and observable in each level descriptor."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": extraction_prompt}],
                response_format={"type": "json_object"},
                temperature=0
            )
            result = json.loads(response.choices[0].message.content)
            return result.get("criteria", [])
        except Exception as e:
            self.log(f"  [WARN] Criteria extraction failed: {e}")
            return []

    def generate_judges(self, criteria: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate LLM-as-a-judge evaluators from extracted criteria with multi-dimensional rubrics."""
        judges = []
        for criterion in criteria:
            judge = {
                "name": criterion.get("criterion_id", criterion.get("name", "unknown")),
                "criterion_type": criterion.get("criterion_type", "GENERAL"),
                "description": criterion.get("description", ""),
                "dimensions": criterion.get("dimensions", []),
                "examples": criterion.get("examples", {}),
                "judge_prompt": self._build_rubric_judge_prompt(criterion)
            }
            judges.append(judge)
        return judges

    def _build_rubric_judge_prompt(self, criterion: Dict[str, Any]) -> str:
        """Build a judge prompt with multi-dimensional rubric for a specific criterion."""
        dimensions = criterion.get("dimensions", [])
        examples = criterion.get("examples", {})

        # Build dimensions rubric text
        dimensions_text = ""
        if dimensions:
            for dim in dimensions:
                dim_name = dim.get("name", dim.get("dimension_id", "Unknown"))
                weight = dim.get("weight", 0.33)
                levels = dim.get("levels", {})

                dimensions_text += f"\n### {dim_name} (weight: {weight:.0%})\n"
                for score, desc in sorted(levels.items(), reverse=True):
                    dimensions_text += f"  - {score}: {desc}\n"
        else:
            # Fallback to simple rubric
            dimensions_text = """
### Classification Accuracy (weight: 50%)
  - 1.0: Correct classification matching expected output
  - 0.5: Partially correct or borderline case
  - 0.0: Incorrect classification

### Reasoning Quality (weight: 50%)
  - 1.0: Clear, logical reasoning with evidence
  - 0.5: Reasoning present but incomplete
  - 0.0: No reasoning or flawed logic
"""

        # Build examples text
        examples_text = ""
        if examples:
            examples_text = "\n## EXAMPLES:\n"
            for score_key, example in examples.items():
                examples_text += f"- {score_key}: {example}\n"

        return f"""You are an expert evaluator for keyword classification using a multi-dimensional rubric.

## CRITERION: {criterion.get("name", criterion.get("criterion_id", "Unknown"))}
- Type: {criterion.get("criterion_type", "GENERAL")}
- Description: {criterion.get("description", "N/A")}

## MULTI-DIMENSIONAL RUBRIC
Evaluate each dimension separately, then compute weighted average.
{dimensions_text}
{examples_text}
## INPUT TO EVALUATE:
Keyword: {{{{keyword}}}}
Expected Classification: {{{{expected}}}}

## MODEL OUTPUT:
Classification: {{{{output_classification}}}}
Reasoning: {{{{output_reasoning}}}}
Confidence: {{{{output_confidence}}}}

## YOUR TASK:
1. Score EACH dimension using its rubric (1.0, 0.5, or 0.0)
2. Compute the weighted average as final score
3. Provide brief explanation for each dimension

Return JSON:
{{
  "dimension_scores": {{
    "<dimension_id>": {{"score": <0.0-1.0>, "reason": "<brief reason>"}},
    ...
  }},
  "score": <weighted average 0.0-1.0>,
  "explanation": "<overall summary>"
}}"""

    def run_judge(
        self,
        scorer: Dict[str, Any],
        input_data: Dict[str, Any],
        expected: Dict[str, Any],
        output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run a single LLM judge scorer."""
        judge_prompt = scorer["judge_prompt"]

        # Substitute variables
        judge_prompt = judge_prompt.replace("{{keyword}}", str(input_data.get("keyword", "")))
        judge_prompt = judge_prompt.replace("{{expected}}", str(expected.get("branding_scope_1", expected.get("branding_scope", expected.get("classification", "")))))
        judge_prompt = judge_prompt.replace("{{output_classification}}", str(output.get("branding_scope", output.get("branding_scope_1", output.get("classification", "")))))
        judge_prompt = judge_prompt.replace("{{output_reasoning}}", str(output.get("reasoning", "")))
        judge_prompt = judge_prompt.replace("{{output_confidence}}", str(output.get("confidence", "")))

        try:
            response = self.client.chat.completions.create(
                model=self.judge_model,
                messages=[{"role": "user", "content": judge_prompt}],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"score": 0.0, "explanation": f"Judge error: {e}"}

    def evaluate_test_case(
        self,
        test_case: Dict[str, Any],
        output: Dict[str, Any],
        scorers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate a single test case with all scorers."""
        input_data = test_case.get("input", test_case)
        expected = test_case.get("expected", test_case)

        scores = {}
        explanations = {}

        for scorer in scorers:
            result = self.run_judge(scorer, input_data, expected, output)
            scores[scorer["name"]] = result.get("score", 0.0)
            explanations[scorer["name"]] = result.get("explanation", "")

        # Calculate pass/fail
        avg_score = sum(scores.values()) / len(scores) if scores else 0.0
        passed = avg_score >= 0.7

        # Check exact match
        expected_class = expected.get("branding_scope_1", expected.get("branding_scope", expected.get("classification", "")))
        output_class = output.get("branding_scope", output.get("branding_scope_1", output.get("classification", "")))
        exact_match = expected_class == output_class

        return {
            "input": input_data,
            "expected": expected,
            "output": output,
            "scores": scores,
            "explanations": explanations,
            "avg_score": avg_score,
            "passed": passed,
            "exact_match": exact_match
        }

    def analyze_failures(
        self,
        test_results: List[Dict[str, Any]],
        scorers: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze failures grouped by rule."""
        rule_failures = {}

        for result in test_results:
            if not result.get("passed", True):
                scores = result.get("scores", {})
                for rule_name, score in scores.items():
                    if score < 0.7:
                        if rule_name not in rule_failures:
                            rule_failures[rule_name] = {
                                "count": 0,
                                "examples": [],
                                "avg_score": 0.0
                            }
                        rule_failures[rule_name]["count"] += 1
                        if len(rule_failures[rule_name]["examples"]) < 3:
                            rule_failures[rule_name]["examples"].append({
                                "keyword": result["input"].get("keyword", ""),
                                "expected": result["expected"],
                                "output": result["output"],
                                "score": score,
                                "explanation": result.get("explanations", {}).get(rule_name, "")
                            })

        # Calculate average scores
        for rule_name, data in rule_failures.items():
            total_score = sum(ex["score"] for ex in data["examples"])
            data["avg_score"] = total_score / len(data["examples"]) if data["examples"] else 0.0

        return rule_failures

    def generate_suggestions(
        self,
        rule_failures: Dict[str, Dict[str, Any]],
        scorers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate improvement suggestions for failing rules."""
        if not rule_failures:
            return []

        failing_rule_names = list(rule_failures.keys())
        failures_context = json.dumps(rule_failures, indent=2, default=str)
        scorers_context = json.dumps([{"name": s["name"], "description": s["description"]} for s in scorers], indent=2)

        suggestions_prompt = f"""You are an expert prompt engineer. Analyze these failing rules and provide specific improvement suggestions.

## FAILING RULES:
{failing_rule_names}

## FAILURE DETAILS:
{failures_context}

## SCORERS (rule definitions):
{scorers_context}

For EACH failing rule, provide a specific, actionable suggestion.

Return JSON:
{{"suggestions": [
  {{"rule_id": "<exact rule name>", "suggestion": "<specific improvement>"}},
  ...
]}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": suggestions_prompt}],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            result = json.loads(response.choices[0].message.content)
            return result.get("suggestions", [])
        except Exception as e:
            self.log(f"  [WARN] Suggestion generation failed: {e}")
            return []

    def optimize_prompt(
        self,
        current_prompt: str,
        rule_failures: Dict[str, Dict[str, Any]],
        suggestions: List[Dict[str, Any]],
        scorers: List[Dict[str, Any]]
    ) -> str:
        """Use reasoning model to rewrite/optimize the prompt."""
        failures_context = json.dumps(rule_failures, indent=2, default=str)
        suggestions_context = json.dumps(suggestions, indent=2)
        scorers_context = json.dumps([{"name": s["name"], "description": s["description"]} for s in scorers], indent=2)

        reasoning_prompt = f"""You are an expert prompt engineer. Optimize this classification prompt based on failure analysis.

## CURRENT PROMPT:
{current_prompt}

## SCORERS (rules being evaluated):
{scorers_context}

## FAILURE ANALYSIS BY RULE:
{failures_context}

## IMPROVEMENT SUGGESTIONS:
{suggestions_context}

## YOUR TASK:
1. Analyze WHY each rule is failing based on the examples
2. Apply the suggested improvements
3. Make rules clearer and more precise
4. Do NOT add hardcoded lists - improve the LOGIC
5. Keep the same overall structure

Return the COMPLETE improved prompt. ONLY return the prompt text, no explanation."""

        try:
            response = self.client.chat.completions.create(
                model=self.optimizer_model,
                messages=[{"role": "user", "content": reasoning_prompt}]
            )
            improved = response.choices[0].message.content.strip()

            # Strip markdown code blocks if present
            if improved.startswith("```"):
                lines = improved.split("\n")
                improved = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

            return improved
        except Exception as e:
            self.log(f"  [ERROR] Prompt optimization failed: {e}")
            return current_prompt

    def generate_diff(self, old_prompt: str, new_prompt: str) -> str:
        """Generate unified diff between prompts."""
        diff = difflib.unified_diff(
            old_prompt.splitlines(keepends=True),
            new_prompt.splitlines(keepends=True),
            fromfile='previous_prompt',
            tofile='current_prompt',
            lineterm=''
        )
        return ''.join(diff)

    def optimize(
        self,
        prompt_path: str,
        dataset_path: str,
        max_iterations: int = 3,
        target_accuracy: float = 0.85,
        max_tests: Optional[int] = None
    ) -> OptimizationResult:
        """
        Run the full optimization loop.

        Args:
            prompt_path: Path to the prompt file
            dataset_path: Path to the dataset JSONL file
            max_iterations: Maximum optimization iterations
            target_accuracy: Stop when this accuracy is reached
            max_tests: Limit number of test cases (None = all)

        Returns:
            OptimizationResult with all iteration data
        """
        self.log(f"\n{'='*60}")
        self.log("PROMPT OPTIMIZATION AGENT")
        self.log(f"{'='*60}")

        # Load prompt and dataset
        original_prompt = self.load_prompt(prompt_path)
        dataset = self.load_dataset(dataset_path, limit=max_tests)

        self.log(f"Module: {self.module}")
        self.log(f"Prompt: {len(original_prompt)} chars")
        self.log(f"Dataset: {len(dataset)} test cases")
        self.log(f"Max iterations: {max_iterations}")
        self.log(f"Target accuracy: {target_accuracy:.0%}")

        # Extract criteria with rubrics and generate judges
        self.log(f"\n[1/5] Extracting criteria with rubrics from prompt...")
        criteria = self.extract_criteria_with_rubrics(original_prompt)
        self.log(f"  Found {len(criteria)} criteria")

        self.log(f"\n[2/5] Generating LLM-as-a-judge evaluators...")
        scorers = self.generate_judges(criteria)
        self.log(f"  Created {len(scorers)} judges with rubrics")

        # Initialize tracking
        current_prompt = original_prompt
        previous_prompt = None
        previous_improvements = []
        iteration_results = []
        best_accuracy = 0.0
        best_iteration = 0
        best_prompt = original_prompt
        errors = []

        # Iteration loop
        for iteration in range(1, max_iterations + 1):
            self.log(f"\n{'='*60}")
            self.log(f"ITERATION {iteration}/{max_iterations}")
            self.log(f"{'='*60}")

            # Run classification on all test cases
            self.log(f"\n[3/5] Running classification on {len(dataset)} keywords...")
            test_results = []

            for i, test_case in enumerate(dataset):
                input_data = test_case.get("input", test_case)
                keyword = input_data.get("keyword", f"test_{i}")

                if self.verbose and (i + 1) % 10 == 0:
                    self.log(f"  Processed {i+1}/{len(dataset)}...")

                # Run classification
                output = self.run_classification(current_prompt, input_data)

                # Evaluate with scorers
                eval_result = self.evaluate_test_case(test_case, output, scorers)
                test_results.append(eval_result)

            # Calculate metrics
            pass_count = sum(1 for r in test_results if r["passed"])
            exact_matches = sum(1 for r in test_results if r["exact_match"])
            accuracy = exact_matches / len(test_results) if test_results else 0.0
            pass_rate = pass_count / len(test_results) if test_results else 0.0

            # Aggregate scores by rule
            aggregate_scores = {}
            for scorer in scorers:
                rule_scores = [r["scores"].get(scorer["name"], 0) for r in test_results]
                aggregate_scores[scorer["name"]] = sum(rule_scores) / len(rule_scores) if rule_scores else 0.0

            self.log(f"\n[4/5] Results:")
            self.log(f"  Accuracy (exact match): {accuracy:.1%}")
            self.log(f"  Pass rate (avg score >= 0.7): {pass_rate:.1%}")
            self.log(f"  Scores by rule:")
            for rule_name, score in sorted(aggregate_scores.items(), key=lambda x: x[1]):
                self.log(f"    {rule_name}: {score:.2f}")

            # Track best
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_iteration = iteration
                best_prompt = current_prompt

            # Analyze failures
            failures = [r for r in test_results if not r["exact_match"]]
            rule_failures = self.analyze_failures(test_results, scorers)

            self.log(f"\n  Failures: {len(failures)}/{len(test_results)}")
            if rule_failures:
                self.log(f"  Failing rules:")
                for rule_name, data in sorted(rule_failures.items(), key=lambda x: x[1]["count"], reverse=True)[:5]:
                    self.log(f"    {rule_name}: {data['count']} failures")

            # Check if target reached
            if accuracy >= target_accuracy:
                self.log(f"\n Target accuracy {target_accuracy:.0%} reached!")

                # Generate diff
                prompt_diff = self.generate_diff(previous_prompt, current_prompt) if previous_prompt else None

                iter_result = IterationResult(
                    iteration=iteration,
                    accuracy=accuracy,
                    pass_rate=pass_rate,
                    prompt_text=current_prompt,
                    prompt_length=len(current_prompt),
                    prompt_diff=prompt_diff,
                    test_results=test_results,
                    aggregate_scores=aggregate_scores,
                    failures=failures,
                    improvements=[],
                    improvements_applied=previous_improvements,
                    timestamp=datetime.now().isoformat()
                )
                iteration_results.append(iter_result)
                break

            # Check if max iterations reached
            if iteration >= max_iterations:
                self.log(f"\n Max iterations reached. Best: {best_accuracy:.1%} at iteration {best_iteration}")

                # Generate suggestions even for final iteration
                suggestions = self.generate_suggestions(rule_failures, scorers)
                improvements = [
                    {
                        "rule_id": s["rule_id"],
                        "suggestion": s["suggestion"],
                        "severity": "high" if rule_failures.get(s["rule_id"], {}).get("count", 0) > 3 else "medium"
                    }
                    for s in suggestions
                ]

                prompt_diff = self.generate_diff(previous_prompt, current_prompt) if previous_prompt else None

                iter_result = IterationResult(
                    iteration=iteration,
                    accuracy=accuracy,
                    pass_rate=pass_rate,
                    prompt_text=current_prompt,
                    prompt_length=len(current_prompt),
                    prompt_diff=prompt_diff,
                    test_results=test_results,
                    aggregate_scores=aggregate_scores,
                    failures=failures,
                    improvements=improvements,
                    improvements_applied=previous_improvements,
                    timestamp=datetime.now().isoformat()
                )
                iteration_results.append(iter_result)
                break

            # Generate suggestions and optimize
            self.log(f"\n[5/5] Optimizing prompt...")
            suggestions = self.generate_suggestions(rule_failures, scorers)
            self.log(f"  Generated {len(suggestions)} suggestions")

            # Build improvements list
            improvements = [
                {
                    "rule_id": s["rule_id"],
                    "suggestion": s["suggestion"],
                    "severity": "high" if rule_failures.get(s["rule_id"], {}).get("count", 0) > 3 else "medium"
                }
                for s in suggestions
            ]

            # Optimize prompt
            new_prompt = self.optimize_prompt(current_prompt, rule_failures, suggestions, scorers)
            self.log(f"  Prompt updated: {len(current_prompt)} -> {len(new_prompt)} chars")

            # Generate diff
            prompt_diff = self.generate_diff(previous_prompt, current_prompt) if previous_prompt else None

            # Store iteration result
            iter_result = IterationResult(
                iteration=iteration,
                accuracy=accuracy,
                pass_rate=pass_rate,
                prompt_text=current_prompt,
                prompt_length=len(current_prompt),
                prompt_diff=prompt_diff,
                test_results=test_results,
                aggregate_scores=aggregate_scores,
                failures=failures,
                improvements=improvements,
                improvements_applied=previous_improvements,
                timestamp=datetime.now().isoformat()
            )
            iteration_results.append(iter_result)

            # Update for next iteration
            previous_prompt = current_prompt
            previous_improvements = improvements
            current_prompt = new_prompt

        # Final result
        original_accuracy = iteration_results[0].accuracy if iteration_results else 0.0

        result = OptimizationResult(
            success=best_accuracy >= target_accuracy,
            best_iteration=best_iteration,
            total_iterations=len(iteration_results),
            original_prompt=original_prompt,
            improved_prompt=best_prompt,
            original_accuracy=original_accuracy,
            best_accuracy=best_accuracy,
            iteration_results=iteration_results,
            scorers_used=[s["name"] for s in scorers],
            criteria_with_rubrics=[
                {
                    "name": s["name"],
                    "criterion_type": s.get("criterion_type", "GENERAL"),
                    "description": s.get("description", ""),
                    "dimensions": s.get("dimensions", []),
                    "examples": s.get("examples", {})
                }
                for s in scorers
            ],
            errors=errors
        )

        self.log(f"\n{'='*60}")
        self.log("OPTIMIZATION COMPLETE")
        self.log(f"{'='*60}")
        self.log(f"Success: {result.success}")
        self.log(f"Best accuracy: {best_accuracy:.1%} (iteration {best_iteration})")
        self.log(f"Improvement: {original_accuracy:.1%} -> {best_accuracy:.1%}")

        return result

    def save_result(self, result: OptimizationResult, output_path: Optional[str] = None) -> str:
        """Save optimization result to JSON file."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.results_dir / f"optimization_{self.module}_{timestamp}.json"

        # Convert to serializable format
        data = {
            "success": result.success,
            "best_iteration": result.best_iteration,
            "total_iterations": result.total_iterations,
            "original_accuracy": result.original_accuracy,
            "best_accuracy": result.best_accuracy,
            "scorers_used": result.scorers_used,
            "criteria_with_rubrics": result.criteria_with_rubrics,
            "errors": result.errors,
            "iteration_results": [
                {
                    "iteration": ir.iteration,
                    "accuracy": ir.accuracy,
                    "pass_rate": ir.pass_rate,
                    "prompt_length": ir.prompt_length,
                    "prompt_diff": ir.prompt_diff,
                    "aggregate_scores": ir.aggregate_scores,
                    "failures_count": len(ir.failures),
                    "improvements": ir.improvements,
                    "improvements_applied": ir.improvements_applied,
                    "timestamp": ir.timestamp,
                    "test_results": [
                        {
                            "keyword": tr.get("input", {}).get("keyword", ""),
                            "expected": tr.get("expected", {}),
                            "output": tr.get("output", {}),
                            "exact_match": tr.get("exact_match", False),
                            "scores": tr.get("scores", {}),
                            "avg_score": tr.get("avg_score", 0)
                        }
                        for tr in ir.test_results
                    ]
                }
                for ir in result.iteration_results
            ]
        }

        # Save prompts separately
        prompts_data = {
            "original_prompt": result.original_prompt,
            "improved_prompt": result.improved_prompt,
            "iteration_prompts": [ir.prompt_text for ir in result.iteration_results]
        }

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

        # Save prompts
        prompts_path = output_path.with_suffix(".prompts.json")
        with open(prompts_path, "w") as f:
            json.dump(prompts_data, f, indent=2)

        self.log(f"\nResults saved to: {output_path}")
        return str(output_path)


# Convenience function
def optimize_prompt(
    module: str,
    prompt_path: str,
    dataset_path: str,
    max_iterations: int = 3,
    target_accuracy: float = 0.85,
    max_tests: Optional[int] = None,
    verbose: bool = True
) -> OptimizationResult:
    """
    Convenience function to run prompt optimization.

    Example:
        result = optimize_prompt(
            module="m02",
            prompt_path="prompts/modules/m02_own_brand.md",
            dataset_path="datasets/m02_dataset.jsonl",
            max_iterations=3,
            target_accuracy=0.85
        )
    """
    optimizer = PromptOptimizer(module=module, verbose=verbose)
    return optimizer.optimize(
        prompt_path=prompt_path,
        dataset_path=dataset_path,
        max_iterations=max_iterations,
        target_accuracy=target_accuracy,
        max_tests=max_tests
    )

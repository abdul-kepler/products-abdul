"""
Critic Agent - Step 1: Find weaknesses in module output.

AGENT A: CRITIC (Adversarial)
Role: Find weaknesses. Must identify at least 3 issues.

Critic Receives:
- question/input_data: Original question/input
- response/output_data: Response to critique
- reference_answer/expected_data: For comparison
- CRITIC_PROMPT: Adversarial instructions

Critic Produces:
- weaknesses[]: Min 3, each with category, claim, evidence, severity (1-5)
- strengths[]: Optional positives
- chain_of_thought: Analysis reasoning
- initial_score: 0-5 Likert

Critic Rubric:
- ACCURACY: Factual errors, incorrect information
- COMPLETENESS: Missing important information
- CLARITY: Confusing, ambiguous, poorly organized
- RELEVANCE: Off-topic, doesn't answer the question
- Severity: 1=Minor, 3=Moderate, 5=Critical
"""

from typing import Any, Optional

from .base_agent import BaseAgent


# Valid categories for weakness/strength classification
CRITIC_CATEGORIES = ["ACCURACY", "COMPLETENESS", "CLARITY", "RELEVANCE"]

# M11-specific categories for hard constraint evaluation
M11_CATEGORIES = [
    "FALSE_POSITIVE",      # Marked something as hard that shouldn't be
    "FALSE_NEGATIVE",      # Missed a genuine hard constraint
    "REASONING_ERROR",     # 3-step test not applied correctly
    "CATEGORY_CONFUSION",  # Confused MECHANISM with QUALITY/DURABILITY/PERFORMANCE
    "DISTRIBUTION_VIOLATION",  # Unreasonable number of constraints
]

# M01-specific categories for brand entity extraction
M01_CATEGORIES = [
    "FALSE_POSITIVE",      # Extracted non-brand (product type, measurement, etc.)
    "FALSE_NEGATIVE",      # Missed valid brand entity
    "FILTER_VIOLATION",    # Exclusion filter not applied correctly
    "TYPO_ERROR",          # Invalid typos (multiple edits, unrealistic)
    "DEDUPLICATION_ERROR", # Duplicate strings in output
    "COUNT_VIOLATION",     # More than 12 entities
]

# Module to categories mapping
MODULE_CATEGORIES = {
    "m11": M11_CATEGORIES,
    "m01": M01_CATEGORIES,
}


class CriticAgent(BaseAgent):
    """
    Adversarial critic that finds weaknesses in module outputs.

    Temperature: 0.7 (higher for diverse weakness discovery)
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7,
        verbose: bool = False
    ):
        super().__init__(model=model, temperature=temperature, verbose=verbose)
        self.min_weaknesses = self._get_config().get('debate', {}).get('min_weaknesses', 3)
        self.categories = CRITIC_CATEGORIES
        self._current_module = None  # Track current module for category selection

    def _get_agent_name(self) -> str:
        return "critic"

    def build_prompt(
        self,
        module_id: str = "",
        input_data: Any = None,
        output_data: Any = None,
        expected_data: Any = None,
        context: str = "",
        **kwargs
    ) -> str:
        """Build the critic prompt for finding weaknesses."""

        # Track current module for category selection
        self._current_module = module_id.lower() if module_id else ""

        # Try module-specific template first (e.g., critic_m11.md)
        module_template = self._load_prompt_template(f"critic_{self._current_module}")
        if module_template:
            if self.verbose:
                print(f"[CriticAgent] Using module-specific prompt: critic_{self._current_module}.md")
            # Use module-specific categories if available
            module_key = self._current_module.lower()
            if module_key in MODULE_CATEGORIES:
                self.categories = MODULE_CATEGORIES[module_key]
            elif "m11" in self._current_module:
                self.categories = M11_CATEGORIES
            elif "m01" in self._current_module:
                self.categories = M01_CATEGORIES
            template = module_template
        else:
            # Fall back to generic template
            template = self._load_prompt_template("critic")
            self.categories = CRITIC_CATEGORIES

        # If template exists, use it with variable substitution
        if template:
            prompt = template.format(
                module_id=module_id,
                input_data=self._format_json(input_data),
                output_data=self._format_json(output_data),
                expected_data=self._format_json(expected_data),
                context=context,
                min_weaknesses=self.min_weaknesses,
                categories=", ".join(self.categories),
            )
            return prompt

        # Fallback inline prompt
        return f"""You are a rigorous ADVERSARIAL critic evaluating LLM module output. Your job is to find AT LEAST {self.min_weaknesses} specific weaknesses in the output.

## YOUR ROLE
You are adversarial - actively look for problems. Be thorough and specific. Don't be satisfied with surface-level issues.

## EVALUATION CONTEXT
Module: {module_id}
{context}

## QUESTION / INPUT (What the module received)
```json
{self._format_json(input_data)}
```

## RESPONSE (What you're critiquing)
```json
{self._format_json(output_data)}
```

## REFERENCE ANSWER (Ground truth for comparison)
```json
{self._format_json(expected_data)}
```

## CRITIC RUBRIC
| Category | What to Look For |
|----------|------------------|
| ACCURACY | Factual errors, incorrect information, wrong values |
| COMPLETENESS | Missing important information, incomplete data |
| CLARITY | Confusing, ambiguous, poorly organized |
| RELEVANCE | Off-topic, doesn't answer the question |

## SEVERITY SCALE (1-5)
1 = Minor (small issue)
2 = Low (noticeable but not significant)
3 = Moderate (affects quality but usable)
4 = Major (significantly reduces usefulness)
5 = Critical (makes output unusable)

## YOUR TASK
1. Analyze the response against the reference answer
2. Identify AT LEAST {self.min_weaknesses} specific weaknesses
3. Document each weakness with category, claim, evidence, and severity (1-5)
4. Note any strengths (optional)
5. Provide your chain of thought reasoning
6. Assign an initial score (0-5 Likert)

## REQUIRED OUTPUT FORMAT
Return ONLY valid JSON:
{{
  "chain_of_thought": "First, I compared the response to the reference answer and noticed...",
  "weaknesses": [
    {{
      "id": "W1",
      "category": "ACCURACY",
      "claim": "The brand name was extracted incorrectly",
      "evidence": "Output shows 'Sonny' but input clearly states 'Sony'",
      "severity": 5
    }},
    {{
      "id": "W2",
      "category": "COMPLETENESS",
      "claim": "Missing sub-brand information",
      "evidence": "Title mentions 'WH-1000XM5' product line but not extracted",
      "severity": 3
    }},
    {{
      "id": "W3",
      "category": "...",
      "claim": "...",
      "evidence": "...",
      "severity": 2
    }}
  ],
  "strengths": [
    {{
      "id": "S1",
      "category": "RELEVANCE",
      "claim": "Output correctly focuses on the requested task",
      "evidence": "All extracted fields relate to brand identification"
    }}
  ],
  "initial_score": 2,
  "overall_assessment": "Brief summary of the main issues found"
}}

IMPORTANT:
- You MUST find at least {self.min_weaknesses} weaknesses
- Each weakness must have concrete evidence from the actual response
- Severity must be a number 1-5 (not text)
- Categories must be: ACCURACY, COMPLETENESS, CLARITY, or RELEVANCE"""

    def parse_response(self, response: dict) -> dict:
        """Parse and validate the critic's response."""
        weaknesses = response.get("weaknesses", [])
        strengths = response.get("strengths", [])

        # Determine valid categories based on current module
        valid_categories = self.categories if self.categories else CRITIC_CATEGORIES
        module_key = (self._current_module or "").lower()
        if module_key in MODULE_CATEGORIES:
            default_category = MODULE_CATEGORIES[module_key][0]  # First category as default
        elif "m11" in module_key or "m01" in module_key:
            default_category = "FALSE_POSITIVE"
        else:
            default_category = "ACCURACY"

        # Validate each weakness has required fields
        validated_weaknesses = []
        for w in weaknesses:
            if all(k in w for k in ["id", "category", "claim", "evidence", "severity"]):
                # Normalize category to uppercase
                w["category"] = w["category"].upper().replace(" ", "_")
                if w["category"] not in valid_categories:
                    w["category"] = default_category  # Module-appropriate default

                # Normalize severity to 1-5 integer
                severity = w.get("severity", 3)
                if isinstance(severity, str):
                    # Convert text severity to numeric
                    severity_map = {"minor": 1, "low": 2, "moderate": 3, "major": 4, "critical": 5}
                    severity = severity_map.get(severity.lower(), 3)
                w["severity"] = max(1, min(5, int(severity)))

                validated_weaknesses.append(w)

        # Validate strengths (optional)
        validated_strengths = []
        strength_default = "CORRECT_IDENTIFICATION" if "m11" in (self._current_module or "") else "RELEVANCE"
        for s in strengths:
            if all(k in s for k in ["id", "category", "claim", "evidence"]):
                s["category"] = s["category"].upper().replace(" ", "_")
                # Strengths can have different categories - be more permissive
                validated_strengths.append(s)

        # Check minimum weaknesses
        has_minimum = len(validated_weaknesses) >= self.min_weaknesses

        # Extract initial score (0-5)
        initial_score = response.get("initial_score", 0)
        if isinstance(initial_score, str):
            try:
                initial_score = float(initial_score)
            except ValueError:
                initial_score = 0
        initial_score = max(0, min(5, initial_score))

        return {
            "chain_of_thought": response.get("chain_of_thought", ""),
            "weaknesses": validated_weaknesses,
            "strengths": validated_strengths,
            "initial_score": initial_score,
            "overall_assessment": response.get("overall_assessment", ""),
            "weakness_count": len(validated_weaknesses),
            "strength_count": len(validated_strengths),
            "has_minimum_weaknesses": has_minimum,
            "by_category": self._group_by_category(validated_weaknesses),
            "by_severity": self._group_by_severity(validated_weaknesses),
            "avg_severity": self._calc_avg_severity(validated_weaknesses),
        }

    def _group_by_category(self, items: list) -> dict:
        """Group items by category."""
        # Use current categories or default
        valid_categories = self.categories if self.categories else CRITIC_CATEGORIES
        grouped = {cat: [] for cat in valid_categories}
        for item in items:
            cat = item.get("category", valid_categories[0] if valid_categories else "ACCURACY")
            if cat in grouped:
                grouped[cat].append(item)
            else:
                # Add unexpected categories to 'other'
                if "other" not in grouped:
                    grouped["other"] = []
                grouped["other"].append(item)
        return grouped

    def _group_by_severity(self, weaknesses: list) -> dict:
        """Group weaknesses by severity level."""
        grouped = {1: [], 2: [], 3: [], 4: [], 5: []}
        for w in weaknesses:
            sev = w.get("severity", 3)
            if sev in grouped:
                grouped[sev].append(w)
        return grouped

    def _calc_avg_severity(self, weaknesses: list) -> float:
        """Calculate average severity of weaknesses."""
        if not weaknesses:
            return 0.0
        total = sum(w.get("severity", 3) for w in weaknesses)
        return round(total / len(weaknesses), 2)

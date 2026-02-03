"""
Judge Agent - Step 3: Evaluate debate and score response.

AGENT C: JUDGE (Pairwise)
Role: Evaluate debate. Score each side. Declare winners.

Judge Receives:
- question/input_data: Original question
- response/output_data: Original response
- critic_output: Full critique (weaknesses, chain_of_thought, initial_score)
- defender_output: Full defense (defenses, overall_argument)
- previous_feedback: (If retry) Meta-judge feedback

Judge Produces:
- point_judgments[]: critic_score, defender_score, winner, reasoning
- rubric_scores{}: Decomposed scores (ACCURACY, COMPLETENESS, CLARITY, RELEVANCE, HELPFULNESS)
- final_score: 0-5 overall (average ± 0.5 debate adjustment)

Judge Rubric:
- Argument Strength (0-5): 0=Invalid, 2=Moderate, 4=Strong, 5=Decisive
- Dimensions: ACCURACY, COMPLETENESS, CLARITY, RELEVANCE, HELPFULNESS
- Final Score: Average of dimensions ± 0.5 based on debate outcome
"""

from typing import Any, Optional

from .base_agent import BaseAgent


# Rubric dimensions for scoring
JUDGE_DIMENSIONS = ["ACCURACY", "COMPLETENESS", "CLARITY", "RELEVANCE", "HELPFULNESS"]


class JudgeAgent(BaseAgent):
    """
    Judge agent that evaluates the debate and scores the response.

    Temperature: 0.3 (lower for consistent scoring)
    """

    DIMENSIONS = JUDGE_DIMENSIONS

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.3,
        verbose: bool = False
    ):
        super().__init__(model=model, temperature=temperature, verbose=verbose)

        # Load Likert rubrics (for scale descriptions)
        likert_config = self._get_likert_rubrics()
        self.scale = likert_config.get("scale", {})

    def _get_agent_name(self) -> str:
        return "judge"

    def build_prompt(
        self,
        module_id: str = "",
        input_data: Any = None,
        output_data: Any = None,
        expected_data: Any = None,
        weaknesses: list = None,
        rebuttals: list = None,
        critic_output: dict = None,
        defender_output: dict = None,
        previous_feedback: str = None,
        context: str = "",
        **kwargs
    ) -> str:
        """Build the judge prompt for pairwise evaluation."""
        weaknesses = weaknesses or []
        rebuttals = rebuttals or []

        # Format debate summary with full critic/defender output
        debate_text = self._format_debate(
            weaknesses, rebuttals,
            critic_output=critic_output,
            defender_output=defender_output
        )

        # Add previous feedback if retrying
        if previous_feedback:
            debate_text += f"\n\n## PREVIOUS META-JUDGE FEEDBACK\n{previous_feedback}"

        # Load template if available
        template = self._load_prompt_template("judge")

        if template:
            return template.format(
                module_id=module_id,
                input_data=self._format_json(input_data),
                output_data=self._format_json(output_data),
                expected_data=self._format_json(expected_data),
                debate_summary=debate_text,
                scale_description="",  # Built into template
                criteria_description="",  # Built into template
                context=context,
            )

        # Fallback inline prompt
        return f"""You are an impartial JUDGE evaluating a debate between a Critic and Defender about an LLM module output.

## YOUR ROLE
Evaluate the debate, score each side, and declare winners.

## EVALUATION CONTEXT
Module: {module_id}
{context}

## QUESTION / INPUT
```json
{self._format_json(input_data)}
```

## RESPONSE (What you're evaluating)
```json
{self._format_json(output_data)}
```

## REFERENCE ANSWER
```json
{self._format_json(expected_data)}
```

## DEBATE TRANSCRIPT
{debate_text}

## ARGUMENT STRENGTH SCALE (0-5)
0=Invalid, 1=Weak, 2=Moderate, 3=Good, 4=Strong, 5=Decisive

## RUBRIC DIMENSIONS (0-5)
ACCURACY: Is the information factually correct?
COMPLETENESS: Does it include all required information?
CLARITY: Is it clear and well-organized?
RELEVANCE: Does it address the question?
HELPFULNESS: Would this be useful to the end user?

## YOUR TASK
1. Judge each debated point (critic_score, defender_score, winner)
2. Score the response on each dimension (0-5)
3. Calculate final_score = average ± 0.5 (adjust based on debate outcome)

## REQUIRED OUTPUT FORMAT
Return ONLY valid JSON:
{{
  "point_judgments": [
    {{
      "weakness_id": "W1",
      "critic_score": 4,
      "defender_score": 2,
      "winner": "critic",
      "reasoning": "The Critic correctly identified..."
    }}
  ],
  "debate_summary": {{
    "critic_wins": 1,
    "defender_wins": 1,
    "ties": 1,
    "overall_winner": "tie"
  }},
  "rubric_scores": {{
    "ACCURACY": 3,
    "COMPLETENESS": 3,
    "CLARITY": 4,
    "RELEVANCE": 4,
    "HELPFULNESS": 3
  }},
  "justifications": {{
    "ACCURACY": "The response correctly...",
    "COMPLETENESS": "Covers the main...",
    "CLARITY": "Well-structured...",
    "RELEVANCE": "Directly addresses...",
    "HELPFULNESS": "Provides useful..."
  }},
  "dimension_average": 3.4,
  "debate_adjustment": -0.5,
  "final_score": 2.9,
  "summary": "The response is acceptable but..."
}}"""

    def _format_debate(
        self,
        weaknesses: list,
        rebuttals: list,
        critic_output: dict = None,
        defender_output: dict = None
    ) -> str:
        """Format the debate for the judge prompt."""
        if not weaknesses:
            return "No debate occurred - evaluating output directly."

        lines = []

        # Add critic's chain of thought if available
        if critic_output and critic_output.get("chain_of_thought"):
            lines.append("### CRITIC'S ANALYSIS")
            lines.append(f"Chain of Thought: {critic_output['chain_of_thought']}")
            lines.append(f"Initial Score: {critic_output.get('initial_score', 'N/A')}/5")
            lines.append("")

        # Create defense lookup
        defense_map = {d.get("weakness_id"): d for d in rebuttals}

        lines.append("### DEBATED POINTS\n")
        for w in weaknesses:
            wid = w.get("id", "?")
            severity = w.get("severity", "?")
            severity_label = {1: 'Minor', 2: 'Low', 3: 'Moderate', 4: 'Major', 5: 'Critical'}.get(severity, str(severity))

            lines.append(f"#### {wid}: {w.get('category', 'UNKNOWN')} (Severity: {severity} - {severity_label})")
            lines.append(f"**CRITIC's Claim**: {w.get('claim', w.get('description', 'No claim'))}")
            lines.append(f"**CRITIC's Evidence**: {w.get('evidence', 'None provided')}")

            if wid in defense_map:
                d = defense_map[wid]
                lines.append(f"**DEFENDER's Verdict**: {d.get('verdict', 'unknown').upper()}")
                lines.append(f"**DEFENDER's Rebuttal**: {d.get('rebuttal', 'No rebuttal')}")
                if d.get("evidence"):
                    lines.append(f"**DEFENDER's Evidence**: {d.get('evidence')}")
                if d.get("concession"):
                    lines.append(f"**DEFENDER's Concession**: {d.get('concession')}")
            lines.append("")

        # Add defender's overall argument if available
        if defender_output and defender_output.get("overall_argument"):
            lines.append("### DEFENDER'S OVERALL ARGUMENT")
            lines.append(defender_output["overall_argument"])

        return "\n".join(lines)

    def parse_response(self, response: dict) -> dict:
        """Parse and validate the judge's response."""
        # Parse point judgments
        point_judgments = response.get("point_judgments", [])
        validated_judgments = []
        for pj in point_judgments:
            if "weakness_id" in pj:
                # Normalize scores to 0-5
                pj["critic_score"] = max(0, min(5, int(pj.get("critic_score", 0))))
                pj["defender_score"] = max(0, min(5, int(pj.get("defender_score", 0))))
                # Normalize winner
                if pj.get("winner") not in ["critic", "defender", "tie"]:
                    # Infer from scores
                    if pj["critic_score"] > pj["defender_score"]:
                        pj["winner"] = "critic"
                    elif pj["defender_score"] > pj["critic_score"]:
                        pj["winner"] = "defender"
                    else:
                        pj["winner"] = "tie"
                validated_judgments.append(pj)

        # Calculate debate summary
        critic_wins = sum(1 for pj in validated_judgments if pj.get("winner") == "critic")
        defender_wins = sum(1 for pj in validated_judgments if pj.get("winner") == "defender")
        ties = sum(1 for pj in validated_judgments if pj.get("winner") == "tie")

        if critic_wins > defender_wins:
            overall_winner = "critic"
        elif defender_wins > critic_wins:
            overall_winner = "defender"
        else:
            overall_winner = "tie"

        debate_summary = response.get("debate_summary", {
            "critic_wins": critic_wins,
            "defender_wins": defender_wins,
            "ties": ties,
            "overall_winner": overall_winner,
        })

        # Parse rubric scores
        rubric_scores = response.get("rubric_scores", {})
        validated_scores = {}
        for dim in self.DIMENSIONS:
            score = rubric_scores.get(dim, rubric_scores.get(dim.lower(), 0))
            try:
                score = int(score)
                score = max(0, min(5, score))
            except (ValueError, TypeError):
                score = 0
            validated_scores[dim] = score

        # Calculate dimension average
        if validated_scores:
            dimension_average = sum(validated_scores.values()) / len(validated_scores)
            dimension_average = round(dimension_average, 2)
        else:
            dimension_average = 0.0

        # Calculate debate adjustment
        if overall_winner == "defender":
            debate_adjustment = 0.5
        elif overall_winner == "critic":
            debate_adjustment = -0.5
        else:
            debate_adjustment = 0.0

        # Calculate final score
        final_score = dimension_average + debate_adjustment
        final_score = max(0, min(5, round(final_score, 1)))

        # Parse justifications
        justifications = response.get("justifications", {})

        # Backward compatibility: map old format to new
        scores_compat = {
            "accuracy": validated_scores.get("ACCURACY", 0),
            "relevance": validated_scores.get("RELEVANCE", 0),
            "completeness": validated_scores.get("COMPLETENESS", 0),
            "clarity": validated_scores.get("CLARITY", 0),
            "reasoning": validated_scores.get("HELPFULNESS", 0),  # Map helpfulness to reasoning for compat
        }

        return {
            # New format
            "point_judgments": validated_judgments,
            "debate_summary": debate_summary,
            "rubric_scores": validated_scores,
            "justifications": justifications,
            "dimension_average": dimension_average,
            "debate_adjustment": debate_adjustment,
            "final_score": final_score,
            "summary": response.get("summary", ""),
            # Backward compatibility
            "scores": scores_compat,
            "overall": final_score,
        }

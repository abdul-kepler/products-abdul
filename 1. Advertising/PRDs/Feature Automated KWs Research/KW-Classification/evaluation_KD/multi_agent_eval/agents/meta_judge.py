"""
Meta Judge Agent - Step 4: Evaluate judgment quality and detect sycophancy.

AGENT D: META-JUDGE
Role: Evaluate the judgment quality. Detect sycophancy.

Meta-Judge Receives:
- All previous outputs: critique, defense, judgment
- META_JUDGE_PROMPT: Anti-sycophancy instructions

Meta-Judge Produces:
- is_sycophantic: true/false
- judgment_quality: 0-5 score
- confidence: 0.0-1.0 (calculated as judgment_quality / 5.0)
- should_retry: true if sycophantic or quality < 3

Meta-Judge Rubric - ANTI-SYCOPHANCY:
- Sycophancy Triggers: "Both sides good" without specifics, 4-5 score with real issues ignored
- Quality Scale: 0=Sycophantic, 3=Adequate, 5=Exceptional
- Confidence: judgment_quality / 5.0
"""

from typing import Any, Optional

from .base_agent import BaseAgent


# Sycophancy trigger keywords
SYCOPHANCY_PHRASES = [
    "both sides made good points",
    "both arguments have merit",
    "excellent output",
    "perfect response",
    "outstanding work",
    "well done",
    "good job",
]


class MetaJudge(BaseAgent):
    """
    Meta-judge that evaluates judgment quality and detects sycophancy.

    Temperature: 0.2 (very low for reliable detection)
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.2,
        verbose: bool = False
    ):
        super().__init__(model=model, temperature=temperature, verbose=verbose)

        # Load sycophancy config
        config = self._get_config()
        self.sycophancy_config = config.get("sycophancy", {})
        self.triggers = self.sycophancy_config.get("triggers", {})

    def _get_agent_name(self) -> str:
        return "meta_judge"

    def build_prompt(
        self,
        critic_output: dict = None,
        defender_output: dict = None,
        judge_output: dict = None,
        # Legacy parameters for backward compatibility
        scores: dict = None,
        justifications: dict = None,
        weaknesses: list = None,
        rebuttals: list = None,
        summary: str = "",
        **kwargs
    ) -> str:
        """Build the meta-judge prompt for sycophancy detection."""
        critic_output = critic_output or {}
        defender_output = defender_output or {}
        judge_output = judge_output or {}

        # Format critic output
        critic_text = self._format_agent_output("Critic", critic_output, [
            ("chain_of_thought", "Chain of Thought"),
            ("initial_score", "Initial Score"),
            ("weaknesses", "Weaknesses"),
            ("strengths", "Strengths"),
            ("overall_assessment", "Overall Assessment"),
        ])

        # Format defender output
        defender_text = self._format_agent_output("Defender", defender_output, [
            ("defenses", "Defenses"),
            ("overall_argument", "Overall Argument"),
            ("weaknesses_accepted", "Weaknesses Accepted"),
            ("weaknesses_rejected", "Weaknesses Rejected"),
        ])

        # Format judge output
        judge_text = self._format_agent_output("Judge", judge_output, [
            ("point_judgments", "Point Judgments"),
            ("debate_summary", "Debate Summary"),
            ("rubric_scores", "Rubric Scores"),
            ("justifications", "Justifications"),
            ("dimension_average", "Dimension Average"),
            ("debate_adjustment", "Debate Adjustment"),
            ("final_score", "Final Score"),
            ("summary", "Summary"),
        ])

        # Load template if available
        template = self._load_prompt_template("meta_judge")

        if template:
            return template.format(
                critic_output=critic_text,
                defender_output=defender_text,
                judge_output=judge_text,
                # Legacy placeholders
                scores_text="",
                justifications_text="",
                summary="",
                weakness_count=0,
                valid_weaknesses=0,
                contested_weaknesses=0,
            )

        # Fallback inline prompt
        return f"""You are a META-JUDGE evaluating judgment quality and detecting sycophancy.

## YOUR ROLE
Evaluate if the Judge's evaluation is reliable or sycophantic.

## FULL DEBATE TRANSCRIPT

### CRITIC OUTPUT (Agent A)
{critic_text}

### DEFENDER OUTPUT (Agent B)
{defender_text}

### JUDGE OUTPUT (Agent C)
{judge_text}

## SYCOPHANCY TRIGGERS (RED FLAGS)
- "Both sides good" without specifics
- 4-5 scores while valid weaknesses exist
- Vague justifications ("good output", "well done")
- Ignored Defender concessions
- Superlatives without evidence

## JUDGMENT QUALITY SCALE (0-5)
0=Sycophantic, 1=Poor, 2=Weak, 3=Adequate, 4=Good, 5=Exceptional

## RETRY CRITERIA
should_retry = true if:
- is_sycophantic = true
- judgment_quality < 3

## REQUIRED OUTPUT FORMAT
Return ONLY valid JSON:
{{
  "is_sycophantic": false,
  "judgment_quality": 4,
  "confidence": 0.8,
  "should_retry": false,
  "sycophancy_triggers": [],
  "quality_reasoning": "The Judge evaluated each point, declared winners appropriately...",
  "issues_found": [],
  "recommendation": "The judgment is reliable."
}}"""

    def _format_agent_output(self, agent_name: str, output: dict, fields: list) -> str:
        """Format agent output for the meta-judge prompt."""
        if not output:
            return f"No {agent_name} output provided."

        lines = []
        for key, label in fields:
            value = output.get(key)
            if value is not None:
                if isinstance(value, list):
                    if len(value) > 0:
                        lines.append(f"**{label}** ({len(value)} items):")
                        for i, item in enumerate(value[:5]):  # Limit to first 5
                            if isinstance(item, dict):
                                item_summary = ", ".join(f"{k}: {str(v)[:50]}" for k, v in list(item.items())[:3])
                                lines.append(f"  {i+1}. {item_summary}")
                            else:
                                lines.append(f"  {i+1}. {str(item)[:100]}")
                elif isinstance(value, dict):
                    lines.append(f"**{label}**: {self._format_json(value)[:200]}")
                else:
                    lines.append(f"**{label}**: {str(value)[:200]}")

        return "\n".join(lines) if lines else f"Empty {agent_name} output."

    def parse_response(self, response: dict) -> dict:
        """Parse and validate the meta-judge's response."""
        is_sycophantic = response.get("is_sycophantic", False)
        judgment_quality = response.get("judgment_quality", 3)

        # Normalize judgment_quality to 0-5
        try:
            judgment_quality = int(judgment_quality)
            judgment_quality = max(0, min(5, judgment_quality))
        except (ValueError, TypeError):
            judgment_quality = 3

        # Calculate confidence as judgment_quality / 5.0
        confidence = judgment_quality / 5.0

        # Override with response confidence if provided and valid
        if "confidence" in response:
            try:
                provided_confidence = float(response["confidence"])
                if 0 <= provided_confidence <= 1:
                    confidence = provided_confidence
            except (ValueError, TypeError):
                pass

        # Determine should_retry: true if sycophantic OR quality < 3
        should_retry = bool(is_sycophantic) or judgment_quality < 3

        # Support legacy recommendation field
        recommendation = response.get("recommendation", "")
        if not recommendation:
            recommendation = "Retry evaluation" if should_retry else "Accept judgment"

        return {
            # New format
            "is_sycophantic": bool(is_sycophantic),
            "judgment_quality": judgment_quality,
            "confidence": round(confidence, 2),
            "should_retry": should_retry,
            "sycophancy_triggers": response.get("sycophancy_triggers", []),
            "quality_reasoning": response.get("quality_reasoning", ""),
            "issues_found": response.get("issues_found", []),
            "recommendation": recommendation,
            # Backward compatibility
            "reasoning": response.get("quality_reasoning", response.get("reasoning", "")),
        }

    def quick_check(
        self,
        scores: dict = None,
        justifications: dict = None,
        weaknesses_count: int = 0,
        weaknesses_valid: int = 0,
        point_judgments: list = None,
        judge_debate_summary: dict = None,
    ) -> dict:
        """
        Quick heuristic check for sycophancy without LLM call.

        This can be used as a fast pre-check before the full meta-judge evaluation.

        Returns:
            {"likely_sycophantic": bool, "triggers": list, "estimated_quality": int}
        """
        triggers = []
        scores = scores or {}
        justifications = justifications or {}
        point_judgments = point_judgments or []
        judge_debate_summary = judge_debate_summary or {}

        # Check 1: All scores above threshold
        all_scores_above = self.triggers.get("all_scores_above", 4)
        if scores and all(s >= all_scores_above for s in scores.values()):
            triggers.append("all_scores_above_4")

        # Check 2: Justifications too short
        min_length = self.triggers.get("min_justification_length", 50)
        short_justifications = [
            k for k, v in justifications.items()
            if isinstance(v, str) and len(v) < min_length
        ]
        if short_justifications:
            triggers.append(f"short_justifications: {', '.join(short_justifications)}")

        # Check 3: High scores despite critic winning
        overall_winner = judge_debate_summary.get("overall_winner", "")
        if overall_winner == "critic" and scores:
            avg_score = sum(scores.values()) / len(scores)
            if avg_score >= 4:
                triggers.append("high_scores_despite_critic_winning")

        # Check 4: "Both sides good" phrase detection
        all_text = " ".join([
            str(v) for v in justifications.values()
        ]).lower()
        for phrase in SYCOPHANCY_PHRASES:
            if phrase in all_text:
                triggers.append(f"sycophantic_phrase: '{phrase}'")
                break

        # Check 5: Point judgments inconsistent with scores
        if point_judgments:
            critic_wins = sum(1 for pj in point_judgments if pj.get("winner") == "critic")
            if critic_wins >= 2 and scores:
                avg_score = sum(scores.values()) / len(scores)
                if avg_score >= 4:
                    triggers.append("critic_won_multiple_but_scores_high")

        # Estimate quality based on triggers
        if len(triggers) >= 3:
            estimated_quality = 1  # Poor
        elif len(triggers) >= 2:
            estimated_quality = 2  # Weak
        elif len(triggers) >= 1:
            estimated_quality = 3  # Adequate
        else:
            estimated_quality = 4  # Good

        return {
            "likely_sycophantic": len(triggers) >= 2,
            "triggers": triggers,
            "trigger_count": len(triggers),
            "estimated_quality": estimated_quality,
            "estimated_confidence": estimated_quality / 5.0,
        }

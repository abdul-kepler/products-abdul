"""
Defender Agent - Step 2: Argue against critic's weaknesses.

AGENT B: DEFENDER
Role: Argue against critic's weaknesses. Defend each point.

Defender Receives:
- question/input_data: Original question
- response/output_data: Original response
- critic_weaknesses[]: All weaknesses from Agent A
- DEFENDER_PROMPT: Defense instructions

Defender Produces:
- defenses[]: One per weakness with rebuttal, evidence, concession
- overall_argument: Summary defense

Defender Rules:
- Must address EVERY weakness (no skipping)
- Must provide counter-evidence or reasoning
- Must concede valid points (shows good faith)
- No strawmanning - engage with actual arguments
"""

from typing import Any, Optional

from .base_agent import BaseAgent


class DefenderAgent(BaseAgent):
    """
    Defender agent that argues against the critic's weaknesses.

    Temperature: 0.5 (moderate for balanced defenses)
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.5,
        verbose: bool = False
    ):
        super().__init__(model=model, temperature=temperature, verbose=verbose)

    def _get_agent_name(self) -> str:
        return "defender"

    def build_prompt(
        self,
        module_id: str = "",
        input_data: Any = None,
        output_data: Any = None,
        expected_data: Any = None,
        weaknesses: list = None,
        context: str = "",
        **kwargs
    ) -> str:
        """Build the defender prompt for arguing against weaknesses."""
        weaknesses = weaknesses or []

        # Format weaknesses for the prompt (using new format with 'claim')
        weaknesses_text = ""
        for w in weaknesses:
            severity = w.get('severity', 3)
            severity_label = {1: 'Minor', 2: 'Low', 3: 'Moderate', 4: 'Major', 5: 'Critical'}.get(severity, str(severity))
            weaknesses_text += f"""
### Weakness {w.get('id', '?')}
- **Category**: {w.get('category', 'UNKNOWN')}
- **Claim**: {w.get('claim', w.get('description', ''))}
- **Evidence**: {w.get('evidence', '')}
- **Severity**: {severity} ({severity_label})
"""

        # Load template if available
        template = self._load_prompt_template("defender")

        if template:
            return template.format(
                module_id=module_id,
                input_data=self._format_json(input_data),
                output_data=self._format_json(output_data),
                expected_data=self._format_json(expected_data),
                weaknesses_text=weaknesses_text,
                context=context,
            )

        # Fallback inline prompt
        return f"""You are a DEFENDER advocating for the module output. Your job is to argue against the critic's weaknesses with fair, evidence-based arguments.

## YOUR ROLE
You defend the response, but fairly. If a criticism is valid, acknowledge it. Your goal is balanced evaluation, not blind defense.

## EVALUATION CONTEXT
Module: {module_id}
{context}

## QUESTION / INPUT (Original question)
```json
{self._format_json(input_data)}
```

## RESPONSE (What you're defending)
```json
{self._format_json(output_data)}
```

## REFERENCE ANSWER (For comparison)
```json
{self._format_json(expected_data)}
```

## CRITIC WEAKNESSES TO ADDRESS
{weaknesses_text}

## DEFENDER RULES
- Address EVERY weakness (no skipping)
- Provide counter-evidence or reasoning
- Concede valid points (shows good faith)
- No strawmanning - engage with actual arguments

## YOUR TASK
For EACH weakness from the critic:
1. Read the weakness claim and evidence carefully
2. Evaluate if the criticism is fair and accurate
3. Provide counter-evidence OR reasoning to defend
4. Concede valid points honestly
5. Classify as: "valid" | "partially_valid" | "invalid"

## REQUIRED OUTPUT FORMAT
Return ONLY valid JSON:
{{
  "defenses": [
    {{
      "weakness_id": "W1",
      "verdict": "partially_valid",
      "rebuttal": "While the critic claims X, the response actually...",
      "evidence": "The input contains '...' which supports...",
      "concession": "However, I acknowledge that the response could have..."
    }},
    {{
      "weakness_id": "W2",
      "verdict": "valid",
      "rebuttal": "The critic is correct that...",
      "evidence": null,
      "concession": "This is a significant issue because..."
    }},
    {{
      "weakness_id": "W3",
      "verdict": "invalid",
      "rebuttal": "The critic's claim is incorrect because...",
      "evidence": "Looking at the reference answer, we can see...",
      "concession": null
    }}
  ],
  "overall_argument": "The response is [assessment]. While [issues], the output correctly [positives]."
}}

IMPORTANT:
- You MUST address EVERY weakness listed above
- Be fair - don't dismiss valid criticisms
- Provide specific evidence from the response
- A good defense acknowledges genuine problems"""

    def parse_response(self, response: dict) -> dict:
        """Parse and validate the defender's response."""
        # Support both old format (rebuttals) and new format (defenses)
        defenses = response.get("defenses", response.get("rebuttals", []))

        # Validate each defense
        validated_defenses = []
        for d in defenses:
            if "weakness_id" in d and "verdict" in d:
                # Normalize verdict
                if d["verdict"] not in ["valid", "partially_valid", "invalid"]:
                    d["verdict"] = "partially_valid"

                # Normalize field names (support old format)
                if "counter_evidence" in d and "evidence" not in d:
                    d["evidence"] = d.pop("counter_evidence")

                validated_defenses.append(d)

        # Count verdicts
        verdict_counts = {
            "valid": 0,
            "partially_valid": 0,
            "invalid": 0,
        }
        for d in validated_defenses:
            v = d.get("verdict", "partially_valid")
            if v in verdict_counts:
                verdict_counts[v] += 1

        # Support both old format (defense_summary) and new format (overall_argument)
        overall_argument = response.get("overall_argument", response.get("defense_summary", ""))

        return {
            "defenses": validated_defenses,
            "rebuttals": validated_defenses,  # Keep for backward compatibility
            "defense_count": len(validated_defenses),
            "rebuttal_count": len(validated_defenses),  # Backward compatibility
            "verdict_counts": verdict_counts,
            "overall_argument": overall_argument,
            "defense_summary": overall_argument,  # Backward compatibility
            "weaknesses_accepted": verdict_counts["valid"],
            "weaknesses_partially_accepted": verdict_counts["partially_valid"],
            "weaknesses_rejected": verdict_counts["invalid"],
            "weaknesses_contested": verdict_counts["invalid"] + verdict_counts["partially_valid"],
        }

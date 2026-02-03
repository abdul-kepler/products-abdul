"""
Input Filter Agent - Step 0: Injection detection and validation.

Responsibilities:
- Detect prompt injection attempts
- Validate JSON structure
- Ensure required fields are present
"""

import re
from typing import Any

from .base_agent import BaseAgent


class InputFilter(BaseAgent):
    """
    Input validation and injection detection filter.

    Does NOT use LLM - performs pattern matching and structural validation.
    """

    def __init__(self, verbose: bool = False):
        """Initialize input filter (no LLM needed)."""
        self.verbose = verbose
        self._load_config()

    def _load_config(self) -> None:
        """Load injection patterns from config."""
        config = self._get_config()
        filter_config = config.get('input_filter', {})

        # Compile injection detection patterns
        patterns = filter_config.get('injection_patterns', [])
        self.injection_patterns = [
            re.compile(p, re.IGNORECASE) for p in patterns
        ]

        # Required fields for valid input
        self.required_fields = filter_config.get('required_fields', ['input', 'output'])

    def build_prompt(self, **kwargs) -> str:
        """Not used - InputFilter doesn't use LLM."""
        return ""

    def parse_response(self, response: dict) -> dict:
        """Not used - InputFilter doesn't use LLM."""
        return response

    def execute(
        self,
        input_data: Any = None,
        output_data: Any = None,
        expected_data: Any = None,
        raw_text: str = None,
        **kwargs
    ) -> dict:
        """
        Validate input data for injection attempts and structural issues.

        Args:
            input_data: The input that was given to the module
            output_data: The module's output to evaluate
            expected_data: Expected/ground truth output (optional)
            raw_text: Raw text to scan for injection (optional)

        Returns:
            {
                "is_valid": bool,
                "rejection_reason": str or None,
                "checks_passed": list[str],
                "checks_failed": list[str],
            }
        """
        checks_passed = []
        checks_failed = []
        rejection_reasons = []

        # Check 1: Required fields present
        if input_data is None:
            checks_failed.append("input_data_present")
            rejection_reasons.append("Missing input_data")
        else:
            checks_passed.append("input_data_present")

        if output_data is None:
            checks_failed.append("output_data_present")
            rejection_reasons.append("Missing output_data")
        else:
            checks_passed.append("output_data_present")

        # Check 2: Scan for injection patterns in all text content
        text_to_scan = self._extract_text_content(input_data, output_data, expected_data, raw_text)
        injection_found, pattern_matched = self._check_injection(text_to_scan)

        if injection_found:
            checks_failed.append("no_injection")
            rejection_reasons.append(f"Potential injection detected: {pattern_matched}")
        else:
            checks_passed.append("no_injection")

        # Check 3: Output is parseable (not malformed)
        if output_data is not None:
            if self._is_valid_structure(output_data):
                checks_passed.append("output_structure_valid")
            else:
                checks_failed.append("output_structure_valid")
                rejection_reasons.append("Output has invalid structure")

        # Check 4: No suspicious nested structures
        if self._has_suspicious_nesting(output_data):
            checks_failed.append("no_suspicious_nesting")
            rejection_reasons.append("Suspicious deeply nested structure detected")
        else:
            checks_passed.append("no_suspicious_nesting")

        is_valid = len(checks_failed) == 0

        if self.verbose:
            status = "PASSED" if is_valid else "REJECTED"
            print(f"[InputFilter] {status} - Passed: {len(checks_passed)}, Failed: {len(checks_failed)}")

        return {
            "is_valid": is_valid,
            "rejection_reason": "; ".join(rejection_reasons) if rejection_reasons else None,
            "checks_passed": checks_passed,
            "checks_failed": checks_failed,
        }

    def _extract_text_content(self, *args) -> str:
        """Extract all text content from arguments for injection scanning."""
        texts = []
        for arg in args:
            if arg is None:
                continue
            if isinstance(arg, str):
                texts.append(arg)
            elif isinstance(arg, dict):
                texts.append(self._dict_to_text(arg))
            elif isinstance(arg, list):
                texts.append(self._list_to_text(arg))
        return " ".join(texts)

    def _dict_to_text(self, d: dict) -> str:
        """Recursively extract text from dictionary."""
        texts = []
        for key, value in d.items():
            texts.append(str(key))
            if isinstance(value, str):
                texts.append(value)
            elif isinstance(value, dict):
                texts.append(self._dict_to_text(value))
            elif isinstance(value, list):
                texts.append(self._list_to_text(value))
            else:
                texts.append(str(value))
        return " ".join(texts)

    def _list_to_text(self, lst: list) -> str:
        """Recursively extract text from list."""
        texts = []
        for item in lst:
            if isinstance(item, str):
                texts.append(item)
            elif isinstance(item, dict):
                texts.append(self._dict_to_text(item))
            elif isinstance(item, list):
                texts.append(self._list_to_text(item))
            else:
                texts.append(str(item))
        return " ".join(texts)

    def _check_injection(self, text: str) -> tuple[bool, str]:
        """
        Check text for injection patterns.

        Returns:
            (found, matched_pattern)
        """
        for pattern in self.injection_patterns:
            if pattern.search(text):
                return True, pattern.pattern
        return False, ""

    def _is_valid_structure(self, data: Any) -> bool:
        """Check if data has a valid structure."""
        if data is None:
            return False
        if isinstance(data, (dict, list, str, int, float, bool)):
            return True
        return False

    def _has_suspicious_nesting(self, data: Any, depth: int = 0, max_depth: int = 10) -> bool:
        """
        Check for suspiciously deep nesting that might indicate an attack.

        Returns:
            True if suspicious nesting detected
        """
        if depth > max_depth:
            return True

        if isinstance(data, dict):
            for value in data.values():
                if self._has_suspicious_nesting(value, depth + 1, max_depth):
                    return True
        elif isinstance(data, list):
            for item in data:
                if self._has_suspicious_nesting(item, depth + 1, max_depth):
                    return True

        return False

    def quick_check(self, text: str) -> bool:
        """
        Quick injection check for a single text string.

        Returns:
            True if text is safe (no injection detected)
        """
        found, _ = self._check_injection(text)
        return not found

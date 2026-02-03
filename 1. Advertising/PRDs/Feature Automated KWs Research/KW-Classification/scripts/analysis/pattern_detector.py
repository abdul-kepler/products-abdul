#!/usr/bin/env python3
"""
Pattern Detector - Option B

Detects patterns in errors:
- Keyword length patterns
- Word count patterns
- Common words in errors
- Confidence score correlation
- Metadata patterns (ASIN, category)
"""

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class Pattern:
    """Detected error pattern."""
    name: str
    description: str
    affected_count: int
    affected_percentage: float
    examples: list[str]
    severity: str  # high, medium, low


class PatternDetector:
    """Detect patterns in classification errors."""

    def __init__(self):
        self.errors: list[dict] = []
        self.patterns: list[Pattern] = []

    def load_errors(self, errors: list[dict]):
        """Load errors for analysis."""
        self.errors = errors

    def detect_all_patterns(self) -> list[Pattern]:
        """Run all pattern detection methods."""
        self.patterns = []

        if not self.errors:
            return []

        # Run detectors
        self._detect_length_patterns()
        self._detect_word_count_patterns()
        self._detect_common_words()
        self._detect_confidence_patterns()
        self._detect_error_type_patterns()
        self._detect_special_char_patterns()

        # Sort by severity and count
        severity_order = {"high": 0, "medium": 1, "low": 2}
        self.patterns.sort(key=lambda p: (severity_order[p.severity], -p.affected_count))

        return self.patterns

    def _detect_length_patterns(self):
        """Detect patterns related to keyword length."""
        lengths = []
        short_errors = []  # < 10 chars
        long_errors = []   # > 50 chars

        for e in self.errors:
            keyword = e.get("keyword", "")
            length = len(keyword)
            lengths.append(length)

            if length < 10:
                short_errors.append(keyword)
            elif length > 50:
                long_errors.append(keyword)

        avg_length = sum(lengths) / len(lengths) if lengths else 0

        if len(short_errors) > len(self.errors) * 0.2:
            self.patterns.append(Pattern(
                name="short_keyword_errors",
                description=f"Many errors on short keywords (<10 chars). Avg error length: {avg_length:.1f}",
                affected_count=len(short_errors),
                affected_percentage=len(short_errors) / len(self.errors) * 100,
                examples=short_errors[:5],
                severity="medium"
            ))

        if len(long_errors) > len(self.errors) * 0.15:
            self.patterns.append(Pattern(
                name="long_keyword_errors",
                description=f"Many errors on long keywords (>50 chars)",
                affected_count=len(long_errors),
                affected_percentage=len(long_errors) / len(self.errors) * 100,
                examples=long_errors[:5],
                severity="medium"
            ))

    def _detect_word_count_patterns(self):
        """Detect patterns in word count."""
        single_word_errors = []
        many_word_errors = []  # > 5 words

        for e in self.errors:
            keyword = e.get("keyword", "")
            word_count = len(keyword.split())

            if word_count == 1:
                single_word_errors.append(keyword)
            elif word_count > 5:
                many_word_errors.append(keyword)

        if len(single_word_errors) > len(self.errors) * 0.25:
            self.patterns.append(Pattern(
                name="single_word_errors",
                description="High error rate on single-word keywords",
                affected_count=len(single_word_errors),
                affected_percentage=len(single_word_errors) / len(self.errors) * 100,
                examples=single_word_errors[:5],
                severity="high"
            ))

        if len(many_word_errors) > len(self.errors) * 0.15:
            self.patterns.append(Pattern(
                name="multi_word_errors",
                description="High error rate on long phrases (>5 words)",
                affected_count=len(many_word_errors),
                affected_percentage=len(many_word_errors) / len(self.errors) * 100,
                examples=many_word_errors[:5],
                severity="medium"
            ))

    def _detect_common_words(self):
        """Detect commonly occurring words in error keywords."""
        word_counter = Counter()
        word_to_keywords = defaultdict(list)

        for e in self.errors:
            keyword = e.get("keyword", "").lower()
            words = re.findall(r'\b\w+\b', keyword)
            for word in words:
                if len(word) > 2:  # Skip very short words
                    word_counter[word] += 1
                    if len(word_to_keywords[word]) < 3:
                        word_to_keywords[word].append(keyword)

        # Find words that appear in >20% of errors
        threshold = len(self.errors) * 0.15
        common_words = [(word, count) for word, count in word_counter.most_common(20)
                        if count >= threshold and word not in {'the', 'and', 'for', 'with'}]

        if common_words:
            top_word, top_count = common_words[0]
            self.patterns.append(Pattern(
                name="common_word_pattern",
                description=f"Word '{top_word}' appears in {top_count} errors. Other common: {', '.join(w for w,c in common_words[1:5])}",
                affected_count=top_count,
                affected_percentage=top_count / len(self.errors) * 100,
                examples=word_to_keywords[top_word][:5],
                severity="high" if top_count > len(self.errors) * 0.3 else "medium"
            ))

    def _detect_confidence_patterns(self):
        """Detect patterns in confidence scores."""
        high_conf_errors = []  # confidence > 0.9
        low_conf_errors = []   # confidence < 0.6

        for e in self.errors:
            conf = e.get("confidence")
            keyword = e.get("keyword", "")

            if conf is not None:
                try:
                    conf = float(conf)
                except (ValueError, TypeError):
                    continue
                if conf > 0.9:
                    high_conf_errors.append((keyword, conf))
                elif conf < 0.6:
                    low_conf_errors.append((keyword, conf))

        if len(high_conf_errors) > len(self.errors) * 0.3:
            self.patterns.append(Pattern(
                name="overconfident_errors",
                description=f"Model is overconfident (>0.9) on {len(high_conf_errors)} errors",
                affected_count=len(high_conf_errors),
                affected_percentage=len(high_conf_errors) / len(self.errors) * 100,
                examples=[k for k, c in high_conf_errors[:5]],
                severity="high"
            ))

        if low_conf_errors:
            self.patterns.append(Pattern(
                name="low_confidence_errors",
                description=f"Model shows low confidence (<0.6) on {len(low_conf_errors)} errors - may be edge cases",
                affected_count=len(low_conf_errors),
                affected_percentage=len(low_conf_errors) / len(self.errors) * 100,
                examples=[k for k, c in low_conf_errors[:5]],
                severity="low"
            ))

    def _detect_error_type_patterns(self):
        """Detect FP vs FN imbalance."""
        fp_count = sum(1 for e in self.errors if e.get("error_type") == "FP")
        fn_count = sum(1 for e in self.errors if e.get("error_type") == "FN")

        if fp_count > 0 and fn_count > 0:
            ratio = max(fp_count, fn_count) / min(fp_count, fn_count)

            if ratio > 3:
                dominant = "FP" if fp_count > fn_count else "FN"
                self.patterns.append(Pattern(
                    name="error_type_imbalance",
                    description=f"Strong {dominant} bias: {fp_count} FP vs {fn_count} FN (ratio: {ratio:.1f}x)",
                    affected_count=max(fp_count, fn_count),
                    affected_percentage=max(fp_count, fn_count) / len(self.errors) * 100,
                    examples=[e["keyword"] for e in self.errors if e.get("error_type") == dominant][:5],
                    severity="high"
                ))

    def _detect_special_char_patterns(self):
        """Detect errors with special characters."""
        special_char_errors = []

        for e in self.errors:
            keyword = e.get("keyword", "")
            if re.search(r'[^a-zA-Z0-9\s\-]', keyword):
                special_char_errors.append(keyword)

        if len(special_char_errors) > len(self.errors) * 0.1:
            self.patterns.append(Pattern(
                name="special_char_errors",
                description="Errors on keywords with special characters",
                affected_count=len(special_char_errors),
                affected_percentage=len(special_char_errors) / len(self.errors) * 100,
                examples=special_char_errors[:5],
                severity="medium"
            ))

    def generate_report(self) -> str:
        """Generate markdown report of patterns."""
        report = []
        report.append("# Error Pattern Analysis")
        report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append(f"\n**Total Errors Analyzed:** {len(self.errors)}")
        report.append(f"\n**Patterns Detected:** {len(self.patterns)}")

        if not self.patterns:
            report.append("\n\nNo significant patterns detected.")
            return "\n".join(report)

        # Summary table
        report.append("\n## Pattern Summary\n")
        report.append("| Pattern | Severity | Count | % of Errors |")
        report.append("|---------|----------|-------|-------------|")
        for p in self.patterns:
            report.append(f"| {p.name} | {p.severity} | {p.affected_count} | {p.affected_percentage:.1f}% |")

        # Detailed patterns
        report.append("\n## Detailed Patterns\n")
        for p in self.patterns:
            severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[p.severity]
            report.append(f"\n### {severity_emoji} {p.name}")
            report.append(f"\n**Description:** {p.description}")
            report.append(f"\n**Affected:** {p.affected_count} errors ({p.affected_percentage:.1f}%)")
            report.append(f"\n**Examples:**")
            for ex in p.examples:
                report.append(f"- `{ex}`")

        return "\n".join(report)

    def export_patterns(self, output_file: str):
        """Export patterns to JSON."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "total_errors": len(self.errors),
            "patterns": [
                {
                    "name": p.name,
                    "description": p.description,
                    "affected_count": p.affected_count,
                    "affected_percentage": p.affected_percentage,
                    "examples": p.examples,
                    "severity": p.severity
                }
                for p in self.patterns
            ]
        }

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)


def main():
    """Example usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Detect patterns in errors")
    parser.add_argument("--errors-file", "-e", required=True, help="JSON file with errors")
    parser.add_argument("--output", "-o", help="Output file for patterns JSON")
    parser.add_argument("--report", "-r", help="Output file for markdown report")

    args = parser.parse_args()

    # Load errors
    with open(args.errors_file) as f:
        errors = json.load(f)

    print(f"Loaded {len(errors)} errors from {args.errors_file}")

    detector = PatternDetector()
    detector.load_errors(errors)
    patterns = detector.detect_all_patterns()

    print(f"\nDetected {len(patterns)} patterns:")
    for p in patterns:
        print(f"  - [{p.severity}] {p.name}: {p.affected_count} errors")

    if args.output:
        detector.export_patterns(args.output)
        print(f"\nPatterns exported to: {args.output}")

    if args.report:
        report = detector.generate_report()
        with open(args.report, "w") as f:
            f.write(report)
        print(f"Report saved to: {args.report}")
    else:
        print("\n" + detector.generate_report())


if __name__ == "__main__":
    main()

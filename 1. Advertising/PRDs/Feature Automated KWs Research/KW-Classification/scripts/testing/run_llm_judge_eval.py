#!/usr/bin/env python3
"""
Run LLM Judge evaluation on M12b classification results.

This script:
1. Loads M12b experiment results
2. Runs LLM Judge on each result
3. Reports detailed evaluation metrics
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

import openai
from dotenv import load_dotenv

# Load environment
load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")

# Paths
JUDGES_DIR = Path(__file__).parent.parent / "prompts" / "judges"
RESULTS_DIR = Path(__file__).parent.parent / "experiment_results"

# Load judge prompt
JUDGE_PROMPT = (JUDGES_DIR / "judge_m12b_classification.md").read_text()


def run_judge(
    keyword: str,
    title: str,
    validated_use: str,
    hard_constraints: list,
    predicted: dict,
    expected: str
) -> dict:
    """Run LLM judge on a single classification result."""

    # Build reasoning from output steps
    reasoning_parts = []
    if predicted.get("step1_hard_constraint"):
        reasoning_parts.append(f"Step 1: {predicted['step1_hard_constraint'].get('reasoning', '')}")
    if predicted.get("step2_product_type"):
        reasoning_parts.append(f"Step 2: {predicted['step2_product_type'].get('reasoning', '')}")
    if predicted.get("step3_primary_use"):
        reasoning_parts.append(f"Step 3: {predicted['step3_primary_use'].get('reasoning', '')}")
    if predicted.get("step4_complementary"):
        reasoning_parts.append(f"Step 4: {predicted['step4_complementary'].get('reasoning', '')}")
    predicted_reasoning = "\n".join(reasoning_parts) if reasoning_parts else "No reasoning provided"

    # Format hard constraints
    hard_constraints_str = ", ".join(hard_constraints) if hard_constraints else "None"

    # Build prompt
    prompt = JUDGE_PROMPT
    prompt = prompt.replace("{{keyword}}", keyword)
    prompt = prompt.replace("{{title}}", title[:300])
    prompt = prompt.replace("{{validated_use}}", validated_use)
    prompt = prompt.replace("{{hard_constraints}}", hard_constraints_str)
    prompt = prompt.replace("{{predicted_classification}}", predicted.get("classification", "N"))
    prompt = prompt.replace("{{predicted_confidence}}", str(predicted.get("confidence", 0.5)))
    prompt = prompt.replace("{{predicted_reasoning}}", predicted_reasoning)
    prompt = prompt.replace("{{expected_classification}}", expected)

    # Call judge
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": prompt}]
    )

    return json.loads(response.choices[0].message.content)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-file", type=str, help="Path to results JSONL file")
    parser.add_argument("--samples", type=int, default=10, help="Number of samples to judge")
    args = parser.parse_args()

    # Find latest results file if not specified
    if args.results_file:
        results_file = Path(args.results_file)
    else:
        results_files = sorted(RESULTS_DIR.glob("m12b_results_*.jsonl"), reverse=True)
        if not results_files:
            print("No M12b results found. Run experiments first.")
            sys.exit(1)
        results_file = results_files[0]

    print(f"Loading results from: {results_file}")

    # Load results
    results = []
    with open(results_file) as f:
        for line in f:
            results.append(json.loads(line))

    print(f"Loaded {len(results)} results")
    print(f"Judging {args.samples} samples...\n")

    # Run judge on samples
    judge_results = []
    pass_count = 0
    fail_count = 0

    for i, r in enumerate(results[:args.samples]):
        inp = r.get("input", {})
        out = r.get("output", {})
        exp = r.get("expected", {})

        keyword = inp.get("keyword", "")
        expected_class = exp.get("relevancy", exp.get("classification", "N"))
        predicted_class = out.get("classification", "N") if isinstance(out, dict) else "ERR"

        print(f"[{i+1}/{args.samples}] Judging: {keyword[:40]}...")

        try:
            judge_result = run_judge(
                keyword=keyword,
                title=inp.get("title", ""),
                validated_use=inp.get("validated_use", ""),
                hard_constraints=inp.get("hard_constraints", []),
                predicted=out if isinstance(out, dict) else {},
                expected=expected_class
            )

            verdict = judge_result.get("verdict", "FAIL")
            total_score = judge_result.get("total_score", 0)
            summary = judge_result.get("summary", "")

            if verdict == "PASS":
                pass_count += 1
                status = "✓"
            else:
                fail_count += 1
                status = "✗"

            print(f"  {status} Score: {total_score}/100 | Verdict: {verdict}")
            print(f"    Predicted: {predicted_class} | Expected: {expected_class}")
            print(f"    Summary: {summary[:80]}...")

            judge_results.append({
                "keyword": keyword,
                "predicted": predicted_class,
                "expected": expected_class,
                "verdict": verdict,
                "total_score": total_score,
                "judge_result": judge_result
            })

        except Exception as e:
            print(f"  Error: {e}")
            fail_count += 1

        print()

    # Summary
    print("=" * 60)
    print("JUDGE EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total judged: {len(judge_results)}")
    print(f"PASS: {pass_count} ({pass_count/len(judge_results)*100:.1f}%)")
    print(f"FAIL: {fail_count} ({fail_count/len(judge_results)*100:.1f}%)")

    avg_score = sum(r["total_score"] for r in judge_results) / len(judge_results) if judge_results else 0
    print(f"Average Score: {avg_score:.1f}/100")

    # Per-class breakdown
    print("\nPer-Class Judge Scores:")
    for cls in ["R", "S", "C", "N"]:
        cls_results = [r for r in judge_results if r["expected"] == cls]
        if cls_results:
            cls_avg = sum(r["total_score"] for r in cls_results) / len(cls_results)
            cls_pass = sum(1 for r in cls_results if r["verdict"] == "PASS")
            print(f"  {cls}: {cls_avg:.1f}/100 avg | {cls_pass}/{len(cls_results)} PASS")

    # Save results
    output_file = RESULTS_DIR / f"judge_eval_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(output_file, "w") as f:
        json.dump({
            "summary": {
                "total": len(judge_results),
                "pass": pass_count,
                "fail": fail_count,
                "avg_score": avg_score
            },
            "results": judge_results
        }, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()

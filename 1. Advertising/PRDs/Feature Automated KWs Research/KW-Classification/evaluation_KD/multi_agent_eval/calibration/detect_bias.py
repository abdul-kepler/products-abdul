#!/usr/bin/env python3
"""
Bias Detection for Adversarial Debate Evaluation.

Detects:
1. Position Bias: Does argument order affect scores?
2. Leniency Bias: Are scores systematically too high/low?
3. Central Tendency: Are scores clustered around middle?
4. Dimension Bias: Are some dimensions scored higher than others?

Usage:
    python3 calibration/detect_bias.py --results results/m11_multiagent_*.json
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List
import statistics


def load_results(json_path: str) -> List[dict]:
    """Load evaluation results."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data.get('results', [])


def detect_leniency_bias(results: List[dict]) -> dict:
    """
    Detect if scores are systematically too high or too low.

    Leniency bias: Mean > 3.5 (on 0-5 scale)
    Severity bias: Mean < 2.5
    """
    overall_scores = []
    for r in results:
        result = r.get('result', {})
        score = result.get('overall', result.get('final_score', 0))
        if score > 0:
            overall_scores.append(score)

    if not overall_scores:
        return {"error": "No scores found"}

    mean = statistics.mean(overall_scores)
    median = statistics.median(overall_scores)
    stdev = statistics.stdev(overall_scores) if len(overall_scores) > 1 else 0

    bias_type = "NONE"
    if mean > 3.5:
        bias_type = "LENIENCY (too generous)"
    elif mean < 2.5:
        bias_type = "SEVERITY (too harsh)"

    return {
        "mean": round(mean, 2),
        "median": round(median, 2),
        "stdev": round(stdev, 2),
        "min": min(overall_scores),
        "max": max(overall_scores),
        "bias_detected": bias_type,
        "recommendation": "Consider adjusting prompts" if bias_type != "NONE" else "Scores appear balanced"
    }


def detect_central_tendency(results: List[dict]) -> dict:
    """
    Detect if scores cluster around middle (avoiding extreme scores).

    Central tendency = >70% scores are 2, 3, or 4
    """
    overall_scores = []
    for r in results:
        result = r.get('result', {})
        score = result.get('overall', result.get('final_score', 0))
        if score > 0:
            overall_scores.append(round(score))

    if not overall_scores:
        return {"error": "No scores found"}

    middle_count = sum(1 for s in overall_scores if 2 <= s <= 4)
    extreme_count = sum(1 for s in overall_scores if s in [0, 1, 5])
    middle_ratio = middle_count / len(overall_scores)

    distribution = {i: overall_scores.count(i) for i in range(6)}

    return {
        "distribution": distribution,
        "middle_ratio": round(middle_ratio * 100, 1),
        "extreme_ratio": round((1 - middle_ratio) * 100, 1),
        "bias_detected": "CENTRAL TENDENCY" if middle_ratio > 0.8 else "NONE",
        "recommendation": "Judge may be avoiding extreme scores" if middle_ratio > 0.8 else "Score distribution appears healthy"
    }


def detect_dimension_bias(results: List[dict]) -> dict:
    """
    Detect if some dimensions are systematically scored higher/lower.
    """
    dimension_scores = defaultdict(list)

    for r in results:
        result = r.get('result', {})
        scores = result.get('scores', {})
        for dim, score in scores.items():
            dimension_scores[dim].append(score)

    if not dimension_scores:
        return {"error": "No dimension scores found"}

    dim_stats = {}
    for dim, scores in dimension_scores.items():
        if scores:
            dim_stats[dim] = {
                "mean": round(statistics.mean(scores), 2),
                "stdev": round(statistics.stdev(scores), 2) if len(scores) > 1 else 0,
            }

    # Find highest and lowest
    means = {d: s["mean"] for d, s in dim_stats.items()}
    highest = max(means.items(), key=lambda x: x[1])
    lowest = min(means.items(), key=lambda x: x[1])
    spread = highest[1] - lowest[1]

    return {
        "dimension_stats": dim_stats,
        "highest": {"dimension": highest[0], "mean": highest[1]},
        "lowest": {"dimension": lowest[0], "mean": lowest[1]},
        "spread": round(spread, 2),
        "bias_detected": "DIMENSION BIAS" if spread > 1.5 else "NONE",
        "recommendation": f"'{lowest[0]}' may be scored too harshly" if spread > 1.5 else "Dimensions appear balanced"
    }


def detect_debate_winner_correlation(results: List[dict]) -> dict:
    """
    Check if debate winner correlates appropriately with final scores.

    Expected: Critic wins → lower scores, Defender wins → higher scores
    """
    critic_wins_scores = []
    defender_wins_scores = []
    tie_scores = []

    for r in results:
        result = r.get('result', {})
        debate_summary = result.get('judge_debate_summary', {})
        winner = debate_summary.get('overall_winner', '')
        score = result.get('overall', result.get('final_score', 0))

        if winner == 'critic':
            critic_wins_scores.append(score)
        elif winner == 'defender':
            defender_wins_scores.append(score)
        else:
            tie_scores.append(score)

    stats = {}
    if critic_wins_scores:
        stats['critic_wins'] = {"count": len(critic_wins_scores), "mean": round(statistics.mean(critic_wins_scores), 2)}
    if defender_wins_scores:
        stats['defender_wins'] = {"count": len(defender_wins_scores), "mean": round(statistics.mean(defender_wins_scores), 2)}
    if tie_scores:
        stats['ties'] = {"count": len(tie_scores), "mean": round(statistics.mean(tie_scores), 2)}

    # Check for anomaly: critic wins should have LOWER scores
    anomaly = False
    if critic_wins_scores and defender_wins_scores:
        if statistics.mean(critic_wins_scores) > statistics.mean(defender_wins_scores):
            anomaly = True

    return {
        "stats": stats,
        "anomaly_detected": anomaly,
        "recommendation": "ANOMALY: Critic wins have higher scores than Defender wins!" if anomaly else "Debate outcomes correlate correctly with scores"
    }


def print_bias_report(results_path: str, results: List[dict]):
    """Print comprehensive bias detection report."""
    print("\n" + "=" * 70)
    print("BIAS DETECTION REPORT")
    print(f"File: {results_path}")
    print(f"Samples: {len(results)}")
    print("=" * 70)

    # 1. Leniency Bias
    print("\n--- 1. LENIENCY/SEVERITY BIAS ---")
    leniency = detect_leniency_bias(results)
    print(f"Mean Score: {leniency.get('mean', 'N/A')} (expected: ~3.0)")
    print(f"Median: {leniency.get('median', 'N/A')}")
    print(f"Std Dev: {leniency.get('stdev', 'N/A')}")
    print(f"Range: {leniency.get('min', 'N/A')} - {leniency.get('max', 'N/A')}")
    status = "✅" if leniency.get('bias_detected') == "NONE" else "⚠️"
    print(f"Status: {status} {leniency.get('bias_detected', 'N/A')}")
    print(f"→ {leniency.get('recommendation', '')}")

    # 2. Central Tendency
    print("\n--- 2. CENTRAL TENDENCY BIAS ---")
    central = detect_central_tendency(results)
    print(f"Score Distribution: {central.get('distribution', {})}")
    print(f"Middle Scores (2-4): {central.get('middle_ratio', 'N/A')}%")
    print(f"Extreme Scores (0,1,5): {central.get('extreme_ratio', 'N/A')}%")
    status = "✅" if central.get('bias_detected') == "NONE" else "⚠️"
    print(f"Status: {status} {central.get('bias_detected', 'N/A')}")
    print(f"→ {central.get('recommendation', '')}")

    # 3. Dimension Bias
    print("\n--- 3. DIMENSION BIAS ---")
    dimension = detect_dimension_bias(results)
    print("Dimension Means:")
    for dim, stats in dimension.get('dimension_stats', {}).items():
        print(f"  {dim}: {stats['mean']} (±{stats['stdev']})")
    print(f"Highest: {dimension.get('highest', {}).get('dimension', 'N/A')} ({dimension.get('highest', {}).get('mean', 'N/A')})")
    print(f"Lowest: {dimension.get('lowest', {}).get('dimension', 'N/A')} ({dimension.get('lowest', {}).get('mean', 'N/A')})")
    print(f"Spread: {dimension.get('spread', 'N/A')}")
    status = "✅" if dimension.get('bias_detected') == "NONE" else "⚠️"
    print(f"Status: {status} {dimension.get('bias_detected', 'N/A')}")
    print(f"→ {dimension.get('recommendation', '')}")

    # 4. Debate Correlation
    print("\n--- 4. DEBATE WINNER CORRELATION ---")
    debate = detect_debate_winner_correlation(results)
    for winner_type, stats in debate.get('stats', {}).items():
        print(f"  {winner_type}: {stats['count']} samples, mean={stats['mean']}")
    status = "✅" if not debate.get('anomaly_detected') else "❌"
    print(f"Status: {status}")
    print(f"→ {debate.get('recommendation', '')}")

    # Summary
    print("\n" + "=" * 70)
    biases_found = []
    if leniency.get('bias_detected') != "NONE":
        biases_found.append(leniency['bias_detected'])
    if central.get('bias_detected') != "NONE":
        biases_found.append(central['bias_detected'])
    if dimension.get('bias_detected') != "NONE":
        biases_found.append(dimension['bias_detected'])
    if debate.get('anomaly_detected'):
        biases_found.append("DEBATE ANOMALY")

    if biases_found:
        print(f"⚠️  BIASES DETECTED: {', '.join(biases_found)}")
    else:
        print("✅ NO SIGNIFICANT BIASES DETECTED")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Detect biases in LLM evaluation")
    parser.add_argument('--results', required=True, help="Results JSON file")
    args = parser.parse_args()

    results = load_results(args.results)
    if not results:
        print("No results found in file")
        return

    print_bias_report(args.results, results)


if __name__ == "__main__":
    main()

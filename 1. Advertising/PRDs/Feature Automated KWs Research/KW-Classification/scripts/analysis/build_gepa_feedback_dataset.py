#!/usr/bin/env python3
"""
Build a GEPA-ready feedback dataset from LLM-judge results.

Example:
  python scripts/analysis/build_gepa_feedback_dataset.py --module m01
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JUDGE_DIR = PROJECT_ROOT / "evaluation_KD" / "evaluation_experimentV5" / "judge_results"


def normalize_module(module: str) -> str:
    module = module.strip().lower()
    if module.startswith("m") and len(module) == 2 and module[1].isdigit():
        return f"m0{module[1]}"
    return module


def load_judge_file(path: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        evaluations = data.get("evaluations") or data.get("items") or data.get("results") or []
        meta = {
            "experiment": data.get("experiment"),
            "module": data.get("module"),
            "model": data.get("model"),
            "rubrics_version": data.get("rubrics_version"),
            "timestamp": data.get("timestamp"),
            "data_source": data.get("data_source"),
        }
        return evaluations, meta
    if isinstance(data, list):
        return data, {}
    raise ValueError(f"Unsupported JSON structure in {path}")


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def pick_latest_file(files: Iterable[Path]) -> Path | None:
    best = None
    best_ts = None
    for path in files:
        try:
            _, meta = load_judge_file(path)
            ts = parse_timestamp(meta.get("timestamp"))
        except Exception:
            ts = None
        if ts is None:
            ts = datetime.fromtimestamp(path.stat().st_mtime)
        if best is None or (ts and ts > best_ts):
            best = path
            best_ts = ts
    return best


def module_matches(module: str, path: Path, meta: Dict[str, Any]) -> bool:
    module = module.lower()
    meta_module = str(meta.get("module", "")).lower()
    if meta_module == module:
        return True
    name = path.stem.lower()
    if name == module:
        return True
    if name.startswith(module):
        next_char = name[len(module):len(module) + 1]
        # Accept exact match or separators, but avoid m01 matching m01a/m01b
        if next_char == "" or not next_char.isalnum():
            return True
    return False


def clip(text: str, max_chars: int) -> str:
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def build_feedback(entry: Dict[str, Any], max_chars: int) -> str:
    parts = []
    criterion = entry.get("criterion")
    verdict = entry.get("verdict")
    reasoning = entry.get("reasoning")
    if criterion:
        parts.append(f"Criterion: {criterion}")
    if verdict:
        parts.append(f"Verdict: {verdict}")
    if reasoning:
        parts.append(f"Reasoning: {reasoning}")

    expected = entry.get("expected")
    output = entry.get("output")
    if expected is not None:
        parts.append("Expected: " + clip(json.dumps(expected, ensure_ascii=False), max_chars))
    if output is not None:
        parts.append("Output: " + clip(json.dumps(output, ensure_ascii=False), max_chars))

    return " | ".join(parts)


def build_records(
    evaluations: List[Dict[str, Any]],
    module: str,
    include_passes: bool,
    max_feedback_chars: int,
    limit: int | None,
    full: bool,
):
    records = []
    for entry in evaluations:
        verdict = str(entry.get("verdict", "")).upper()
        if not include_passes and verdict == "PASS":
            continue

        record = {
            "input": entry.get("input"),
            "expected": entry.get("expected"),
            "output": entry.get("output"),
            "feedback": build_feedback(entry, max_feedback_chars),
        }
        if full:
            record.update({
                "module": module,
                "sample_id": entry.get("sample_id"),
                "rubric_id": entry.get("rubric_id"),
                "criterion": entry.get("criterion"),
                "verdict": entry.get("verdict"),
                "reasoning": entry.get("reasoning"),
            })
        records.append(record)
        if limit and len(records) >= limit:
            break
    return records


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build GEPA feedback dataset from judge_results JSON.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--module", required=True, help="Module name (e.g., m01, m12b)")
    parser.add_argument("--judge-dir", default=str(DEFAULT_JUDGE_DIR), help="Directory with judge_results JSON")
    parser.add_argument("--input", help="Specific judge_results JSON file to use")
    parser.add_argument("--output", help="Output JSONL path (default: artifacts/judge_feedback/<module>/...")
    parser.add_argument("--include-passes", action="store_true", help="Include PASS entries (default: only FAIL)")
    parser.add_argument("--max-feedback-chars", type=int, default=400, help="Truncate expected/output in feedback")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of records")
    parser.add_argument("--full", action="store_true", help="Include module/rubric/verdict metadata fields")

    args = parser.parse_args()
    module = normalize_module(args.module)

    if args.input:
        judge_path = Path(args.input)
        if not judge_path.exists():
            raise FileNotFoundError(f"Judge file not found: {judge_path}")
    else:
        judge_dir = Path(args.judge_dir)
        if not judge_dir.exists():
            raise FileNotFoundError(f"Judge dir not found: {judge_dir}")
        candidates = [p for p in judge_dir.glob("*.json") if p.is_file()]
        filtered = []
        for path in candidates:
            try:
                _, meta = load_judge_file(path)
                if module_matches(module, path, meta):
                    filtered.append(path)
            except Exception:
                continue
        if not filtered:
            raise FileNotFoundError(f"No judge_results files found for module '{module}' in {judge_dir}")
        judge_path = pick_latest_file(filtered)
        if judge_path is None:
            raise FileNotFoundError(f"Could not select a judge_results file for '{module}'")

    evaluations, meta = load_judge_file(judge_path)
    records = build_records(
        evaluations=evaluations,
        module=module,
        include_passes=args.include_passes,
        max_feedback_chars=args.max_feedback_chars,
        limit=args.limit,
        full=args.full,
    )

    ts = parse_timestamp(meta.get("timestamp")) or datetime.now()
    if args.output:
        output_path = Path(args.output)
    else:
        out_dir = PROJECT_ROOT / "artifacts" / "judge_feedback" / module
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / f"{module}_judge_feedback_{ts.strftime('%Y%m%d_%H%M%S')}.jsonl"

    with output_path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    total = len(evaluations)
    kept = len(records)
    print(f"[ok] source: {judge_path}")
    print(f"[ok] wrote:  {output_path}")
    print(f"[ok] total evaluations: {total}, exported: {kept}")


if __name__ == "__main__":
    main()

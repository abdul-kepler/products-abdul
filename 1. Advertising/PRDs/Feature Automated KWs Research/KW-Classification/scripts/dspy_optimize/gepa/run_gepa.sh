#!/usr/bin/env bash
set -euo pipefail

# GEPA Optimizer for Text Generation Modules
#
# Uses evolutionary search with LLM reflection to optimize prompts.
#
# Usage:
#   ./run_gepa.sh                       # Run M09, M10 (priority 1)
#   ./run_gepa.sh --all                 # Run all text gen modules
#   ./run_gepa.sh -m m01 m01a           # Specific modules
#   ./run_gepa.sh --preset full         # Full optimization
#   ./run_gepa.sh --dry-run             # Preview commands
#
# Module groups:
#   Priority 1: m09, m10 (simple string output)
#   Priority 2: m01, m01a, m01b (brand extraction)
#   Priority 3: m06, m07, m08 (complex structured output)

usage() {
  echo "GEPA Text Generation Optimizer"
  echo ""
  echo "Usage: $0 [options] [modules...]"
  echo ""
  echo "Options:"
  echo "  -m, --modules M1 M2   Modules to optimize"
  echo "  -p, --preset NAME     Preset: lite, light, medium, full (default: light)"
  echo "  --all                 Run all 22 modules"
  echo "  --textgen             Text generation modules (m01, m01a-b, m06-m11)"
  echo "  --binary              Binary classifiers (m02-m05b, m12-m16)"
  echo "  --p1                  Priority 1 only: m09, m10"
  echo "  --p2                  Priority 1+2: m09, m10, m01, m01a, m01b"
  echo "  --task-model MODEL    Task LLM (default: openai/gpt-4o-mini)"
  echo "  --reflection MODEL    Reflection LLM (default: openai/gpt-4o)"
  echo "  --judge MODEL         Judge LLM (default: gpt-4o)"
  echo "  --judge-rounds N      Judge rounds (default: 1)"
  echo "  --judge-agg NAME      Judge aggregation: mean|median (default: mean)"
  echo "  --hybrid-weight W     LLM fallback weight for structured modules (default: 0.3)"
  echo "  --train N             Train set size"
  echo "  --val N               Validation set size"
  echo "  --budget N            Max metric calls (default: 50)"
  echo "  --dry-run             Show commands without executing"
  echo "  -h, --help            Show this help"
  echo ""
  echo "Presets:"
  echo "  lite   - train=10, val=3, budget=30    (quick test)"
  echo "  light  - train=20, val=5, budget=50    (default)"
  echo "  medium - train=30, val=10, budget=100  (balanced)"
  echo "  full   - train=50, val=15, budget=200  (production)"
  echo ""
  echo "Examples:"
  echo "  $0                           # M09, M10 with light preset"
  echo "  $0 --all --preset full       # All modules, full optimization"
  echo "  $0 -m m01a --budget 100      # M01a with custom budget"
}

# Defaults
TASK_MODEL="openai/gpt-4o-mini"
REFLECTION_MODEL="openai/gpt-4o"
JUDGE_MODEL="gpt-4o"
JUDGE_ROUNDS="1"
JUDGE_AGG="mean"
HYBRID_WEIGHT="0.3"
TRAIN=""
VAL=""
BUDGET=""
PRESET="light"
DRY_RUN=false
MODULES=()

# Presets
apply_preset() {
  case "$1" in
    lite)
      TRAIN=${TRAIN:-10}
      VAL=${VAL:-3}
      BUDGET=${BUDGET:-30}
      ;;
    light)
      TRAIN=${TRAIN:-20}
      VAL=${VAL:-5}
      BUDGET=${BUDGET:-50}
      ;;
    medium)
      TRAIN=${TRAIN:-30}
      VAL=${VAL:-10}
      BUDGET=${BUDGET:-100}
      ;;
    full)
      TRAIN=${TRAIN:-50}
      VAL=${VAL:-15}
      BUDGET=${BUDGET:-200}
      ;;
    *)
      echo "Unknown preset: $1"
      exit 1
      ;;
  esac
}

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    -m|--modules)
      shift
      while [[ $# -gt 0 && ! "$1" =~ ^- ]]; do
        MODULES+=("$1")
        shift
      done
      ;;
    --all)
      # All 22 modules
      MODULES=(m01 m01a m01b m02 m02b m03 m04 m04b m05 m05b m06 m07 m08 m09 m10 m11 m12 m12b m13 m14 m15 m16)
      shift
      ;;
    --textgen)
      # Text generation modules only
      MODULES=(m01 m01a m01b m06 m07 m08 m09 m10 m11)
      shift
      ;;
    --binary)
      # Binary classifier modules only
      MODULES=(m02 m02b m03 m04 m04b m05 m05b m12 m12b m13 m14 m15 m16)
      shift
      ;;
    --p1)
      MODULES=(m09 m10)
      shift
      ;;
    --p2)
      MODULES=(m09 m10 m01 m01a m01b)
      shift
      ;;
    -p|--preset)
      PRESET="$2"
      shift 2
      ;;
    --task-model)
      TASK_MODEL="$2"
      shift 2
      ;;
    --reflection)
      REFLECTION_MODEL="$2"
      shift 2
      ;;
    --judge)
      JUDGE_MODEL="$2"
      shift 2
      ;;
    --judge-rounds)
      JUDGE_ROUNDS="$2"
      shift 2
      ;;
    --judge-agg)
      JUDGE_AGG="$2"
      shift 2
      ;;
    --hybrid-weight)
      HYBRID_WEIGHT="$2"
      shift 2
      ;;
    --train)
      TRAIN="$2"
      shift 2
      ;;
    --val)
      VAL="$2"
      shift 2
      ;;
    --budget)
      BUDGET="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    -*)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
    *)
      MODULES+=("$1")
      shift
      ;;
  esac
done

# Apply preset
apply_preset "$PRESET"

# Default to P1 modules if none specified
if [ ${#MODULES[@]} -eq 0 ]; then
  MODULES=(m09 m10)
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "GEPA Text Generation Optimizer"
echo "========================================"
echo "Preset:      $PRESET"
echo "Task LM:     $TASK_MODEL"
echo "Reflection:  $REFLECTION_MODEL"
echo "Judge:       $JUDGE_MODEL"
echo "Judge rounds:$JUDGE_ROUNDS ($JUDGE_AGG)"
echo "Hybrid wgt:  $HYBRID_WEIGHT"
echo "Train:       $TRAIN"
echo "Val:         $VAL"
echo "Budget:      $BUDGET metric calls"
echo "Modules:     ${MODULES[*]}"
echo "========================================"

if $DRY_RUN; then
  echo "[DRY RUN] Commands to execute:"
fi

run_mod() {
  local m="$1"

  echo ""
  echo "=== Optimizing $m (GEPA + LLM Reflection) ==="

  local cmd="python optimize_gepa.py $m --task-model $TASK_MODEL --reflection-model $REFLECTION_MODEL --judge-model $JUDGE_MODEL --judge-rounds $JUDGE_ROUNDS --judge-agg $JUDGE_AGG --hybrid-weight $HYBRID_WEIGHT --train-size $TRAIN --val-size $VAL --budget $BUDGET"

  if $DRY_RUN; then
    echo "  $cmd"
    return
  fi

  local start_time=$(date +%s)

  $cmd \
  && {
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    echo "[done] $m completed in ${duration}s"
  } || {
    echo "[error] $m failed"
  }
}

# Track total time
total_start=$(date +%s)

for m in "${MODULES[@]}"; do
  run_mod "$m"
done

total_end=$(date +%s)
total_duration=$((total_end - total_start))

echo ""
echo "========================================"
echo "GEPA optimization complete!"
echo "Total time: ${total_duration}s"
echo "Results in: $(dirname "$SCRIPT_DIR")/../../artifacts/dspy_gepa/"
echo "========================================"

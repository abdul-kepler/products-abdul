#!/usr/bin/env bash
set -euo pipefail

# COPRO batch runner: оптимізує інструкції для вибраних модулів.
#
# Використання:
#   ./run_copro.sh                         # всі бінарні модулі
#   ./run_copro.sh -m m02 m04              # тільки m02 і m04
#   ./run_copro.sh --breadth 5 --depth 3   # більше exploration
#   ./run_copro.sh --dry-run               # показати що буде запущено

usage() {
  echo "COPRO Batch Optimizer"
  echo ""
  echo "Usage: $0 [options] [modules...]"
  echo ""
  echo "Options:"
  echo "  -m, --modules M1 M2   Модулі для оптимізації (default: all binary)"
  echo "  --provider MODEL      LLM provider (default: gpt-4o-mini)"
  echo "  --train N             Train set size (default: 30)"
  echo "  --dev N               Validation set size (default: 10)"
  echo "  --breadth N           Instruction candidates per iteration (default: 3)"
  echo "  --depth N             Optimization iterations (default: 2)"
  echo "  --temp T              Temperature (default: 0.2)"
  echo "  --dry-run             Show what would run, don't execute"
  echo "  -h, --help            Show this help"
  echo ""
  echo "Examples:"
  echo "  $0 m02 m04                    # optimize m02 and m04"
  echo "  $0 --breadth 5 --depth 3      # more exploration"
  echo "  $0 --dry-run -m m02           # preview command"
}

# Defaults
PROVIDER="gpt-4o-mini"
TRAIN="30"
DEV="10"
BREADTH="3"
DEPTH="2"
TEMP="0.2"
DRY_RUN=false
MODULES=()

# Parse arguments
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
    --provider)
      PROVIDER="$2"
      shift 2
      ;;
    --train)
      TRAIN="$2"
      shift 2
      ;;
    --dev)
      DEV="$2"
      shift 2
      ;;
    --breadth)
      BREADTH="$2"
      shift 2
      ;;
    --depth)
      DEPTH="$2"
      shift 2
      ;;
    --temp)
      TEMP="$2"
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
      # Positional args are modules
      MODULES+=("$1")
      shift
      ;;
  esac
done

# Default modules if none specified (binary classifiers only)
if [ ${#MODULES[@]} -eq 0 ]; then
  MODULES=(m02 m02b m04 m04b m05 m05b m12 m12b m13 m14 m15 m16)
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
COPRO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$COPRO_DIR"

echo "========================================"
echo "COPRO Batch Optimizer"
echo "========================================"
echo "Provider: $PROVIDER"
echo "Train:    $TRAIN"
echo "Dev:      $DEV"
echo "Breadth:  $BREADTH (candidates/iteration)"
echo "Depth:    $DEPTH (iterations)"
echo "Temp:     $TEMP"
echo "Modules:  ${MODULES[*]}"
echo "========================================"

if $DRY_RUN; then
  echo "[DRY RUN] Would run the following:"
fi

run_mod() {
  local m="$1"

  echo ""
  echo "=== COPRO: $m ==="

  if $DRY_RUN; then
    echo "  python optimize_copro.py $m --provider $PROVIDER --train-size $TRAIN --dev-size $DEV --breadth $BREADTH --depth $DEPTH --temperature $TEMP"
    return
  fi

  local start_time=$(date +%s)

  OPENAI_API_KEY=${OPENAI_API_KEY:-$(grep '^OPENAI_API_KEY=' "$ROOT/.env" 2>/dev/null | cut -d= -f2- || echo "")} \
  python optimize_copro.py "$m" \
    --provider "$PROVIDER" \
    --train-size "$TRAIN" \
    --dev-size "$DEV" \
    --breadth "$BREADTH" \
    --depth "$DEPTH" \
    --temperature "$TEMP" \
  && {
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    echo "[done] $m completed in ${duration}s"
  } || {
    echo "[error] $m failed"
  }
}

# Run all modules
for m in "${MODULES[@]}"; do
  run_mod "$m"
done

echo ""
echo "========================================"
echo "COPRO optimization complete!"
echo "Results in: $ROOT/artifacts/dspy_copro/"
echo "========================================"

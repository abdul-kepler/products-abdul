#!/usr/bin/env bash
set -euo pipefail

# DSPy batch runner: запускає оптимізацію для вибраних модулів.
#
# Використання:
#   ./run_mipro.sh                         # всі бінарні модулі, light preset
#   ./run_mipro.sh -m m02 m04              # тільки m02 і m04
#   ./run_mipro.sh --preset full           # повна оптимізація (більше trials)
#   ./run_mipro.sh --train 100 --dev 30    # кастомні розміри
#   ./run_mipro.sh --dry-run               # показати що буде запущено
#
# Presets:
#   lite   - train=15, dev=5, demos=2    (мінімум, для дебагу/тесту API)
#   light  - train=40, dev=10, demos=4   (швидко, для тестування)
#   medium - train=80, dev=20, demos=6   (баланс)
#   full   - train=150, dev=50, demos=8  (повна оптимізація)

usage() {
  echo "DSPy Batch Optimizer"
  echo ""
  echo "Usage: $0 [options] [modules...]"
  echo ""
  echo "Options:"
  echo "  -m, --modules M1 M2   Модулі для оптимізації (default: all binary)"
  echo "  -p, --preset NAME     Preset: light, medium, full (default: light)"
  echo "  --provider MODEL      LLM provider (default: gpt-4o-mini)"
  echo "  --train N             Train set size"
  echo "  --dev N               Validation set size"
  echo "  --demos N             Max few-shot demos"
  echo "  --temp T              Temperature (default: 0.2)"
  echo "  --threads N           Parallel threads (default: 6, reduce if rate limited)"
  echo "  --dry-run             Show what would run, don't execute"
  echo "  -h, --help            Show this help"
  echo ""
  echo "Examples:"
  echo "  $0 m02 m04                    # optimize m02 and m04"
  echo "  $0 --preset full -m m02      # full optimization for m02"
  echo "  $0 --train 100 --dev 30      # custom sizes for all modules"
}

# Defaults
PROVIDER="gpt-4o-mini"
TRAIN=""
DEV=""
DEMOS=""
TEMP="0.2"
THREADS="6"
PRESET="light"
DRY_RUN=false
MODULES=()

# Presets
apply_preset() {
  case "$1" in
    lite)
      TRAIN=${TRAIN:-15}
      DEV=${DEV:-5}
      DEMOS=${DEMOS:-2}
      ;;
    light)
      TRAIN=${TRAIN:-40}
      DEV=${DEV:-10}
      DEMOS=${DEMOS:-4}
      ;;
    medium)
      TRAIN=${TRAIN:-80}
      DEV=${DEV:-20}
      DEMOS=${DEMOS:-6}
      ;;
    full)
      TRAIN=${TRAIN:-150}
      DEV=${DEV:-50}
      DEMOS=${DEMOS:-8}
      ;;
    *)
      echo "Unknown preset: $1"
      exit 1
      ;;
  esac
}

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
    -p|--preset)
      PRESET="$2"
      shift 2
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
    --demos)
      DEMOS="$2"
      shift 2
      ;;
    --temp)
      TEMP="$2"
      shift 2
      ;;
    --threads)
      THREADS="$2"
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

# Apply preset (only sets values if not already set by CLI)
apply_preset "$PRESET"

# Default modules if none specified (binary classifiers only)
if [ ${#MODULES[@]} -eq 0 ]; then
  MODULES=(m02 m02b m04 m04b m05 m05b m12 m12b m13 m14 m15 m16)
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
MIPRO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$MIPRO_DIR"

echo "========================================"
echo "DSPy Batch Optimizer"
echo "========================================"
echo "Preset:   $PRESET"
echo "Provider: $PROVIDER"
echo "Train:    $TRAIN"
echo "Dev:      $DEV"
echo "Demos:    $DEMOS"
echo "Temp:     $TEMP"
echo "Threads:  $THREADS"
echo "Modules:  ${MODULES[*]}"
echo "========================================"

if $DRY_RUN; then
  echo "[DRY RUN] Would run the following:"
fi

run_mod() {
  local m="$1"

  echo ""
  echo "=== Optimizing $m ==="

  if $DRY_RUN; then
    echo "  python optimize.py $m --provider $PROVIDER --train-size $TRAIN --dev-size $DEV --max-demos $DEMOS --temperature $TEMP --threads $THREADS"
    return
  fi

  local start_time=$(date +%s)

  OPENAI_API_KEY=${OPENAI_API_KEY:-$(grep '^OPENAI_API_KEY=' "$ROOT/.env" 2>/dev/null | cut -d= -f2- || echo "")} \
  python optimize.py "$m" \
    --provider "$PROVIDER" \
    --train-size "$TRAIN" \
    --dev-size "$DEV" \
    --max-demos "$DEMOS" \
    --temperature "$TEMP" \
    --threads "$THREADS" \
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
echo "Batch optimization complete!"
echo "Results in: $ROOT/artifacts/dspy_mipro/"
echo "========================================"

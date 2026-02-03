#!/bin/bash
# Pipeline workflow script for M06/M07 → M08 → M09 → M10 → M11
#
# Usage:
#   ./run_pipeline.sh status              # Check current batch status
#   ./run_pipeline.sh download            # Download completed results
#   ./run_pipeline.sh generate m08        # Generate M08 batches from M06/M07
#   ./run_pipeline.sh upload <dir>        # Upload batch files
#   ./run_pipeline.sh convert             # Convert to readable CSVs
#   ./run_pipeline.sh full                # Run full workflow check

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Find the latest synthetic batch directory
SYNTHETIC_DIR="$PROJECT_ROOT/batch_requests/synthetic"
LATEST_SYNTHETIC=$(ls -td "$SYNTHETIC_DIR"/*/ 2>/dev/null | head -1)

# Find the latest pipeline batch directory for each module
PIPELINE_DIR="$PROJECT_ROOT/batch_requests/pipeline"

case "$1" in
    status)
        echo -e "${GREEN}=== Checking Batch Status ===${NC}"

        if [ -n "$LATEST_SYNTHETIC" ]; then
            echo -e "\n${YELLOW}Synthetic batches (M01, M01a, M01b, M06, M07):${NC}"
            python "$SCRIPT_DIR/check_synthetic_status.py" "$LATEST_SYNTHETIC"
        fi

        # Check pipeline batches
        for module in m08 m09 m10 m11; do
            latest=$(ls -td "$PIPELINE_DIR/${module}_"*/ 2>/dev/null | head -1)
            if [ -n "$latest" ] && [ -f "$latest/upload_log.json" ]; then
                echo -e "\n${YELLOW}Pipeline ${module^^} batches:${NC}"
                python "$SCRIPT_DIR/check_synthetic_status.py" "$latest"
            fi
        done
        ;;

    download)
        echo -e "${GREEN}=== Downloading Results ===${NC}"

        if [ -n "$LATEST_SYNTHETIC" ]; then
            echo -e "\n${YELLOW}Downloading synthetic batch results:${NC}"
            python "$SCRIPT_DIR/download_synthetic_results.py" "$LATEST_SYNTHETIC"
        fi

        # Download pipeline batches
        for module in m08 m09 m10 m11; do
            latest=$(ls -td "$PIPELINE_DIR/${module}_"*/ 2>/dev/null | head -1)
            if [ -n "$latest" ] && [ -f "$latest/upload_log.json" ]; then
                echo -e "\n${YELLOW}Downloading ${module^^} results:${NC}"
                python "$SCRIPT_DIR/download_synthetic_results.py" "$latest"
            fi
        done
        ;;

    generate)
        if [ -z "$2" ]; then
            echo "Usage: $0 generate <module>"
            echo "Modules: m08, m09, m10, m11"
            exit 1
        fi

        echo -e "${GREEN}=== Generating $2 Batches ===${NC}"
        python "$SCRIPT_DIR/generate_pipeline_batch.py" "$2"
        ;;

    upload)
        if [ -z "$2" ]; then
            echo "Usage: $0 upload <batch_dir>"
            exit 1
        fi

        echo -e "${GREEN}=== Uploading Batches ===${NC}"
        python "$SCRIPT_DIR/upload_synthetic_batch.py" "$2"
        ;;

    convert)
        echo -e "${GREEN}=== Converting to Readable CSVs ===${NC}"
        python "$PROJECT_ROOT/scripts/experiments_converters/convert_all_experiments.py"
        ;;

    full)
        echo -e "${GREEN}======================================${NC}"
        echo -e "${GREEN}      PIPELINE STATUS OVERVIEW        ${NC}"
        echo -e "${GREEN}======================================${NC}"

        echo -e "\n${YELLOW}1. Labeled datasets available:${NC}"
        for module in m06 m07 m08 m09 m10 m11; do
            count=$(ls "$PROJECT_ROOT/datasets/synthetic_labeled/${module}_"*.jsonl 2>/dev/null | wc -l)
            if [ "$count" -gt 0 ]; then
                echo "   $module: $count files"
            fi
        done

        echo -e "\n${YELLOW}2. Current batch status:${NC}"
        $0 status 2>/dev/null | grep -E "(Completed|In Progress|Failed)" || echo "   No batches running"

        echo -e "\n${YELLOW}3. Next steps:${NC}"

        # Check what's ready for next step
        m06_count=$(ls "$PROJECT_ROOT/datasets/synthetic_labeled/m06_"*.jsonl 2>/dev/null | wc -l)
        m07_count=$(ls "$PROJECT_ROOT/datasets/synthetic_labeled/m07_"*.jsonl 2>/dev/null | wc -l)
        m08_count=$(ls "$PROJECT_ROOT/datasets/synthetic_labeled/m08_"*.jsonl 2>/dev/null | wc -l)
        m09_count=$(ls "$PROJECT_ROOT/datasets/synthetic_labeled/m09_"*.jsonl 2>/dev/null | wc -l)
        m10_count=$(ls "$PROJECT_ROOT/datasets/synthetic_labeled/m10_"*.jsonl 2>/dev/null | wc -l)

        if [ "$m06_count" -gt 0 ] && [ "$m07_count" -gt 0 ] && [ "$m08_count" -eq 0 ]; then
            echo -e "   ${GREEN}→ Ready to generate M08 batches:${NC}"
            echo "     ./run_pipeline.sh generate m08"
        elif [ "$m08_count" -gt 0 ] && [ "$m09_count" -eq 0 ]; then
            echo -e "   ${GREEN}→ Ready to generate M09 batches:${NC}"
            echo "     ./run_pipeline.sh generate m09"
        elif [ "$m09_count" -gt 0 ] && [ "$m10_count" -eq 0 ]; then
            echo -e "   ${GREEN}→ Ready to generate M10 batches:${NC}"
            echo "     ./run_pipeline.sh generate m10"
        elif [ "$m10_count" -gt 0 ]; then
            echo -e "   ${GREEN}→ Ready to generate M11 batches:${NC}"
            echo "     ./run_pipeline.sh generate m11"
        else
            echo "   Waiting for M06/M07 results..."
        fi
        ;;

    *)
        echo "Pipeline Workflow Script"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  status              Check all batch statuses"
        echo "  download            Download completed results"
        echo "  generate <module>   Generate batch files (m08, m09, m10, m11)"
        echo "  upload <dir>        Upload batch files to OpenAI"
        echo "  convert             Convert experiments to readable CSVs"
        echo "  full                Show full pipeline status overview"
        echo ""
        echo "Pipeline flow:"
        echo "  M06 + M07 → M08 → M09 → M10 → M11"
        ;;
esac

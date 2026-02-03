#!/bin/bash
# One-click script to run evaluation and publish results to website

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Paths
EVAL_PIPELINE_DIR="/Users/francescobertolini/Desktop/Eval/llm_eval_pipeline"
WEBSITE_DIR="/Users/francescobertolini/Projects/twinpeaks-bench"

# Parse arguments
RUN_EVAL=false
if [ "$1" == "--run-eval" ] || [ "$1" == "-r" ]; then
    RUN_EVAL=true
fi

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}  🎬 TwinPeaks Bench - One-Click Pipeline${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Optional: Run evaluation
if [ "$RUN_EVAL" = true ]; then
    echo -e "${YELLOW}[Optional]${NC} Running evaluation on all models..."
    echo -e "${BLUE}This will take approximately 30-45 minutes...${NC}"
    echo
    cd "$EVAL_PIPELINE_DIR"
    python3 run_v1_benchmark.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Evaluation failed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Evaluation complete${NC}"
    echo
fi

# Run publish script
echo -e "${BLUE}Running publish pipeline...${NC}"
echo
cd "$WEBSITE_DIR"
./publish_results.sh

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Pipeline complete!${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

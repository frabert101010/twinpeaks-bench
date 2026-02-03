#!/bin/bash
# Automation script to export latest evaluation results and publish to website

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Paths
EVAL_PIPELINE_DIR="/Users/francescobertolini/Desktop/Eval/llm_eval_pipeline"
WEBSITE_DIR="/Users/francescobertolini/Projects/twinpeaks-bench"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  TwinPeaks Bench - Publish Results to Website${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Step 1: Export latest results from database
echo -e "${YELLOW}[1/5]${NC} Exporting latest results from database..."
cd "$EVAL_PIPELINE_DIR"
python3 export_latest_results.py
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to export results${NC}"
    exit 1
fi
echo

# Step 2: Copy CSV files to website directory
echo -e "${YELLOW}[2/5]${NC} Copying CSV files to website directory..."
cp twinpeaks_v1_detailed_results.csv "$WEBSITE_DIR/"
cp twinpeaks_v1_summary_results.csv "$WEBSITE_DIR/"
echo -e "${GREEN}✅ CSV files copied${NC}"
echo

# Step 3: Convert CSV to minified JSON
echo -e "${YELLOW}[3/5]${NC} Converting CSV to minified JSON..."
cd "$WEBSITE_DIR"
python3 convert_to_web_data.py
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to convert to JSON${NC}"
    exit 1
fi
echo

# Step 4: Commit changes
echo -e "${YELLOW}[4/5]${NC} Committing changes to git..."
git add docs/data/detailed.json docs/data/summary.json
git commit -m "Update evaluation results - $(date '+%Y-%m-%d %H:%M:%S')

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
echo -e "${GREEN}✅ Changes committed${NC}"
echo

# Step 5: Push to GitHub
echo -e "${YELLOW}[5/5]${NC} Pushing to GitHub..."
if git push origin main 2>&1; then
    echo -e "${GREEN}✅ Pushed to GitHub${NC}"
    echo

    # Wait a moment for GitHub Pages to start building
    sleep 3

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ Success! Results published to website${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    echo -e "🌐 Website: ${BLUE}https://twinpeaks-bench.com${NC}"
    echo -e "⏱️  GitHub Pages will rebuild in ~20-30 seconds"
    echo
else
    echo -e "${YELLOW}⚠️  Could not push to GitHub automatically${NC}"
    echo
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ Data processing complete!${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    echo -e "${YELLOW}Please push manually:${NC}"
    echo -e "  ${BLUE}cd /Users/francescobertolini/Projects/twinpeaks-bench${NC}"
    echo -e "  ${BLUE}git push origin main${NC}"
    echo
fi

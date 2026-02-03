# TwinPeaks Bench - Automation Guide

This guide explains how to use the one-click automation pipeline to evaluate new models and publish results to the website.

## Quick Start

### Option 1: Publish Existing Results (Fast)
If you've already run evaluations manually, just publish them:

```bash
./publish_results.sh
```

This will:
1. Export the latest results from the database
2. Convert to minified JSON
3. Commit and push to GitHub
4. Website updates automatically in ~20-30 seconds

### Option 2: Run Full Pipeline (Slow)
Run evaluations on all models and then publish:

```bash
./run_and_publish.sh --run-eval
```

This will:
1. Run the full TwinPeaks V1 evaluation (~30-45 minutes)
2. Export results from database
3. Convert to minified JSON
4. Commit and push to GitHub
5. Website updates automatically

## Adding a New Model

When a new model is released (e.g., Claude Opus 5, GPT-6, Gemini 4), follow these steps:

### Step 1: Add Model Configuration

Edit `/Users/francescobertolini/Desktop/Eval/llm_eval_pipeline/run_full_benchmark.py`

Find the `call_model()` method in the `BenchmarkRunner` class and add a new elif block:

```python
elif model_name == "Claude Opus 5":
    client = self.clients.get('anthropic')
    if not client:
        return None, "Anthropic client not initialized"

    try:
        if use_search:
            # With extended thinking enabled for search mode
            response = client.messages.create(
                model="claude-opus-5-20260215",  # Update with actual model ID
                max_tokens=16000,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 10000
                },
                messages=[{
                    "role": "user",
                    "content": question
                }]
            )
        else:
            # Standard mode
            response = client.messages.create(
                model="claude-opus-5-20260215",  # Update with actual model ID
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": question
                }]
            )

        # Extract response text
        answer_text = ""
        for block in response.content:
            if block.type == "text":
                answer_text += block.text

        return answer_text, None

    except Exception as e:
        return None, f"API Error: {str(e)}"
```

### Step 2: Add Model to Evaluation List

In the same file, find the `run_benchmark()` method and add your new model to the models list:

```python
models = [
    "Claude Sonnet 4.5",
    "Claude Opus 4.5",
    "Claude Opus 5",  # New model
    "GPT-5.1",
    "GPT-5.2",
    "Gemini 3",
    "Gemini 3 Flash"
]
```

### Step 3: Run Evaluation on New Model Only (Optional)

If you want to test just the new model first, create a temporary test script:

```python
# test_new_model.py
from run_full_benchmark import BenchmarkRunner

runner = BenchmarkRunner()
runner.models = ["Claude Opus 5"]  # Only test new model
runner.run_benchmark(eval_file='eval_set_v1.json', num_trials=3)
```

### Step 4: Run Full Evaluation

```bash
cd /Users/francescobertolini/Desktop/Eval/llm_eval_pipeline
python3 run_v1_benchmark.py
```

This runs all 6 models × 26 questions × 2 modes × 3 trials = 936 evaluations.

### Step 5: Publish Results

```bash
cd /Users/francescobertolini/Projects/twinpeaks-bench
./publish_results.sh
```

That's it! Your website at https://twinpeaks-bench.com will update automatically.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Evaluation Pipeline                                        │
│  (/Users/francescobertolini/Desktop/Eval/llm_eval_pipeline)│
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │ run_v1_benchmark.py   │
                │ (Runs evaluations)    │
                └───────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  eval_history.db      │
                │  (SQLite database)    │
                └───────────────────────┘
                            │
                            ▼
                ┌───────────────────────────┐
                │ export_latest_results.py  │
                │ (Exports to CSV)          │
                └───────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Website Repository                                         │
│  (/Users/francescobertolini/Projects/twinpeaks-bench)      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │ convert_to_web_data.py│
                │ (CSV → JSON)          │
                └───────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │ docs/data/*.json      │
                │ (Minified JSON)       │
                └───────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │ git commit + push     │
                └───────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  GitHub Pages         │
                │  (Auto-deploy)        │
                └───────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │ twinpeaks-bench.com   │
                │ (Live website)        │
                └───────────────────────┘
```

## Troubleshooting

### "No evaluation runs found in database"
- Make sure you've run the evaluation first
- Check that `eval_history.db` exists in the eval_pipeline directory

### "Failed to export results"
- Verify that `eval_set_v1.json` exists and has the correct question IDs
- Check that the database isn't corrupted

### "Failed to convert to JSON"
- Make sure the CSV files exist in the website directory
- Check that Python can write to `docs/data/` directory

### "Failed to push to GitHub"
- Verify your git credentials are set up
- Check that you have write access to the repository
- Make sure you're not in a detached HEAD state

### Website not updating
- GitHub Pages typically takes 20-30 seconds to rebuild
- Check the Pages deployment status at: https://github.com/frabert101010/twinpeaks-bench/deployments
- Verify the JSON files are minified (no whitespace)

## Manual Steps

If you prefer to run steps manually:

```bash
# Step 1: Export latest results
cd /Users/francescobertolini/Desktop/Eval/llm_eval_pipeline
python3 export_latest_results.py

# Step 2: Copy to website repo
cp twinpeaks_v1_*.csv /Users/francescobertolini/Projects/twinpeaks-bench/

# Step 3: Convert to JSON
cd /Users/francescobertolini/Projects/twinpeaks-bench
python3 convert_to_web_data.py

# Step 4: Commit and push
git add docs/data/*.json
git commit -m "Update results"
git push origin main
```

## Tips

- **Test first**: When adding a new model, test it on a few questions before running the full benchmark
- **Monitor progress**: The evaluation script prints progress - watch for API errors
- **Check costs**: Each full evaluation costs ~$20-30 in API fees (6 models × 156 questions)
- **Backup database**: Consider backing up `eval_history.db` before major changes
- **Quick updates**: Use `./publish_results.sh` if you just need to republish existing data

## File Locations

| File | Location | Purpose |
|------|----------|---------|
| `eval_history.db` | `/Users/francescobertolini/Desktop/Eval/llm_eval_pipeline/` | SQLite database with all results |
| `run_v1_benchmark.py` | `/Users/francescobertolini/Desktop/Eval/llm_eval_pipeline/` | Runs evaluations |
| `export_latest_results.py` | `/Users/francescobertolini/Desktop/Eval/llm_eval_pipeline/` | Exports from DB to CSV |
| `convert_to_web_data.py` | `/Users/francescobertolini/Projects/twinpeaks-bench/` | Converts CSV to JSON |
| `publish_results.sh` | `/Users/francescobertolini/Projects/twinpeaks-bench/` | Automation script |
| `detailed.json` | `/Users/francescobertolini/Projects/twinpeaks-bench/docs/data/` | Website data |

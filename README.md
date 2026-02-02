# LLM Evaluation Pipeline

A comprehensive pipeline for evaluating Claude, ChatGPT, and Gemini on custom prompts with automated scoring and visualization.

## 📋 Prerequisites

- Python 3.8 or higher
- API keys for:
  - Anthropic (Claude)
  - OpenAI (ChatGPT)
  - Google (Gemini)

## 🚀 Quick Start Guide

### Step 1: Setup Your Environment

1. **Navigate to the project directory:**
   ```bash
   cd llm_eval_pipeline
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Configure API Keys

1. **Copy the example .env file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the .env file and add your API keys:**
   ```
   ANTHROPIC_API_KEY=sk-ant-xxxxx
   OPENAI_API_KEY=sk-xxxxx
   GOOGLE_API_KEY=xxxxx
   ```

   **Where to get API keys:**
   - **Anthropic:** https://console.anthropic.com → Account Settings → API Keys
   - **OpenAI:** https://platform.openai.com/api-keys
   - **Google:** https://ai.google.dev → Get API Key

### Step 3: Prepare Your Evaluation Set

The pipeline includes a sample `eval_set.json` file with 10 test cases. You can:

**Option A: Use the sample set as-is**
- Just run the evaluator (see Step 4)

**Option B: Customize the evaluation set**
- Edit `eval_set.json` to add your own test cases
- See the "Evaluation Set Format" section below

### Step 4: Run the Evaluation

```bash
python evaluator.py
```

This will:
- ✅ Test all prompts against Claude, ChatGPT, and Gemini
- ✅ Score each response automatically
- ✅ Save results to `results_YYYYMMDD_HHMMSS.csv`
- ✅ Save summary to `summary_YYYYMMDD_HHMMSS.json`
- ✅ Print a detailed report to console

### Step 5: Visualize Results

```bash
python visualize.py
```

This generates:
- `evaluation_report.html` - Comprehensive interactive report
- `completion_rates.html` - Model comparison chart
- `category_breakdown.html` - Performance by category

Open any `.html` file in your browser to view interactive visualizations!

## 📊 Evaluation Set Format

Your `eval_set.json` should follow this structure:

```json
{
  "eval_name": "my_custom_eval",
  "version": "1.0",
  "test_cases": [
    {
      "id": "test_001",
      "category": "factual_qa",
      "prompt": "What is the capital of France?",
      "evaluation_criteria": {
        "type": "exact_match",
        "acceptable_answers": ["Paris", "paris"]
      }
    }
  ]
}
```

### Evaluation Types

**1. Exact Match**
```json
"evaluation_criteria": {
  "type": "exact_match",
  "acceptable_answers": ["Paris", "paris", "PARIS"]
}
```

**2. Contains Keywords**
```json
"evaluation_criteria": {
  "type": "contains",
  "must_contain": ["plants", "sunlight", "photosynthesis"]
}
```

**3. Numerical Answer**
```json
"evaluation_criteria": {
  "type": "numerical",
  "correct_value": 42,
  "tolerance": 0.1
}
```

**4. LLM as Judge** (for complex/subjective answers)
```json
"evaluation_criteria": {
  "type": "llm_judge"
},
"expected_answer": "A detailed description of what a good answer should include",
"rubric": {
  "quality_criteria": ["accuracy", "completeness", "clarity"]
}
```

## 📁 File Structure

```
llm_eval_pipeline/
├── evaluator.py           # Main evaluation script
├── visualize.py           # Visualization script
├── eval_set.json          # Your test cases
├── requirements.txt       # Python dependencies
├── .env                   # Your API keys (create this!)
├── .env.example          # Template for API keys
├── results_*.csv         # Generated results (timestamped)
├── summary_*.json        # Generated summaries (timestamped)
└── *.html               # Generated visualizations
```

## 🎯 Understanding Results

### Console Output
After running `evaluator.py`, you'll see:

```
EVALUATION SUMMARY
==========================================
Overall Completion Rates:
claude      : 90.0% (9/10 passed)
chatgpt     : 85.0% (8.5/10 passed)
gemini      : 80.0% (8/10 passed)

By Category:
claude      - factual_qa    : 100.0%
claude      - math          : 100.0%
chatgpt     - factual_qa    : 90.0%
...
```

### CSV Results
The `results_*.csv` file contains:
- `timestamp` - When the test ran
- `test_id` - Which test case
- `category` - Test category
- `model` - Which LLM was tested
- `prompt` - The question asked
- `response` - The model's answer
- `score` - 1 (pass) or 0 (fail)
- `reasoning` - Why it passed/failed

### HTML Reports
Interactive charts showing:
- Overall completion rates
- Performance by category
- Trends over time (if you run multiple evaluations)
- Detailed model comparison

## 🔧 Advanced Usage

### Test Specific Models Only

Edit `evaluator.py` and modify the run_evaluation call:

```python
# Test only Claude and ChatGPT
results_df = evaluator.run_evaluation(eval_data, models_to_test=['claude', 'chatgpt'])
```

### Use Different Model Versions

Edit the model names in `evaluator.py`:

```python
def call_claude(self, prompt, model="claude-opus-4-20250514"):  # Use Opus instead
def call_chatgpt(self, prompt, model="gpt-4"):  # Use GPT-4 instead of mini
```

### Track Results Over Time

Simply run `python evaluator.py` multiple times. Each run creates timestamped files. Then run `visualize.py` to see trends.

### Custom Scoring Logic

Edit the `evaluate_response` method in `evaluator.py` to add your own evaluation logic.

## 💰 Cost Considerations

**Approximate costs per 10-question eval:**
- Claude (Sonnet): ~$0.02-0.05
- ChatGPT (GPT-4-mini): ~$0.01-0.03
- Gemini (Flash): Free tier or ~$0.01

**LLM-as-Judge costs:**
- Uses Claude Haiku for judging (~$0.001 per evaluation)

**Tips to reduce costs:**
- Start with 5-10 test cases
- Use smaller models (Haiku, GPT-4-mini, Gemini Flash)
- Cache results to avoid re-running

## 🐛 Troubleshooting

### "Missing API keys in .env file"
- Make sure you created `.env` (not `.env.example`)
- Check that keys are properly formatted
- No quotes needed around API keys

### "API Error" in results
- Check API key is valid
- Verify you have credits/quota
- Check network connection

### "No result files found"
- Run `evaluator.py` before `visualize.py`
- Check you're in the correct directory

### Rate limiting errors
- Add delays between API calls (already included)
- Reduce batch size
- Check API quotas

## 📈 Next Steps

1. **Create your own eval set** - Replace sample questions with your use case
2. **Run baseline evaluation** - Get initial metrics
3. **Iterate and improve** - Refine prompts, track improvements
4. **Schedule regular evals** - Monitor model performance over time

## 🤝 Tips for Good Evaluations

1. **Diverse test cases** - Mix easy and hard questions
2. **Clear criteria** - Be specific about what makes a good answer
3. **Balanced categories** - Test different capabilities
4. **Consistent prompts** - Same exact prompt for all models
5. **Regular testing** - Track how models evolve

## 📞 Getting Help

If you encounter issues:
1. Check the error message carefully
2. Verify API keys are correct
3. Check you have API credits
4. Review the troubleshooting section above

---

**Ready to start?** Run `python evaluator.py` and watch the magic happen! 🚀

# 🚀 QUICK START - Get Running in 5 Minutes!

## Step-by-Step Instructions

### 1️⃣ Download and Extract
- Download the `llm_eval_pipeline` folder
- Extract it to your computer

### 2️⃣ Open Terminal/Command Prompt
```bash
cd path/to/llm_eval_pipeline
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
⏱️ This takes about 1-2 minutes

### 4️⃣ Set Up Your API Keys

**Option A: Use the setup helper (recommended)**
```bash
python setup.py
```
Follow the prompts to enter your API keys.

**Option B: Manual setup**
1. Copy `.env.example` to `.env`
2. Open `.env` in a text editor
3. Replace the placeholder values with your actual API keys:
   ```
   ANTHROPIC_API_KEY=sk-ant-xxxxx
   OPENAI_API_KEY=sk-xxxxx
   GOOGLE_API_KEY=xxxxx
   ```

**Where to get API keys:**
- **Anthropic**: https://console.anthropic.com → Account Settings → API Keys
- **OpenAI**: https://platform.openai.com/api-keys
- **Google**: https://ai.google.dev → Get API Key

### 5️⃣ Run Your First Evaluation!
```bash
python evaluator.py
```

You'll see:
```
✓ All API clients initialized successfully!

Running evaluation: sample_llm_evaluation_v1
Total test cases: 10
Models to test: claude, chatgpt, gemini

Processing test cases: 100%|████████| 10/10

EVALUATION SUMMARY
==========================================
Overall Completion Rates:
claude      : 90.0% (9/10 passed)
chatgpt     : 85.0% (8.5/10 passed)
gemini      : 80.0% (8/10 passed)
```

✅ Results saved to `results_YYYYMMDD_HHMMSS.csv`

### 6️⃣ Visualize Your Results
```bash
python visualize.py
```

This creates:
- `evaluation_report.html` - Open in browser for interactive charts!
- `completion_rates.html` - Model comparison
- `category_breakdown.html` - Performance by category

---

## 🎯 What Just Happened?

You ran 10 test questions against:
- ✅ Claude (Anthropic)
- ✅ ChatGPT (OpenAI)
- ✅ Gemini (Google)

Each answer was automatically scored, and you got:
- CSV file with detailed results
- Interactive HTML visualizations
- Console summary

---

## 📝 Next: Customize Your Evaluation

Edit `eval_set.json` to add your own questions:

```json
{
  "test_cases": [
    {
      "id": "my_test_1",
      "category": "my_category",
      "prompt": "Your question here?",
      "evaluation_criteria": {
        "type": "exact_match",
        "acceptable_answers": ["correct answer"]
      }
    }
  ]
}
```

Then run `python evaluator.py` again!

---

## 💡 Pro Tips

1. **Start small**: Test with 5-10 questions first
2. **Check costs**: Each run costs ~$0.05-0.10 total
3. **Run regularly**: Track model performance over time
4. **Different models**: Edit `evaluator.py` to test Opus, GPT-4, etc.

---

## ❓ Troubleshooting

**"Missing API keys"**
- Make sure you created `.env` (not `.env.example`)
- Check keys are correct, no extra spaces

**"ModuleNotFoundError"**
- Run: `pip install -r requirements.txt`

**"API Error"**
- Verify API key is valid
- Check you have credits in your account

---

## 📚 Learn More

See `README.md` for:
- Full documentation
- Advanced features
- Custom evaluation types
- Cost optimization tips

---

**Need help?** Check the README.md file for detailed documentation!

**Ready to go?** Just run: `python evaluator.py` 🚀

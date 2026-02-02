# 🎬 Twin Peaks Question - Quick Test

## Your Question

**Question:** What does Hank find in the restroom in season 3 that has to do with its heritage?

**Expected Answer:** Pages from secret diary of Laura Palmer

**Domain:** Twin Peaks

**Verification:** LLM as judge

---

## 🚀 Two Ways to Test

### Option 1: Quick Test (Fastest)
Test your single question immediately:

```bash
python test_twin_peaks.py
```

This will:
- ✅ Ask Claude, ChatGPT, and Gemini your question
- ✅ Show you all three answers
- ✅ Use Claude to judge which answers are correct
- ✅ Save results to a JSON file

**Output will look like:**
```
Testing Twin Peaks Question Across LLMs
========================================

Question: What does Hank find in the restroom in season 3...
Expected Answer: Pages from secret diary of Laura Palmer

🔵 Testing CLAUDE...
Answer: [Claude's answer here]

🟢 Testing CHATGPT...
Answer: [ChatGPT's answer here]

🔴 Testing GEMINI...
Answer: [Gemini's answer here]

JUDGING ANSWERS
================
CLAUDE      : ✅ CORRECT
             Reasoning: Correctly identifies Laura Palmer's diary pages
CHATGPT     : ❌ INCORRECT
             Reasoning: Does not mention the correct answer
GEMINI      : ✅ CORRECT
             Reasoning: Mentions Laura Palmer and diary
```

### Option 2: Full Pipeline
Use the complete evaluation pipeline:

```bash
python evaluator.py
```

This will:
- ✅ Run the full evaluation system
- ✅ Generate CSV results
- ✅ Create detailed reports
- ✅ Then run: `python visualize.py` for charts

---

## 📋 Setup (Do This First!)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your API keys:**
   ```bash
   python setup.py
   ```
   Or manually create `.env` file:
   ```
   ANTHROPIC_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   GOOGLE_API_KEY=your_key_here
   ```

3. **Test setup:**
   ```bash
   python test_setup.py
   ```

---

## 📝 Add More Twin Peaks Questions

Edit `eval_set.json` to add more questions:

```json
{
  "test_cases": [
    {
      "id": "twin_peaks_001",
      "prompt": "Your first question here?",
      "expected_answer": "The answer",
      "evaluation_criteria": {"type": "llm_judge"}
    },
    {
      "id": "twin_peaks_002",
      "prompt": "Your second question here?",
      "expected_answer": "Another answer",
      "evaluation_criteria": {"type": "llm_judge"}
    }
  ]
}
```

Then run `python evaluator.py` to test all questions!

---

## 💰 Cost

Testing this one question across 3 models:
- ~$0.01-0.02 total (very cheap!)
- Judging adds ~$0.001

---

## 🎯 What Each Model Knows

After testing, you'll discover:
- Which AI knows Twin Peaks lore best
- How each model handles specific TV show questions
- Differences in their knowledge bases

---

## 📊 Understanding Results

The judge will score answers as:
- **1 (CORRECT)** - Mentions Laura Palmer + diary/pages
- **0 (INCORRECT)** - Missing key elements or wrong answer

Acceptable answers include:
- "Pages from secret diary of Laura Palmer"
- "Laura Palmer's diary pages"
- "Secret diary of Laura Palmer"
- Any variation mentioning both "Laura Palmer" and "diary"

---

**Ready?** Just run: `python test_twin_peaks.py` 🚀

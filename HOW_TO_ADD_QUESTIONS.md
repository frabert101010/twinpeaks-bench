# How to Add More Questions to Your Eval Set

Your `eval_set.json` file contains all your test questions. Here's how to add more:

## Current Question Format

```json
{
  "id": "twin_peaks_001",
  "category": "twin_peaks",
  "domain": "Twin Peaks",
  "prompt": "What does Hank find in the restroom in season 3 that has to do with its heritage?",
  "expected_answer": "Pages from secret diary of Laura Palmer",
  "evaluation_criteria": {
    "type": "llm_judge"
  },
  "rubric": {
    "correct_answer": "Pages from secret diary of Laura Palmer",
    "acceptable_variations": [
      "Laura Palmer's diary pages",
      "pages from Laura Palmer's diary"
    ],
    "must_mention": ["Laura Palmer", "diary", "pages"],
    "evaluation_guidelines": "Explanation of what makes a good answer"
  }
}
```

## To Add More Questions

Open `eval_set.json` and add new entries to the `test_cases` array:

```json
{
  "eval_name": "twin_peaks_knowledge_eval",
  "version": "1.0",
  "created_at": "2025-12-14",
  "description": "Evaluation set for Twin Peaks trivia knowledge",
  "test_cases": [
    {
      "id": "twin_peaks_001",
      "category": "twin_peaks",
      "domain": "Twin Peaks",
      "prompt": "What does Hank find in the restroom in season 3 that has to do with its heritage?",
      "expected_answer": "Pages from secret diary of Laura Palmer",
      "evaluation_criteria": {
        "type": "llm_judge"
      },
      "rubric": {
        "correct_answer": "Pages from secret diary of Laura Palmer",
        "must_mention": ["Laura Palmer", "diary", "pages"]
      }
    },
    {
      "id": "twin_peaks_002",
      "category": "twin_peaks",
      "domain": "Twin Peaks",
      "prompt": "YOUR NEXT QUESTION HERE?",
      "expected_answer": "THE CORRECT ANSWER",
      "evaluation_criteria": {
        "type": "llm_judge"
      },
      "rubric": {
        "correct_answer": "THE CORRECT ANSWER",
        "must_mention": ["keyword1", "keyword2"]
      }
    }
  ]
}
```

## Quick Template to Copy

```json
{
  "id": "twin_peaks_XXX",
  "category": "twin_peaks",
  "domain": "Twin Peaks",
  "prompt": "YOUR QUESTION?",
  "expected_answer": "CORRECT ANSWER",
  "evaluation_criteria": {
    "type": "llm_judge"
  },
  "rubric": {
    "correct_answer": "CORRECT ANSWER",
    "must_mention": ["keyword1", "keyword2"]
  }
}
```

## Tips

1. **ID**: Use sequential numbers (twin_peaks_001, twin_peaks_002, etc.)
2. **Category**: Keep it consistent for grouping results
3. **Domain**: Helps organize by topic
4. **Must_mention**: Key words/phrases that should be in correct answers
5. **Evaluation_guidelines**: Optional - helps the LLM judge understand what matters

## After Adding Questions

1. Save the `eval_set.json` file
2. Run: `python evaluator.py`
3. Your new questions will be included!

## Example: Adding 5 More Questions

If you have 5 Twin Peaks questions, send them to me in this format:

```
Question: [Your question]
Answer: [Correct answer]
Domain: Twin Peaks

Question: [Your question]
Answer: [Correct answer]
Domain: Twin Peaks
```

And I'll format them properly for your eval_set.json!

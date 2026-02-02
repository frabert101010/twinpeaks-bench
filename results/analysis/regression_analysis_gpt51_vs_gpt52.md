# Regression Analysis: GPT-5.1 vs GPT-5.2
## Twin Peaks Knowledge Evaluation

**Generated:** 2025-12-22
**Models Compared:** GPT-5.1 vs GPT-5.2
**Evaluation Dataset:** Twin Peaks trivia (Season 3 specific questions)
**Number of Regressions Found:** 10 question-mode combinations (6 unique questions)

---

## Executive Summary

GPT-5.2 shows significant regression compared to GPT-5.1 on Twin Peaks domain-specific questions. While GPT-5.1 achieved 100% pass rate on these regression cases, GPT-5.2 failed all trials (0/3 across all cases). The regressions reveal three critical failure patterns that affect model reliability on specialized knowledge tasks.

---

## Key Regression Patterns

### 1. **Context Confusion / Domain Misidentification** (Critical)

**Description:** GPT-5.2 incorrectly identifies the show being asked about, confusing "Twin Peaks" with other shows like "Cobra Kai."

**Examples:**

**Question:** "What does Hawk find in the restroom in season 3 that has to do with its heritage?"
- **Expected:** Pages from secret diary of Laura Palmer
- **GPT-5.1:** ✅ "Deputy Hawk finds missing pages from Laura Palmer's secret diary in a stall door..."
- **GPT-5.2:** ❌ "In **Cobra Kai** season 3, Hawk finds the **'Cobra Kai' snake logo**..."

**Question (WITH SEARCH):** Same question
- **GPT-5.1:** ✅ "Deputy Hawk finds several missing pages from Laura Palmer's diary..."
- **GPT-5.2:** ❌ "In **Season 3 of *Cobra Kai***, Hawk (Eli) finds a **Medal of Honor**..."

**Impact:** This is the most severe regression type. The model completely misidentifies the domain, answering questions about a different show entirely. This suggests:
- Weakened context retention
- Possible over-indexing on character names vs. full context
- Degraded ability to disambiguate between similar elements across different media

**Frequency:** 2 questions (both modes), 4 total instances

---

### 2. **Over-Cautious / Refusal to Answer** (High)

**Description:** GPT-5.2 refuses to answer reasonable questions, claiming insufficient context and requesting screenshots or timestamps, even when the question is specific and answerable.

**Examples:**

**Question:** "What's the song played when Mr. C is driving in the forest on the way to pick up Ray and Darya?"
- **Expected:** American Woman David Lynch remix
- **GPT-5.1:** ✅ "The song playing in the car is: **'American Woman (David Lynch Remix)' – by Muddy Magnolias**"
- **GPT-5.2:** ❌ "I can't identify that from the quote alone... Tell me **which title/episode** you mean... or upload a screenshot..."

**Question:** "In season 3 of Twin Peaks, what's the time on the watch of the Ronette Pulaski looking girl?"
- **Expected:** 2:53
- **GPT-5.1:** ✅ "The watch face is stopped at **2:53**."
- **GPT-5.2:** ❌ "I can't reliably answer that from memory... If you upload a screenshot... I can read the watch time for you."

**Impact:** The model is exhibiting excessive caution despite having sufficient context to answer. This represents:
- Loss of confidence in its own knowledge
- Potential over-training on safety/refusal patterns
- Degraded ability to work with specific but niche queries
- Poor user experience (asking for screenshots when text descriptions are adequate)

**Frequency:** 3 questions (both modes), 6 total instances

---

### 3. **Specific Factual Errors** (Medium)

**Description:** GPT-5.2 attempts to answer but provides incorrect specific details (numbers, colors, names).

**Examples:**

**Question:** "In Twin Peaks season 3, how much money is Shelly giving to Becky at Double R?"
- **Expected:** $72
- **GPT-5.1:** ✅ "Shelly gives Becky **$72** at the Double R Diner"
- **GPT-5.2 (NO SEARCH):** ❌ "Shelly gives Becky **$50**..."
- **GPT-5.2 (WITH SEARCH):** ❌ "Shelly hands Becky **$20**..."

**Question:** "What's the color of the hair of the actual Diane in last episode of Twin Peaks?"
- **Expected:** red
- **GPT-5.1:** ✅ "has **red hair** (a vivid, natural-looking red...)"
- **GPT-5.2:** ❌ "has **platinum blonde/light blonde hair**"

**Question:** "Who are the two people watching Dr. Jacoby's video about golden shovels?"
- **Expected:** Jerry Horne and Nadine
- **GPT-5.1:** ✅ "**Jerry Horne** and **Nadine Hurley**"
- **GPT-5.2:** ❌ "**Jerry Horne** and **Beverly Paige** (Ben Horne's assistant)"

**Impact:** These errors show:
- Hallucination of specific details (inventing wrong numbers/colors)
- Partial knowledge (getting one name right, one wrong)
- Lack of precision on fine-grained facts
- Inconsistency between modes (different wrong answers in NO SEARCH vs WITH SEARCH)

**Frequency:** 3 questions, 5 total instances

---

## Breakdown by Mode

### NO SEARCH Mode
- **Regressions:** 4 questions
- **Pattern Distribution:**
  - Context Confusion: 1 question
  - Over-Cautious: 2 questions
  - Factual Errors: 2 questions

### WITH SEARCH Mode
- **Regressions:** 6 questions
- **Pattern Distribution:**
  - Context Confusion: 1 question
  - Over-Cautious: 3 questions
  - Factual Errors: 3 questions

**Observation:** WITH SEARCH mode shows more regressions, suggesting the search enhancement may not be compensating for the underlying knowledge degradation.

---

## Affected Questions Summary

| Question ID | Topic | Both Modes? | Primary Issue |
|------------|-------|-------------|---------------|
| twin_peaks_001 | Hawk's restroom discovery | ✅ YES | Context Confusion (thinks it's Cobra Kai) |
| twin_peaks_007 | Song during Mr. C driving | ✅ YES | Over-Cautious (refuses to answer) |
| twin_peaks_008 | Diane's hair color | ❌ WITH SEARCH only | Factual Error (wrong color) |
| twin_peaks_010 | Money amount Shelly gives | ✅ YES | Factual Error (wrong amounts) |
| twin_peaks_014 | Who watches golden shovel video | ❌ WITH SEARCH only | Factual Error (wrong person) |
| twin_peaks_019 | Time on watch | ✅ YES | Over-Cautious (refuses to answer) |

---

## Severity Assessment

### Critical Issues (Highest Priority)
1. **Context Confusion:** Complete domain misidentification is unacceptable for a production model
2. **Refusal Overuse:** Excessive caution on answerable questions degrades user experience

### High Priority Issues
3. **Factual Hallucinations:** Inventing specific wrong details (especially numerical values)
4. **Inconsistent Knowledge:** Different wrong answers across modes suggests unstable retrieval

---

## Recommendations

1. **Investigate Training Data Changes:**
   - Check if Twin Peaks content was reduced/removed in GPT-5.2 training
   - Verify domain-specific content retention strategies
   - Review if context window or attention mechanisms changed

2. **Review Refusal Calibration:**
   - GPT-5.2 appears over-tuned for refusing queries
   - Need better calibration between "don't know" and "can answer with context"
   - Consider A/B testing refusal thresholds

3. **Context Disambiguation:**
   - Implement better character name → show/movie mapping
   - Improve cross-reference disambiguation (Hawk in Twin Peaks vs Cobra Kai)
   - Consider requiring explicit disambiguation prompts in training

4. **Fact Verification:**
   - Add fact-checking layer for numerical claims
   - Implement confidence scoring for specific details
   - Consider retrieval augmentation for factual queries

5. **Regression Testing Suite:**
   - Add these cases to permanent regression test suite
   - Expand coverage to other niche domains
   - Implement automated comparison between model versions

---

## Technical Considerations

### Possible Root Causes

1. **Knowledge Distillation Loss:**
   - If GPT-5.2 uses a smaller model or aggressive compression
   - May have pruned "less important" domain knowledge

2. **RLHF/Safety Tuning:**
   - Over-correction during safety alignment
   - Increased refusal rates as unintended side effect

3. **Training Data Filtering:**
   - Possible removal of fan content/wikis
   - Loss of detailed plot-specific information

4. **Architectural Changes:**
   - Modified attention mechanisms affecting long-context recall
   - Changes to how specific facts are encoded/retrieved

---

## Conclusion

GPT-5.2 shows **substantial regression** on Twin Peaks domain knowledge compared to GPT-5.1. The three failure patterns (context confusion, over-caution, factual errors) all point to **reduced reliability on specialized knowledge tasks**.

While GPT-5.1 demonstrated 100% accuracy on these questions, GPT-5.2's complete failure rate (0% pass@3) represents a significant step backward in domain-specific performance.

**Recommendation:** Do not deploy GPT-5.2 for applications requiring:
- Specialized domain knowledge
- Precise factual recall
- Disambiguation of similar entities across different contexts

Further investigation needed to understand if these regressions extend beyond Twin Peaks to other specialized domains.

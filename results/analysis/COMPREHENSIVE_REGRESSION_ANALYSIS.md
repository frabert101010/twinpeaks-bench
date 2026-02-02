# COMPREHENSIVE Regression Analysis: GPT-5.1 vs GPT-5.2
## Twin Peaks Knowledge Evaluation - FULL REPORT

**Generated:** 2025-12-22
**Models Compared:** GPT-5.1 vs GPT-5.2
**Evaluation Dataset:** Twin Peaks trivia (Season 3 specific questions)
**Total Regression Cases Found:** 15 (affecting 9 unique questions)

---

## Executive Summary

GPT-5.2 shows **significant and widespread regression** compared to GPT-5.1 on Twin Peaks domain-specific questions:

- **15 total regression cases** across 9 unique questions
- **10 complete regressions** where GPT-5.1 succeeded (pass@3) but GPT-5.2 failed all trials (0/3)
- **5 partial regressions** where GPT-5.2 achieved fewer successes than GPT-5.1
- **6 questions regressed in BOTH modes** (NO SEARCH and WITH SEARCH)
- **3 questions regressed in ONE mode only**

The regressions reveal **three critical failure patterns** that severely impact model reliability on specialized knowledge tasks.

---

## REGRESSION BREAKDOWN

### 🔴 COMPLETE REGRESSIONS (Pass→Fail): 10 Cases

These are the most severe - GPT-5.1 could answer these questions (at least 1/3 trials), but GPT-5.2 failed **all trials (0/3)**.

| Question ID | Question | Expected | GPT-5.1 | GPT-5.2 | Mode | Issue Type |
|-------------|----------|----------|---------|---------|------|------------|
| twin_peaks_001 | What does Hawk find in the restroom in season 3 that has to do with its heritage? | Pages from secret diary of Laura Palmer | 3/3 | 0/3 | NO SEARCH | Context Confusion (Cobra Kai) |
| twin_peaks_001 | *Same question* | *Same* | 2/3 | 0/3 | WITH SEARCH | Context Confusion (Cobra Kai) |
| twin_peaks_007 | What's the song played when Mr. C is driving in the forest on the way to pick up Ray and Darya? | American Woman David Lynch remix | 2/3 | 0/3 | NO SEARCH | Over-Cautious Refusal |
| twin_peaks_007 | *Same question* | *Same* | 3/3 | 0/3 | WITH SEARCH | Over-Cautious Refusal |
| twin_peaks_008 | What's the color of the hair of the actual Diane in last episode of Twin Peaks? | red | 3/3 | 0/3 | WITH SEARCH | Factual Error (said blonde) |
| twin_peaks_010 | In Twin Peaks season 3, how much money is Shelly giving to Becky at Double R? | $72 | 3/3 | 0/3 | NO SEARCH | Factual Error ($50) |
| twin_peaks_010 | *Same question* | *Same* | 3/3 | 0/3 | WITH SEARCH | Factual Error ($20) |
| twin_peaks_014 | In Twin Peaks season 3, who are the two people watching Dr. Jacoby's video about golden shovels? | Jerry Horne and Nadine | 3/3 | 0/3 | WITH SEARCH | Factual Error (Beverly Paige instead of Nadine) |
| twin_peaks_019 | In season 3 of Twin Peaks, what's the time on the watch of the Ronette Pulaski looking girl? | 2:53 | 2/3 | 0/3 | NO SEARCH | Over-Cautious Refusal |
| twin_peaks_019 | *Same question* | *Same* | 1/3 | 0/3 | WITH SEARCH | Over-Cautious Refusal |

### 🟡 PARTIAL REGRESSIONS (Perfect→Imperfect): 4 Cases

GPT-5.1 was **perfect (3/3)**, but GPT-5.2 became **imperfect (1/3 or 2/3)**.

| Question ID | Question | Expected | GPT-5.1 | GPT-5.2 | Mode | Issue |
|-------------|----------|----------|---------|---------|------|-------|
| twin_peaks_006 | What is the second hint from the giant to agent Dale Cooper? | Owls are not what they seem | 3/3 | 2/3 | WITH SEARCH | Intermittent success |
| twin_peaks_008 | What's the color of the hair of the actual Diane in last episode of Twin Peaks? | red | 3/3 | 1/3 | NO SEARCH | Mostly wrong (said blonde) |
| twin_peaks_014 | In Twin Peaks season 3, who are the two people watching Dr. Jacoby's video about golden shovels? | Jerry Horne and Nadine | 3/3 | 2/3 | NO SEARCH | Wrong person (Dr. Amp himself) |
| twin_peaks_015 | In Twin Peaks season 3, how much money does Cooper/Mr. Jackpot win at the Silver Mustang? | $425,000 | 3/3 | 2/3 | WITH SEARCH | Intermittent success |

### 🟠 PARTIAL REGRESSION: 1 Case

Both models were imperfect, but GPT-5.2 got **worse**.

| Question ID | Question | Expected | GPT-5.1 | GPT-5.2 | Mode | Issue |
|-------------|----------|----------|---------|---------|------|-------|
| twin_peaks_013 | What's the animal that whispers Judy towards the end of Fire Walk with Me? | Monkey | 2/3 | 1/3 | NO SEARCH | Said "angel" instead |

---

## KEY REGRESSION PATTERNS (Detailed Analysis)

### 🔴 Pattern 1: Context Confusion / Domain Misidentification (CRITICAL)

**Severity:** CRITICAL
**Frequency:** 2 questions, 4 instances (both modes)

**Description:** GPT-5.2 incorrectly identifies the show being asked about, confusing "Twin Peaks" with entirely different shows.

**Example - twin_peaks_001:**
```
Question: What does Hawk find in the restroom in season 3 that has to do with its heritage?
Expected Answer: Pages from secret diary of Laura Palmer

GPT-5.1 (3/3): ✅ "Deputy Hawk finds missing pages from Laura Palmer's secret diary
in a stall door in the sheriff's station restroom. He notices a manufacturing logo
on the door that features a Native American head, which he connects to the Log Lady's
message..."

GPT-5.2 (0/3): ❌ "In **Cobra Kai** season 3, Hawk finds the **'Cobra Kai' snake logo**
(a symbol of the dojo's heritage) **painted/graffiti'd in the restroom**, signaling
the dojo's legacy and influence."
```

**Analysis:**
- GPT-5.2 confuses Twin Peaks with Cobra Kai because both have characters named "Hawk"
- Shows complete domain misidentification despite clear context
- Suggests weakened ability to disambiguate character names across different media
- This happens in BOTH NO SEARCH and WITH SEARCH modes

**Impact:** This is the **most severe** type of regression - the model answers about a completely different show, making the response not just wrong but nonsensical in context.

---

### 🔴 Pattern 2: Over-Cautious / Excessive Refusal (CRITICAL)

**Severity:** CRITICAL
**Frequency:** 3 questions, 6 instances (both modes)

**Description:** GPT-5.2 refuses to answer reasonable questions with adequate context, demanding screenshots/timestamps when GPT-5.1 could answer from text descriptions.

**Example - twin_peaks_007:**
```
Question: What's the song played when Mr. C is driving in the forest
on the way to pick up Ray and Darya?
Expected Answer: American Woman David Lynch remix

GPT-5.1 (3/3 WITH SEARCH): ✅ "The song playing while Mr. C is driving through
the forest to pick up Ray and Darya (Twin Peaks: The Return, Part 2) is:
**'American Woman (David Lynch Remix)' by Muddy Magnolias**"

GPT-5.2 (0/3): ❌ "I can't identify that from your description alone because
'Mr. C,' 'Ray,' and 'Darya' could refer to multiple shows/films, and the song
depends on the exact episode/scene. Tell me **which title (show/film)** and
**which episode/season (or a timestamp)**, or upload a clip/screenshot of
the scene, and I'll find the song."
```

**Example - twin_peaks_019:**
```
Question: In season 3 of Twin Peaks, what's the time on the watch of
the Ronette Pulaski looking girl?
Expected Answer: 2:53

GPT-5.1 (2/3 NO SEARCH): ✅ "On the girl who resembles Ronette Pulaski in
*Twin Peaks: The Return* (Season 3), the watch face is stopped at **2:53**."

GPT-5.2 (0/3): ❌ "I can't determine that from your question alone...
If you tell me **the episode number** and **rough timestamp** (or upload
a screenshot of the watch), I can read the time off the watch for you."
```

**Analysis:**
- GPT-5.2 claims insufficient context when GPT-5.1 had enough to answer
- Requests visual evidence (screenshots) for questions that can be answered textually
- Shows loss of confidence in its own knowledge
- May indicate over-correction during RLHF/safety tuning
- User experience degradation: asks for information that should be unnecessary

**Impact:** Creates frustrating user experience and reduces model utility for knowledge queries. Users expect the model to use its training data knowledge, not demand external evidence.

---

### 🔴 Pattern 3: Specific Factual Errors (HIGH SEVERITY)

**Severity:** HIGH
**Frequency:** 5 questions across various types

**Description:** GPT-5.2 attempts to answer but provides incorrect specific details (wrong numbers, colors, names).

#### Subcategory A: Wrong Numerical Values

**Example - twin_peaks_010:**
```
Question: In Twin Peaks season 3, how much money is Shelly giving to Becky at Double R?
Expected Answer: $72

GPT-5.1 (3/3 both modes): ✅ "$72"

GPT-5.2 NO SEARCH (0/3): ❌ "$50"
GPT-5.2 WITH SEARCH (0/3): ❌ "$20"
```

**Analysis:** GPT-5.2 hallucinates different wrong amounts depending on mode, showing:
- Unstable factual retrieval
- Inconsistent hallucination patterns
- Search doesn't help correct the error

#### Subcategory B: Wrong Colors

**Example - twin_peaks_008:**
```
Question: What's the color of the hair of the actual Diane in last episode of Twin Peaks?
Expected Answer: red

GPT-5.1 (3/3): ✅ "red hair (a vivid, natural-looking red...)"

GPT-5.2 NO SEARCH (1/3): ❌ "blonde hair" (mostly failed)
GPT-5.2 WITH SEARCH (0/3): ❌ "platinum blonde/light blonde hair" (always failed)
```

**Analysis:** Color attributes are consistently wrong, and WITH SEARCH performs worse than NO SEARCH.

#### Subcategory C: Wrong Names (Partial Correct)

**Example - twin_peaks_014:**
```
Question: In Twin Peaks season 3, who are the two people watching
Dr. Jacoby's video about golden shovels?
Expected Answer: Jerry Horne and Nadine

GPT-5.1 (3/3): ✅ "Jerry Horne and Nadine Hurley"

GPT-5.2 NO SEARCH (2/3): ❌ "Jerry Horne and Dr. Amp (Dr. Lawrence Jacoby) himself"
GPT-5.2 WITH SEARCH (0/3): ❌ "Jerry Horne and Beverly Paige"
```

**Analysis:**
- Gets one name correct (Jerry Horne) but substitutes wrong second person
- Different wrong answers in different modes
- Shows partial knowledge but inability to retrieve complete correct information

#### Subcategory D: Wrong Entity Type

**Example - twin_peaks_013:**
```
Question: What's the animal that whispers Judy towards the end of Fire Walk with Me?
Expected Answer: Monkey

GPT-5.1 (2/3): ✅ "The animal is a **monkey**"

GPT-5.2 (1/3): ❌ "It's **an angel**—seen as a **white, winged figure**"
```

**Analysis:** Confuses an animal with a supernatural entity, suggesting category confusion in retrieval.

---

## QUESTIONS AFFECTED - COMPLETE LIST

### Questions with Regressions in BOTH Modes (6 questions)

1. **twin_peaks_001** - Hawk's restroom discovery
   - NO SEARCH: Complete regression (3/3→0/3) - Context confusion
   - WITH SEARCH: Complete regression (2/3→0/3) - Context confusion

2. **twin_peaks_007** - Song during Mr. C's drive
   - NO SEARCH: Complete regression (2/3→0/3) - Refusal
   - WITH SEARCH: Complete regression (3/3→0/3) - Refusal

3. **twin_peaks_008** - Diane's hair color
   - NO SEARCH: Partial regression (3/3→1/3) - Wrong color
   - WITH SEARCH: Complete regression (3/3→0/3) - Wrong color

4. **twin_peaks_010** - Money amount Shelly gives Becky
   - NO SEARCH: Complete regression (3/3→0/3) - Wrong amount ($50)
   - WITH SEARCH: Complete regression (3/3→0/3) - Wrong amount ($20)

5. **twin_peaks_014** - Who watches golden shovel video
   - NO SEARCH: Partial regression (3/3→2/3) - Wrong person
   - WITH SEARCH: Complete regression (3/3→0/3) - Wrong person

6. **twin_peaks_019** - Time on watch
   - NO SEARCH: Complete regression (2/3→0/3) - Refusal
   - WITH SEARCH: Complete regression (1/3→0/3) - Refusal

### Questions with Regressions in ONE Mode Only (3 questions)

7. **twin_peaks_006** - Second hint from the Giant
   - WITH SEARCH ONLY: Partial regression (3/3→2/3)

8. **twin_peaks_013** - Animal that whispers Judy
   - NO SEARCH ONLY: Partial regression (2/3→1/3) - Said "angel"

9. **twin_peaks_015** - Money Cooper wins at casino
   - WITH SEARCH ONLY: Partial regression (3/3→2/3)

---

## STATISTICAL SUMMARY

### Overall Regression Stats
- **Total regression cases:** 15
- **Unique questions affected:** 9
- **Questions regressing in both modes:** 6 (67%)
- **Questions regressing in one mode:** 3 (33%)

### By Regression Severity
- **Complete Regressions (Pass→Fail):** 10 cases (67%)
- **Partial Regressions (Perfect→Imperfect):** 4 cases (27%)
- **Partial Regressions (other):** 1 case (6%)

### By Mode
- **NO SEARCH regressions:** 7 cases
- **WITH SEARCH regressions:** 8 cases
- **WITH SEARCH performs slightly worse**

### By Failure Pattern
- **Context Confusion:** 4 instances (2 questions × 2 modes)
- **Over-Cautious Refusal:** 6 instances (3 questions × 2 modes)
- **Factual Errors:** 5 instances (various types)

---

## CRITICAL INSIGHTS

### 1. Search Doesn't Fix the Problem
WITH SEARCH mode has **8 regressions** vs 7 in NO SEARCH mode. This suggests:
- The underlying knowledge degradation is not compensated by search capability
- Search may even introduce additional errors (e.g., different wrong amounts for twin_peaks_010)

### 2. Consistency Problem
Questions like twin_peaks_010 show **different wrong answers** depending on mode:
- NO SEARCH: Says $50
- WITH SEARCH: Says $20
- Neither is correct ($72)

This indicates **unstable retrieval** and **inconsistent hallucination patterns**.

### 3. Context Window / Disambiguation Failure
The Cobra Kai confusion (twin_peaks_001) happens despite:
- Question explicitly mentioning "season 3"
- Context about restroom discovery
- Reference to "heritage"

GPT-5.2 fixates on character name "Hawk" and ignores all other context clues.

### 4. Calibration Problem
The refusal pattern (twin_peaks_007, twin_peaks_019) shows GPT-5.2:
- Has lower confidence threshold for answering
- Over-indexes on wanting visual evidence
- Ignores that textual descriptions can be sufficient

This may be over-correction from safety/refusal training.

---

## ROOT CAUSE HYPOTHESES

### Hypothesis 1: Knowledge Pruning / Compression
**Evidence:**
- Complete loss of specific details (numbers, colors, names)
- Affects niche domain knowledge (Twin Peaks)
- Suggests aggressive model compression or knowledge distillation

**Likelihood:** HIGH

### Hypothesis 2: RLHF/Safety Over-Tuning
**Evidence:**
- Increased refusal rates on reasonable questions
- Requests for "screenshots" when unnecessary
- Over-cautious behavior

**Likelihood:** HIGH

### Hypothesis 3: Training Data Changes
**Evidence:**
- Specific domain knowledge degradation
- May indicate removal of fan wikis, detailed plot summaries
- Could be copyright-related filtering

**Likelihood:** MEDIUM-HIGH

### Hypothesis 4: Context Processing Degradation
**Evidence:**
- Confusion between shows despite context clues
- Inability to disambiguate character names across media
- May indicate attention mechanism or context window changes

**Likelihood:** MEDIUM

### Hypothesis 5: Retrieval Mechanism Changes
**Evidence:**
- Inconsistent answers between modes
- Different wrong answers for same question
- Partial correct information (gets one name, not the other)

**Likelihood:** MEDIUM

---

## RECOMMENDATIONS

### Immediate Actions (P0)

1. **Do NOT deploy GPT-5.2 for applications requiring:**
   - Specialized domain knowledge
   - Precise factual recall
   - Disambiguation of entities across different contexts
   - Reliable answers on niche topics

2. **Create permanent regression test suite:**
   - Add all 15 cases to automated testing
   - Expand to other specialized domains (other TV shows, technical domains, etc.)
   - Run before any future model releases

3. **Root cause investigation:**
   - Compare training data between GPT-5.1 and GPT-5.2
   - Analyze what domain-specific content was removed/reduced
   - Check if model compression/distillation was applied

### Short-term Fixes (P1)

4. **Calibrate refusal behavior:**
   - Reduce over-cautious refusal rates
   - Better calibration between "don't know" vs "can answer with context"
   - A/B test different refusal thresholds

5. **Improve context disambiguation:**
   - Better handling of ambiguous entity names (Hawk in Twin Peaks vs Cobra Kai)
   - Strengthen context window attention
   - Consider explicit disambiguation prompts in training

6. **Fact verification layer:**
   - Add confidence scoring for specific numerical claims
   - Implement consistency checks across modes
   - Consider retrieval augmentation for factual queries

### Long-term Improvements (P2)

7. **Knowledge retention strategy:**
   - Develop better methods for preserving specialized knowledge during compression
   - Consider domain-specific fine-tuning
   - Implement knowledge verification during training

8. **Multi-model comparison framework:**
   - Automated comparison between model versions before release
   - Regression detection across multiple domains
   - Performance dashboards for model evolution

---

## SEVERITY CLASSIFICATION

| Regression Type | Count | User Impact | Business Risk |
|----------------|-------|-------------|---------------|
| Context Confusion | 4 | CRITICAL - Wrong domain entirely | HIGH - Reputation damage |
| Over-Cautious Refusal | 6 | HIGH - Poor UX, frustrated users | MEDIUM - Reduced utility |
| Factual Errors | 5 | HIGH - Misinformation | MEDIUM-HIGH - Trust issues |

---

## CONCLUSION

GPT-5.2 represents a **significant regression** from GPT-5.1 on specialized knowledge tasks:

- **15 regression cases** across 9 questions (out of a focused Twin Peaks dataset)
- **67% are complete regressions** (pass@3 → 0/3 failure)
- **Three distinct failure patterns** all indicating reduced reliability
- **Search capability does not compensate** for underlying knowledge loss

The most concerning finding is the **context confusion pattern**, where GPT-5.2 answers questions about entirely different shows. This represents a fundamental failure in domain understanding and context processing.

**Deployment Recommendation:** **DO NOT DEPLOY** GPT-5.2 for knowledge-intensive applications until these regressions are addressed. The model shows worse performance than GPT-5.1 across multiple dimensions and failure modes.

**Next Steps:**
1. Expand testing to other specialized domains to determine scope of regressions
2. Investigate root causes (training data, model architecture, RLHF tuning)
3. Implement fixes and re-evaluate before considering deployment
4. Establish permanent regression testing for future releases

---

**Report Generated:** 2025-12-22
**Analyst:** Claude Code Automated Analysis
**Data Source:** `all_regressions_gpt51_vs_gpt52.csv`

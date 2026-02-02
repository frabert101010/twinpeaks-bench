import csv
from collections import defaultdict

# Read GPT-5.1 results
gpt51_results = defaultdict(lambda: {'NO SEARCH': {'scores': [], 'responses': []}, 'WITH SEARCH': {'scores': [], 'responses': []}})
questions_data = {}

with open('gpt51_detailed_20251222_070815.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        question_id = row['Question ID']
        mode = row['Mode']
        score = int(row['Score (0/1)'])
        response = row['Model Response']
        gpt51_results[question_id][mode]['scores'].append(score)
        gpt51_results[question_id][mode]['responses'].append(response)

        if question_id not in questions_data:
            questions_data[question_id] = {
                'question': row['Question'],
                'expected_answer': row['Expected Answer'],
                'category': row['Category']
            }

# Read GPT-5.2 results from full benchmark file
gpt52_results = defaultdict(lambda: {'NO SEARCH': {'scores': [], 'responses': []}, 'WITH SEARCH': {'scores': [], 'responses': []}})

with open('results_detailed_20251216_103242.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Model'] == 'GPT-5.2':
            question_id = row['Question ID']
            mode = row['Mode']
            score = int(row['Score (0/1)'])
            response = row['Model Response']
            gpt52_results[question_id][mode]['scores'].append(score)
            gpt52_results[question_id][mode]['responses'].append(response)

# Find ALL cases where GPT-5.2 regressed (lower score than GPT-5.1)
all_regressions = []

for question_id in gpt51_results.keys():
    for mode in ['NO SEARCH', 'WITH SEARCH']:
        gpt51_data = gpt51_results[question_id][mode]
        gpt52_data = gpt52_results[question_id][mode]

        gpt51_scores = gpt51_data['scores']
        gpt52_scores = gpt52_data['scores']
        gpt51_responses = gpt51_data['responses']
        gpt52_responses = gpt52_data['responses']

        # Skip if GPT-5.2 has no data for this question
        if not gpt52_scores:
            continue

        # Calculate success counts
        gpt51_success_count = sum(gpt51_scores)
        gpt52_success_count = sum(gpt52_scores)
        gpt51_total = len(gpt51_scores)
        gpt52_total = len(gpt52_scores)

        # Check if there's a regression (GPT-5.2 has lower success rate)
        gpt51_rate = gpt51_success_count / gpt51_total if gpt51_total > 0 else 0
        gpt52_rate = gpt52_success_count / gpt52_total if gpt52_total > 0 else 0

        if gpt52_rate < gpt51_rate:
            # Determine regression type
            if gpt51_success_count > 0 and gpt52_success_count == 0:
                regression_type = "Complete Regression (Pass→Fail)"
            elif gpt51_success_count == gpt51_total and gpt52_success_count < gpt52_total:
                regression_type = "Partial Regression (Perfect→Imperfect)"
            else:
                regression_type = "Partial Regression"

            # Get representative answers
            gpt51_first_pass = None
            for i, score in enumerate(gpt51_scores):
                if score == 1:
                    gpt51_first_pass = gpt51_responses[i]
                    break

            gpt52_first_response = gpt52_responses[0] if gpt52_responses else ""

            all_regressions.append({
                'Question ID': question_id,
                'Question': questions_data[question_id]['question'],
                'Expected Answer': questions_data[question_id]['expected_answer'],
                'Category': questions_data[question_id]['category'],
                'Mode': mode,
                'Regression Type': regression_type,
                'GPT-5.1 Score': f"{gpt51_success_count}/{gpt51_total}",
                'GPT-5.2 Score': f"{gpt52_success_count}/{gpt52_total}",
                'GPT-5.1 Pass@3': 'YES' if gpt51_success_count > 0 else 'NO',
                'GPT-5.2 Pass@3': 'YES' if gpt52_success_count > 0 else 'NO',
                'GPT-5.1 Answer (First Pass)': gpt51_first_pass,
                'GPT-5.2 Answer (Trial 1)': gpt52_first_response
            })

# Sort by regression type severity, then by question ID
severity_order = {
    "Complete Regression (Pass→Fail)": 0,
    "Partial Regression (Perfect→Imperfect)": 1,
    "Partial Regression": 2
}
all_regressions.sort(key=lambda x: (severity_order[x['Regression Type']], x['Question ID'], x['Mode']))

# Write to CSV
output_file = 'all_regressions_gpt51_vs_gpt52.csv'
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['Question ID', 'Question', 'Expected Answer', 'Category', 'Mode',
                  'Regression Type', 'GPT-5.1 Score', 'GPT-5.2 Score',
                  'GPT-5.1 Pass@3', 'GPT-5.2 Pass@3',
                  'GPT-5.1 Answer (First Pass)', 'GPT-5.2 Answer (Trial 1)']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_regressions)

print(f"✅ Comprehensive comparison complete!")
print(f"📊 Found {len(all_regressions)} total regression cases")
print(f"📄 Results saved to: {output_file}")

# Summary stats
print(f"\n{'='*60}")
print("REGRESSION BREAKDOWN BY TYPE:")
print(f"{'='*60}")

regression_counts = defaultdict(int)
for r in all_regressions:
    regression_counts[r['Regression Type']] += 1

for reg_type in ["Complete Regression (Pass→Fail)",
                 "Partial Regression (Perfect→Imperfect)",
                 "Partial Regression"]:
    count = regression_counts[reg_type]
    if count > 0:
        print(f"{reg_type}: {count} cases")

print(f"\n{'='*60}")
print("BREAKDOWN BY MODE:")
print(f"{'='*60}")

no_search_count = sum(1 for r in all_regressions if r['Mode'] == 'NO SEARCH')
with_search_count = sum(1 for r in all_regressions if r['Mode'] == 'WITH SEARCH')
print(f"NO SEARCH: {no_search_count} regressions")
print(f"WITH SEARCH: {with_search_count} regressions")

print(f"\n{'='*60}")
print("UNIQUE QUESTIONS AFFECTED:")
print(f"{'='*60}")

unique_questions = set(r['Question ID'] for r in all_regressions)
print(f"Total unique questions with regressions: {len(unique_questions)}")

# Count questions with regressions in both modes
both_modes = set()
for qid in unique_questions:
    modes = [r['Mode'] for r in all_regressions if r['Question ID'] == qid]
    if 'NO SEARCH' in modes and 'WITH SEARCH' in modes:
        both_modes.add(qid)

print(f"Questions with regressions in BOTH modes: {len(both_modes)}")
print(f"Questions with regressions in ONE mode only: {len(unique_questions) - len(both_modes)}")

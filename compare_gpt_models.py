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

# Find questions where GPT-5.1 succeeded (at least one trial passed) but GPT-5.2 failed (all trials failed)
comparisons = []

for question_id in gpt51_results.keys():
    for mode in ['NO SEARCH', 'WITH SEARCH']:
        gpt51_data = gpt51_results[question_id][mode]
        gpt52_data = gpt52_results[question_id][mode]

        gpt51_scores = gpt51_data['scores']
        gpt52_scores = gpt52_data['scores']
        gpt51_responses = gpt51_data['responses']
        gpt52_responses = gpt52_data['responses']

        # Check if GPT-5.1 succeeded (at least one 1) and GPT-5.2 failed (all 0s)
        gpt51_passed = any(score == 1 for score in gpt51_scores) if gpt51_scores else False
        gpt52_failed = all(score == 0 for score in gpt52_scores) if gpt52_scores else False

        if gpt51_passed and gpt52_failed and gpt52_scores:  # Make sure GPT-5.2 has data
            # Get first passing GPT-5.1 response and first GPT-5.2 response
            gpt51_first_pass = None
            for i, score in enumerate(gpt51_scores):
                if score == 1:
                    gpt51_first_pass = gpt51_responses[i]
                    break

            gpt52_first_response = gpt52_responses[0] if gpt52_responses else ""

            comparisons.append({
                'Question ID': question_id,
                'Question': questions_data[question_id]['question'],
                'Expected Answer': questions_data[question_id]['expected_answer'],
                'Category': questions_data[question_id]['category'],
                'Mode': mode,
                'GPT-5.1 Pass@3': 'YES',
                'GPT-5.2 Pass@3': 'NO',
                'GPT-5.1 Trials': f"{sum(gpt51_scores)}/3",
                'GPT-5.2 Trials': f"{sum(gpt52_scores)}/3",
                'GPT-5.1 Answer (First Pass)': gpt51_first_pass,
                'GPT-5.2 Answer (Trial 1)': gpt52_first_response
            })

# Write to CSV
output_file = 'gpt51_wins_over_gpt52_detailed.csv'
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['Question ID', 'Question', 'Expected Answer', 'Category', 'Mode',
                  'GPT-5.1 Pass@3', 'GPT-5.2 Pass@3', 'GPT-5.1 Trials', 'GPT-5.2 Trials',
                  'GPT-5.1 Answer (First Pass)', 'GPT-5.2 Answer (Trial 1)']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(comparisons)

print(f"✅ Comparison complete!")
print(f"📊 Found {len(comparisons)} questions where GPT-5.1 succeeded but GPT-5.2 failed")
print(f"📄 Results saved to: {output_file}")

# Summary stats
no_search_count = sum(1 for c in comparisons if c['Mode'] == 'NO SEARCH')
with_search_count = sum(1 for c in comparisons if c['Mode'] == 'WITH SEARCH')
print(f"\nBreakdown:")
print(f"  NO SEARCH: {no_search_count} questions")
print(f"  WITH SEARCH: {with_search_count} questions")

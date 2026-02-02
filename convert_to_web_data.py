"""
Convert CSV data to JSON format for the website
"""
import csv
import json

# Convert summary CSV to JSON
summary_data = []
with open('twinpeaks_v1_summary_results.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        summary_data.append({
            'model': row['model'],
            'mode': row['mode'],
            'pass1': float(row['pass@1']),
            'pass3': float(row['pass@3']),
            'accuracy': float(row['accuracy'])
        })

# Organize by model
models = {}
for row in summary_data:
    model = row['model']
    if model not in models:
        models[model] = {}
    models[model][row['mode']] = {
        'pass1': row['pass1'],
        'pass3': row['pass3'],
        'accuracy': row['accuracy']
    }

# Convert to list format sorted by no-search accuracy
model_list = []
for model, modes in models.items():
    model_list.append({
        'model': model,
        'no_search': modes.get('NO SEARCH', {}),
        'with_search': modes.get('WITH SEARCH', {})
    })

# Sort by no-search accuracy
model_list.sort(key=lambda x: x.get('no_search', {}).get('accuracy', 0), reverse=True)

# Save summary
with open('docs/data/summary.json', 'w') as f:
    json.dump(model_list, f, indent=2)

print(f"✓ Converted summary data: {len(model_list)} models")

# Convert detailed CSV to JSON
detailed_data = []
with open('twinpeaks_v1_detailed_results.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        detailed_data.append({
            'question_id': row['question_id'],
            'question': row['question'],
            'expected_answer': row['expected_answer'],
            'category': row['category'],
            'model': row['model'],
            'mode': row['mode'],
            'trial': int(row['trial']),
            'response': row['response'],
            'score': int(row['score']),
            'reasoning': row['reasoning'],
            'latency': float(row['latency']) if row['latency'] else 0
        })

# Organize by question
questions = {}
for row in detailed_data:
    q_id = row['question_id']
    if q_id not in questions:
        questions[q_id] = {
            'id': q_id,
            'question': row['question'],
            'expected_answer': row['expected_answer'],
            'responses': []
        }
    questions[q_id]['responses'].append({
        'model': row['model'],
        'mode': row['mode'],
        'trial': row['trial'],
        'response': row['response'],
        'score': row['score'],
        'reasoning': row['reasoning'],
        'latency': row['latency']
    })

# Calculate difficulty for each question (lower accuracy = harder)
for q_id, q_data in questions.items():
    total_score = sum(r['score'] for r in q_data['responses'])
    total_trials = len(q_data['responses'])
    q_data['accuracy'] = (total_score / total_trials * 100) if total_trials > 0 else 0

    # Difficulty rating (1-5 stars, inverse of accuracy)
    if q_data['accuracy'] < 20:
        q_data['difficulty'] = 5  # Very hard
    elif q_data['accuracy'] < 40:
        q_data['difficulty'] = 4  # Hard
    elif q_data['accuracy'] < 60:
        q_data['difficulty'] = 3  # Medium
    elif q_data['accuracy'] < 80:
        q_data['difficulty'] = 2  # Easy
    else:
        q_data['difficulty'] = 1  # Very easy

# Convert to list and sort by question ID
question_list = list(questions.values())
question_list.sort(key=lambda x: x['id'])

# Save detailed data
with open('docs/data/detailed.json', 'w', encoding='utf-8') as f:
    json.dump(question_list, f, indent=2, ensure_ascii=False)

print(f"✓ Converted detailed data: {len(question_list)} questions")
print(f"✓ Total responses: {len(detailed_data)}")
print("\n✅ Data conversion complete!")

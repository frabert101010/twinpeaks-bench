import sqlite3
import json
import csv
import statistics
from collections import defaultdict

# Configuration
NO_SEARCH_RUN = "TwinPeaks Bench V1 (NO SEARCH) - RUN_20260104_130836"
WITH_SEARCH_RUN_1 = "TwinPeaks Bench V1 (WITH SEARCH) - RUN_20260104_130836"
WITH_SEARCH_RUN_2 = "TwinPeaks Bench V1 (WITH SEARCH) - RUN_20260104_192334"
NUM_TRIALS = 3

def get_question_id_mapping():
    """Load eval_set_v1.json to get question IDs"""
    with open('eval_set_v1.json', 'r') as f:
        data = json.load(f)

    mapping = {}
    for test_case in data['test_cases']:
        mapping[test_case['prompt'].strip()] = test_case['id']
    return mapping

def extract_results_from_db():
    """Extract all results from database"""
    conn = sqlite3.connect('eval_history.db')
    cursor = conn.cursor()

    # Get question ID mapping
    question_mapping = get_question_id_mapping()

    all_results = []

    # Query NO SEARCH results (all 27 questions)
    cursor.execute('''
        SELECT e.question, e.expected_answer, e.category,
               mr.model_name, mr.response, mr.score, mr.reasoning, mr.latency_seconds
        FROM evaluations e
        JOIN model_responses mr ON e.id = mr.eval_id
        WHERE e.eval_name = ?
        ORDER BY e.question, mr.model_name
    ''', (NO_SEARCH_RUN,))

    for row in cursor.fetchall():
        question, expected, category, model, response, score, reasoning, latency = row
        question_id = question_mapping.get(question.strip(), "unknown")
        all_results.append({
            'question_id': question_id,
            'question': question,
            'expected_answer': expected,
            'category': category,
            'model': model,
            'mode': 'NO SEARCH',
            'response': response,
            'score': score if score is not None else 0,
            'reasoning': reasoning,
            'latency': latency
        })

    # Query WITH SEARCH results questions 1-21 from first run
    cursor.execute('''
        SELECT e.question, e.expected_answer, e.category,
               mr.model_name, mr.response, mr.score, mr.reasoning, mr.latency_seconds
        FROM evaluations e
        JOIN model_responses mr ON e.id = mr.eval_id
        WHERE e.eval_name = ?
        ORDER BY e.question, mr.model_name
    ''', (WITH_SEARCH_RUN_1,))

    for row in cursor.fetchall():
        question, expected, category, model, response, score, reasoning, latency = row
        question_id = question_mapping.get(question.strip(), "unknown")
        # Only include if it's NOT question 22 (since that run hung on 22)
        if not question_id.endswith('_022'):
            all_results.append({
                'question_id': question_id,
                'question': question,
                'expected_answer': expected,
                'category': category,
                'model': model,
                'mode': 'WITH SEARCH',
                'response': response,
                'score': score if score is not None else 0,
                'reasoning': reasoning,
                'latency': latency
            })

    # Query WITH SEARCH results questions 22-27 from continuation run
    cursor.execute('''
        SELECT e.question, e.expected_answer, e.category,
               mr.model_name, mr.response, mr.score, mr.reasoning, mr.latency_seconds
        FROM evaluations e
        JOIN model_responses mr ON e.id = mr.eval_id
        WHERE e.eval_name = ?
        ORDER BY e.question, mr.model_name
    ''', (WITH_SEARCH_RUN_2,))

    for row in cursor.fetchall():
        question, expected, category, model, response, score, reasoning, latency = row
        question_id = question_mapping.get(question.strip(), "unknown")
        all_results.append({
            'question_id': question_id,
            'question': question,
            'expected_answer': expected,
            'category': category,
            'model': model,
            'mode': 'WITH SEARCH',
            'response': response,
            'score': score if score is not None else 0,
            'reasoning': reasoning,
            'latency': latency
        })

    conn.close()
    return all_results

def organize_results_by_trial(all_results):
    """Organize results by question, model, mode, and trial number"""
    # Group by question_id, model, mode
    grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for result in all_results:
        key = (result['question_id'], result['model'], result['mode'])
        grouped[result['question_id']][result['model']][result['mode']].append({
            'response': result['response'],
            'score': result['score'],
            'reasoning': result['reasoning'],
            'latency': result['latency'],
            'question': result['question'],
            'expected_answer': result['expected_answer'],
            'category': result['category']
        })

    # Add trial numbers
    detailed_results = []
    for question_id in sorted(grouped.keys()):
        for model in sorted(grouped[question_id].keys()):
            for mode in ['NO SEARCH', 'WITH SEARCH']:
                if mode in grouped[question_id][model]:
                    trials = grouped[question_id][model][mode]
                    for trial_num, trial_data in enumerate(trials, 1):
                        detailed_results.append({
                            'question_id': question_id,
                            'question': trial_data['question'],
                            'expected_answer': trial_data['expected_answer'],
                            'category': trial_data['category'],
                            'model': model,
                            'mode': mode,
                            'trial': trial_num,
                            'response': trial_data['response'],
                            'score': trial_data['score'],
                            'reasoning': trial_data['reasoning'],
                            'latency': trial_data['latency']
                        })

    return detailed_results

def calculate_stats(detailed_results):
    """Calculate Pass@1, Pass@3, and Accuracy"""
    # Organize by question_id, model, mode
    organized = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for result in detailed_results:
        organized[result['question_id']][result['model']][result['mode']].append(result['score'])

    # Calculate stats per model per mode
    stats = defaultdict(lambda: defaultdict(dict))

    models = sorted(set(r['model'] for r in detailed_results))

    for model in models:
        for mode in ['NO SEARCH', 'WITH SEARCH']:
            pass1_scores = []
            pass3_scores = []
            all_scores = []

            for question_id in sorted(organized.keys()):
                if mode in organized[question_id][model]:
                    scores = organized[question_id][model][mode]
                    if scores:
                        # Pass@1: first trial success
                        pass1_scores.append(scores[0])
                        # Pass@3: success in any of the 3 trials
                        pass3_scores.append(1 if any(scores) else 0)
                        # All trial scores for accuracy
                        all_scores.extend(scores)

            if pass1_scores:
                stats[model][mode] = {
                    'pass@1': statistics.mean(pass1_scores) * 100,
                    'pass@3': statistics.mean(pass3_scores) * 100,
                    'accuracy': statistics.mean(all_scores) * 100
                }

    return stats

def export_detailed_csv(detailed_results, filename='twinpeaks_v1_detailed_results.csv'):
    """Export detailed results to CSV"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'question_id', 'question', 'expected_answer', 'category',
            'model', 'mode', 'trial', 'response', 'score', 'reasoning', 'latency'
        ])
        writer.writeheader()
        writer.writerows(detailed_results)
    print(f"✅ Exported detailed results to {filename}")

def export_summary_csv(stats, filename='twinpeaks_v1_summary_results.csv'):
    """Export summary stats to CSV"""
    rows = []
    for model in sorted(stats.keys()):
        for mode in ['NO SEARCH', 'WITH SEARCH']:
            if mode in stats[model]:
                rows.append({
                    'model': model,
                    'mode': mode,
                    'pass@1': round(stats[model][mode]['pass@1'], 2),
                    'pass@3': round(stats[model][mode]['pass@3'], 2),
                    'accuracy': round(stats[model][mode]['accuracy'], 2)
                })

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['model', 'mode', 'pass@1', 'pass@3', 'accuracy'])
        writer.writeheader()
        writer.writerows(rows)
    print(f"✅ Exported summary results to {filename}")

def display_summary(stats):
    """Display summary table"""
    print("\n" + "="*80)
    print("TWINPEAKS BENCH V1 - FINAL RESULTS")
    print("="*80)
    print(f"\n{'Model':<25} {'Mode':<15} {'Pass@1':<10} {'Pass@3':<10} {'Accuracy':<10}")
    print("-"*80)

    for model in sorted(stats.keys()):
        for mode in ['NO SEARCH', 'WITH SEARCH']:
            if mode in stats[model]:
                print(f"{model:<25} {mode:<15} "
                      f"{stats[model][mode]['pass@1']:>7.2f}%  "
                      f"{stats[model][mode]['pass@3']:>7.2f}%  "
                      f"{stats[model][mode]['accuracy']:>7.2f}%")
    print("="*80)

if __name__ == "__main__":
    print("\n🔍 Extracting results from database...")
    all_results = extract_results_from_db()
    print(f"   Found {len(all_results)} total responses")

    print("\n📊 Organizing results by trial...")
    detailed_results = organize_results_by_trial(all_results)
    print(f"   Organized into {len(detailed_results)} trial records")

    print("\n📈 Calculating statistics...")
    stats = calculate_stats(detailed_results)

    print("\n💾 Exporting results...")
    export_detailed_csv(detailed_results)
    export_summary_csv(stats)

    display_summary(stats)

    print("\n✅ Export complete!")

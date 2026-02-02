import sqlite3
import csv
from datetime import datetime

def find_and_export_run():
    conn = sqlite3.connect('eval_history.db')
    cursor = conn.cursor()
    
    # Find runs that match these exact stats
    # Looking for: Sonnet No Search = 87.5% avg (7/8 correct across 5 trials)
    # This is distinctive enough to identify the run
    
    cursor.execute('''
        SELECT DISTINCT e.timestamp, e.eval_name
        FROM evaluations e
        JOIN model_responses mr ON e.id = mr.eval_id
        WHERE mr.model_name = 'Claude Sonnet 4.5'
        AND e.eval_name LIKE '%NO SEARCH%'
        GROUP BY e.timestamp, e.eval_name
        HAVING ABS(AVG(mr.score) * 100 - 87.5) < 1
        ORDER BY e.timestamp DESC
        LIMIT 1
    ''')
    
    result = cursor.fetchone()
    
    if not result:
        print("❌ Could not find that specific run. Trying most recent...")
        cursor.execute('''
            SELECT timestamp FROM evaluations 
            ORDER BY timestamp DESC LIMIT 1
        ''')
        result = cursor.fetchone()
    
    target_timestamp = result[0]
    
    print(f"\n📊 Exporting benchmark run from: {target_timestamp}")
    print("=" * 70)
    
    # Get all responses from this timestamp (both modes)
    cursor.execute('''
        SELECT 
            e.question,
            e.expected_answer,
            e.category,
            e.eval_name,
            mr.model_name,
            mr.response,
            mr.score,
            mr.reasoning,
            mr.error,
            mr.latency_seconds,
            e.id
        FROM evaluations e
        JOIN model_responses mr ON e.id = mr.eval_id
        WHERE e.timestamp = ?
        ORDER BY e.id, mr.model_name, mr.id
    ''', (target_timestamp,))
    
    responses = cursor.fetchall()
    
    if not responses:
        print("No responses found")
        return
    
    # Count questions
    cursor.execute('''
        SELECT COUNT(DISTINCT id) FROM evaluations WHERE timestamp = ?
    ''', (target_timestamp,))
    num_questions = cursor.fetchone()[0]
    
    # Export to CSV
    export_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"benchmark_results_{export_timestamp}.csv"
    
    # Track for trial numbering
    trial_counter = {}
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Question ID',
            'Question',
            'Expected Answer',
            'Category',
            'Model',
            'Mode',
            'Trial',
            'Model Response',
            'Score (0/1)',
            'Pass/Fail',
            'Judge Reasoning',
            'Error',
            'Latency (s)'
        ])
        
        for row in responses:
            question, expected, category, eval_name, model, response, score, reasoning, error, latency, eval_id = row
            
            # Determine mode
            if "NO SEARCH" in eval_name:
                mode = "No Search"
            elif "WITH SEARCH" in eval_name:
                mode = "With Search"
            else:
                mode = "Unknown"
            
            # Track trial number
            key = (eval_id, model, mode)
            if key not in trial_counter:
                trial_counter[key] = 0
            trial_counter[key] += 1
            trial_num = trial_counter[key]
            
            pass_fail = "PASS" if score == 1 else "FAIL" if score == 0 else "N/A"
            response_text = response if response else f"ERROR: {error}" if error else "No response"
            latency_str = f"{latency:.2f}" if latency else "N/A"
            
            # Generate question ID
            question_id = f"q{eval_id}"
            
            writer.writerow([
                question_id,
                question,
                expected,
                category,
                model,
                mode,
                trial_num,
                response_text,
                score if score is not None else "N/A",
                pass_fail,
                reasoning if reasoning else "",
                error if error else "",
                latency_str
            ])
    
    print(f"✅ Exported {len(responses)} responses to: {filename}")
    print(f"   Questions: {num_questions // 2}")  # Divide by 2 because we have 2 modes
    print(f"   Trials per question: ~5")
    
    # Show summary matching the terminal output
    print("\n📈 VERIFICATION - SHOULD MATCH YOUR TERMINAL OUTPUT:")
    print("=" * 70)
    
    models = ["Claude Sonnet 4.5", "Claude Opus 4.5", "GPT-5.2", "Gemini 3"]
    
    for model in models:
        for mode_suffix in [" (NO SEARCH)", " (WITH SEARCH)"]:
            mode_display = "No Search" if "NO SEARCH" in mode_suffix else "With Search"
            
            # Get stats for this model/mode combo
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT e.id) as num_questions,
                    SUM(CASE WHEN mr.score = 1 AND mr.id IN (
                        SELECT MIN(mr2.id) FROM model_responses mr2 
                        JOIN evaluations e2 ON mr2.eval_id = e2.id
                        WHERE e2.timestamp = ? AND e2.eval_name LIKE ? AND mr2.model_name = ?
                        GROUP BY e2.id
                    ) THEN 1 ELSE 0 END) as pass_at_1,
                    AVG(mr.score) * 100 as avg_score
                FROM evaluations e
                JOIN model_responses mr ON e.id = mr.eval_id
                WHERE e.timestamp = ?
                AND e.eval_name LIKE ?
                AND mr.model_name = ?
            ''', (target_timestamp, f'%{mode_suffix}', model, target_timestamp, f'%{mode_suffix}', model))
            
            result = cursor.fetchone()
            if result and result[0]:
                num_q, pass1, avg = result
                pass1_pct = (pass1 / num_q * 100) if num_q else 0
                avg_display = avg if avg is not None else 0
                
                print(f"{model:20s} {mode_display:15s}  Pass@1: {pass1_pct:>5.1f}%  Avg: {avg_display:>5.1f}%")
    
    conn.close()
    print("\n" + "=" * 70)

if __name__ == "__main__":
    find_and_export_run()

import sqlite3
import csv
from datetime import datetime

def export_latest_eval():
    conn = sqlite3.connect('eval_history.db')
    cursor = conn.cursor()
    
    # Get the most recent evaluation run
    cursor.execute('''
        SELECT DISTINCT eval_name, timestamp
        FROM evaluations
        ORDER BY timestamp DESC
        LIMIT 1
    ''')
    
    latest = cursor.fetchone()
    if not latest:
        print("No evaluations found in database")
        return
    
    eval_name, timestamp = latest
    print(f"\n📊 Exporting latest evaluation:")
    print(f"   Name: {eval_name}")
    print(f"   Date: {timestamp}")
    print("-" * 70)
    
    # Get all responses from the latest eval
    cursor.execute('''
        SELECT 
            e.id,
            e.question,
            e.expected_answer,
            e.category,
            mr.model_name,
            mr.response,
            mr.score,
            mr.reasoning,
            mr.error,
            mr.latency_seconds
        FROM evaluations e
        JOIN model_responses mr ON e.id = mr.eval_id
        WHERE e.eval_name = ?
        ORDER BY e.id, mr.model_name, mr.id
    ''', (eval_name,))
    
    responses = cursor.fetchall()
    
    if not responses:
        print("No responses found for this evaluation")
        return
    
    # Export to CSV
    export_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"exported_eval_results_{export_timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Eval ID',
            'Question',
            'Expected Answer',
            'Category',
            'Model',
            'Model Response',
            'Score (0/1)',
            'Pass/Fail',
            'Judge Reasoning',
            'Error',
            'Latency (s)'
        ])
        
        for row in responses:
            eval_id, question, expected, category, model, response, score, reasoning, error, latency = row
            
            pass_fail = "PASS" if score == 1 else "FAIL" if score == 0 else "N/A"
            response_text = response if response else f"ERROR: {error}"
            latency_str = f"{latency:.2f}" if latency else "N/A"
            
            writer.writerow([
                eval_id,
                question,
                expected,
                category,
                model,
                response_text,
                score if score is not None else "N/A",
                pass_fail,
                reasoning if reasoning else "",
                error if error else "",
                latency_str
            ])
    
    conn.close()
    
    print(f"\n✅ Exported {len(responses)} responses to: {filename}")
    
    # Show summary
    print("\n📈 SUMMARY:")
    
    conn = sqlite3.connect('eval_history.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            mr.model_name,
            COUNT(*) as total,
            SUM(CASE WHEN mr.score = 1 THEN 1 ELSE 0 END) as passed,
            AVG(mr.score) * 100 as avg_score
        FROM evaluations e
        JOIN model_responses mr ON e.id = mr.eval_id
        WHERE e.eval_name = ? AND mr.score IS NOT NULL
        GROUP BY mr.model_name
    ''', (eval_name,))
    
    stats = cursor.fetchall()
    
    for model, total, passed, avg_score in stats:
        print(f"   {model:25s}: {passed}/{total} passed ({avg_score:.1f}%)")
    
    conn.close()
    print("-" * 70)

if __name__ == "__main__":
    export_latest_eval()

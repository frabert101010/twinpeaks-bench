import sqlite3
import csv
from datetime import datetime

def export_latest_run():
    conn = sqlite3.connect('eval_history.db')
    cursor = conn.cursor()
    
    # Get the most recent timestamp
    cursor.execute('''
        SELECT MAX(timestamp) 
        FROM evaluations
        WHERE eval_name LIKE '%NO SEARCH%' OR eval_name LIKE '%WITH SEARCH%'
    ''')
    
    latest_timestamp = cursor.fetchone()[0]
    
    print(f"\n📊 Exporting ONLY the latest benchmark run:")
    print(f"   Timestamp: {latest_timestamp}")
    print("-" * 70)
    
    # Get all responses from ONLY this timestamp
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
            mr.latency_seconds
        FROM evaluations e
        JOIN model_responses mr ON e.id = mr.eval_id
        WHERE e.timestamp = ?
        ORDER BY e.eval_name, e.id, mr.model_name, mr.id
    ''', (latest_timestamp,))
    
    responses = cursor.fetchall()
    
    if not responses:
        print("No responses found")
        return
    
    # Export to CSV
    export_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"latest_run_only_{export_timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Question',
            'Expected Answer',
            'Category',
            'Model',
            'Mode',
            'Model Response',
            'Score (0/1)',
            'Pass/Fail',
            'Judge Reasoning',
            'Error',
            'Latency (s)'
        ])
        
        for row in responses:
            question, expected, category, eval_name, model, response, score, reasoning, error, latency = row
            
            if "NO SEARCH" in eval_name:
                mode = "No Search"
            elif "WITH SEARCH" in eval_name:
                mode = "With Search"
            else:
                mode = "Unknown"
            
            pass_fail = "PASS" if score == 1 else "FAIL" if score == 0 else "N/A"
            response_text = response if response else f"ERROR: {error}" if error else "No response"
            latency_str = f"{latency:.2f}" if latency else "N/A"
            
            writer.writerow([
                question,
                expected,
                category,
                model,
                mode,
                response_text,
                score if score is not None else "N/A",
                pass_fail,
                reasoning if reasoning else "",
                error if error else "",
                latency_str
            ])
    
    conn.close()
    
    print(f"\n✅ Exported {len(responses)} responses from latest run to: {filename}")
    
    # Detailed summary
    print("\n📈 DETAILED SUMMARY:")
    
    conn = sqlite3.connect('eval_history.db')
    cursor = conn.cursor()
    
    # Count by mode and model
    cursor.execute('''
        SELECT 
            e.eval_name,
            mr.model_name,
            COUNT(*) as total,
            SUM(CASE WHEN mr.score = 1 THEN 1 ELSE 0 END) as passed,
            SUM(CASE WHEN mr.score = 0 THEN 1 ELSE 0 END) as failed,
            SUM(CASE WHEN mr.error IS NOT NULL THEN 1 ELSE 0 END) as errors,
            AVG(CASE WHEN mr.score IS NOT NULL THEN mr.score END) * 100 as avg_score
        FROM evaluations e
        JOIN model_responses mr ON e.id = mr.eval_id
        WHERE e.timestamp = ?
        GROUP BY e.eval_name, mr.model_name
        ORDER BY e.eval_name, mr.model_name
    ''', (latest_timestamp,))
    
    stats = cursor.fetchall()
    
    current_mode = None
    for eval_name, model, total, passed, failed, errors, avg_score in stats:
        mode = "No Search" if "NO SEARCH" in eval_name else "With Search"
        
        if mode != current_mode:
            print(f"\n  {mode}:")
            print("  " + "-" * 68)
            current_mode = mode
        
        avg_display = f"{avg_score:.1f}%" if avg_score is not None else "N/A"
        print(f"     {model:25s}: {passed} pass, {failed} fail, {errors} errors ({avg_display})")
    
    conn.close()
    print("\n" + "=" * 70)

if __name__ == "__main__":
    export_latest_run()

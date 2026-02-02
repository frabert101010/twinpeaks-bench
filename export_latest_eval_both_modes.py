import sqlite3
import csv
from datetime import datetime

def export_latest_eval():
    conn = sqlite3.connect('eval_history.db')
    cursor = conn.cursor()
    
    # Get the most recent benchmark (look for both modes)
    cursor.execute('''
        SELECT DISTINCT eval_name, timestamp
        FROM evaluations
        WHERE eval_name LIKE '%NO SEARCH%' OR eval_name LIKE '%WITH SEARCH%'
        ORDER BY timestamp DESC
        LIMIT 2
    ''')
    
    evals = cursor.fetchall()
    if not evals:
        print("No evaluations found in database")
        return
    
    # Extract base name (remove mode suffix)
    base_name = evals[0][0].replace(" (NO SEARCH)", "").replace(" (WITH SEARCH)", "")
    
    print(f"\n📊 Exporting latest benchmark:")
    print(f"   Name: {base_name}")
    print(f"   Modes: No Search + With Search")
    print("-" * 70)
    
    # Get all responses from BOTH modes
    cursor.execute('''
        SELECT 
            e.id,
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
        WHERE e.eval_name LIKE ?
        ORDER BY e.eval_name, e.id, mr.model_name, mr.id
    ''', (f"{base_name}%",))
    
    responses = cursor.fetchall()
    
    if not responses:
        print("No responses found")
        return
    
    # Export to CSV
    export_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"exported_eval_results_{export_timestamp}.csv"
    
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
            eval_id, question, expected, category, eval_name, model, response, score, reasoning, error, latency = row
            
            # Extract mode from eval_name
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
    
    print(f"\n✅ Exported {len(responses)} responses to: {filename}")
    
    # Show summary BY MODE
    print("\n📈 SUMMARY BY MODE:")
    
    conn = sqlite3.connect('eval_history.db')
    cursor = conn.cursor()
    
    for mode_suffix in [" (NO SEARCH)", " (WITH SEARCH)"]:
        eval_name_pattern = f"{base_name}{mode_suffix}"
        mode_display = "No Search" if "NO SEARCH" in mode_suffix else "With Search"
        
        print(f"\n  {mode_display}:")
        print("  " + "-" * 68)
        
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
        ''', (eval_name_pattern,))
        
        stats = cursor.fetchall()
        
        if stats:
            for model, total, passed, avg_score in stats:
                print(f"     {model:25s}: {passed}/{total} passed ({avg_score:.1f}%)")
        else:
            print(f"     No data found for {mode_display}")
    
    conn.close()
    print("\n" + "=" * 70)

if __name__ == "__main__":
    export_latest_eval()

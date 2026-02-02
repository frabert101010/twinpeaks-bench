import sqlite3
from datetime import datetime

class EvalLogger:
    def __init__(self, db_path="eval_history.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                question TEXT NOT NULL,
                expected_answer TEXT,
                category TEXT,
                eval_name TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                eval_id INTEGER NOT NULL,
                model_name TEXT NOT NULL,
                response TEXT,
                error TEXT,
                latency_seconds REAL,
                FOREIGN KEY (eval_id) REFERENCES evaluations (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✓ Database initialized: {self.db_path}")
    
    def log_evaluation(self, question, expected_answer, category="general", eval_name="manual_test"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO evaluations (timestamp, question, expected_answer, category, eval_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), question, expected_answer, category, eval_name))
        
        eval_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return eval_id
    
    def log_model_response(self, eval_id, model_name, response, error=None, latency=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO model_responses 
            (eval_id, model_name, response, error, latency_seconds)
            VALUES (?, ?, ?, ?, ?)
        ''', (eval_id, model_name, response, error, latency))
        
        conn.commit()
        conn.close()
    
    def get_stats(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM evaluations')
        total_evals = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT model_name, 
                   COUNT(*) as total_responses,
                   AVG(latency_seconds) as avg_latency
            FROM model_responses
            GROUP BY model_name
        ''')
        
        model_stats = cursor.fetchall()
        conn.close()
        
        return {
            'total_evaluations': total_evals,
            'model_stats': model_stats
        }

if __name__ == "__main__":
    logger = EvalLogger()
    print("✓ Eval logger ready!")

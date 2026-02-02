from eval_logger import EvalLogger
from datetime import datetime

logger = EvalLogger()

print("\n" + "="*70)
print("EVALUATION HISTORY")
print("="*70)

stats = logger.get_stats()

print(f"\n📊 STATS:")
print(f"   Total Evaluations: {stats['total_evaluations']}")
print(f"\n   Model Performance:")

for model, count, latency in stats['model_stats']:
    latency_str = f"{latency:.2f}s" if latency else "N/A"
    print(f"   • {model:20s}: {count} tests, {latency_str} avg latency")

print("\n" + "="*70)
print("View detailed history:")
print("  sqlite3 eval_history.db 'SELECT * FROM evaluations;'")
print("  sqlite3 eval_history.db 'SELECT * FROM model_responses;'")
print("="*70 + "\n")

import csv
import json
from datetime import datetime

# Read the CSV file
csv_path = "/Users/francescobertolini/Downloads/TwinPeaks Bench  - Prompts_V1.csv"
output_path = "/Users/francescobertolini/Desktop/Eval/llm_eval_pipeline/eval_set_v1.json"

test_cases = []

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for idx, row in enumerate(reader, start=1):
        test_case = {
            "id": f"twin_peaks_{idx:03d}",
            "category": "twin_peaks",
            "domain": row['Domain'],
            "prompt": row['Question'],
            "expected_answer": row['Answer']
        }
        test_cases.append(test_case)

# Create the eval set structure
eval_set = {
    "eval_name": "TwinPeaks Bench V1",
    "version": "1.0",
    "created_at": datetime.now().strftime("%Y-%m-%d"),
    "description": f"TwinPeaks knowledge evaluation benchmark with {len(test_cases)} questions covering obscure details from the series - V1 prompts",
    "test_cases": test_cases
}

# Write to JSON file
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(eval_set, f, indent=2, ensure_ascii=False)

print(f"✓ Created eval_set_v1.json with {len(test_cases)} test cases")
print(f"  Output: {output_path}")

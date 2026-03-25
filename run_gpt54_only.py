"""
Run TwinPeaks Bench evaluation for GPT-5.4, GPT-5.4-mini, GPT-5.4-nano
and merge results into the main CSV without touching existing model data.
"""
import anthropic
import openai
import json
import os
import csv
import time
import statistics
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from eval_logger import EvalLogger

load_dotenv()

MODELS = ["GPT-5.4", "GPT-5.4-mini", "GPT-5.4-nano"]
MODEL_IDS = {
    "GPT-5.4":      "gpt-5.4",
    "GPT-5.4-mini": "gpt-5.4-mini",
    "GPT-5.4-nano": "gpt-5.4-nano",
}


class GPT54Runner:
    def __init__(self):
        self.logger = EvalLogger()
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')

        self.clients = {}
        if anthropic_key:
            self.clients['anthropic'] = anthropic.Anthropic(api_key=anthropic_key)
        if openai_key:
            self.clients['openai'] = openai.OpenAI(api_key=openai_key)

        self.all_responses = []
        self.run_id = datetime.now().strftime('%Y%m%d_%H%M%S')

    def call_model(self, model_name, question, use_search=False):
        model_id = MODEL_IDS[model_name]
        max_retries = 5

        for attempt in range(max_retries):
            try:
                if use_search:
                    response = self.clients['openai'].responses.create(
                        model=model_id,
                        tools=[{"type": "web_search"}],
                        tool_choice="auto",
                        input=question
                    )
                    return response.output_text, None
                else:
                    response = self.clients['openai'].chat.completions.create(
                        model=model_id,
                        messages=[{"role": "user", "content": question}],
                        max_completion_tokens=500
                    )
                    return response.choices[0].message.content, None

            except Exception as e:
                error_msg = str(e)
                retryable = ["504", "503", "429", "500", "timeout", "Timeout",
                             "RESOURCE_EXHAUSTED", "UNAVAILABLE"]
                if any(r in error_msg for r in retryable) and attempt < max_retries - 1:
                    wait = 2 ** attempt
                    print(f" (retry {attempt+1}/{max_retries} after {wait}s)...", end="", flush=True)
                    time.sleep(wait)
                    continue
                return None, f"{model_name} error: {error_msg[:200]}"

        return None, f"{model_name}: max retries reached"

    def judge_response(self, question, expected_answer, response):
        judge_prompt = f"""You are evaluating an AI's answer to a question.

QUESTION: {question}

CORRECT ANSWER: {expected_answer}

AI'S ANSWER:
{response}

Evaluate if the AI's answer is correct.

Respond with ONLY a JSON object:
{{"score": 0 or 1, "reasoning": "brief explanation"}}

Score 1 if correct, 0 if incorrect."""

        try:
            judge_response = self.clients['anthropic'].messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=200,
                messages=[{"role": "user", "content": judge_prompt}]
            )
            judge_text = judge_response.content[0].text.strip()
            if judge_text.startswith('```'):
                judge_text = judge_text.split('```')[1]
                if judge_text.startswith('json'):
                    judge_text = judge_text[4:]
                judge_text = judge_text.strip()
            result = json.loads(judge_text)
            return result['score'], result['reasoning']
        except Exception as e:
            return 0, str(e)

    def run_single_mode(self, eval_data, num_trials, use_search=False):
        mode_name = "WITH SEARCH" if use_search else "NO SEARCH"
        test_cases = eval_data['test_cases']

        print(f"\n{'='*70}")
        print(f"MODE: {mode_name}")
        print(f"{'='*70}\n")

        results = {}

        for test_case in test_cases:
            test_id = test_case['id']
            question = test_case['prompt']
            expected = test_case['expected_answer']

            print(f"\n📝 {test_id}: {question[:70]}...")
            print("-" * 70)

            eval_name = f"{eval_data.get('eval_name', 'benchmark')} ({mode_name}) - RUN_{self.run_id}"
            eval_id = self.logger.log_evaluation(
                question=question,
                expected_answer=expected,
                category=test_case.get('category', 'general'),
                eval_name=eval_name
            )

            results[test_id] = {}

            for model_name in MODELS:
                print(f"\n  {model_name}:")
                model_results = []

                for trial in range(num_trials):
                    print(f"    Trial {trial+1}/{num_trials}...", end=" ", flush=True)

                    start_time = time.time()
                    response, error = self.call_model(model_name, question, use_search=use_search)
                    latency = time.time() - start_time

                    if response:
                        score, reasoning = self.judge_response(question, expected, response)

                        self.logger.log_model_response(
                            eval_id=eval_id,
                            model_name=model_name,
                            response=response,
                            error=None,
                            latency=latency
                        )
                        conn = sqlite3.connect('eval_history.db')
                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE model_responses
                            SET score = ?, reasoning = ?
                            WHERE eval_id = ? AND model_name = ? AND response = ?
                        ''', (score, reasoning, eval_id, model_name, response))
                        conn.commit()
                        conn.close()

                        self.all_responses.append({
                            'question_id': test_id,
                            'question': question,
                            'expected_answer': expected,
                            'category': test_case.get('category', 'general'),
                            'model': model_name,
                            'mode': mode_name,
                            'trial': trial + 1,
                            'response': response,
                            'score': score,
                            'reasoning': reasoning,
                            'latency': latency
                        })
                        model_results.append(score)
                        print("✅" if score == 1 else "❌")
                    else:
                        self.logger.log_model_response(
                            eval_id=eval_id,
                            model_name=model_name,
                            response=None,
                            error=error or "Unknown error",
                            latency=latency
                        )
                        self.all_responses.append({
                            'question_id': test_id,
                            'question': question,
                            'expected_answer': expected,
                            'category': test_case.get('category', 'general'),
                            'model': model_name,
                            'mode': mode_name,
                            'trial': trial + 1,
                            'response': f"ERROR: {error or 'Unknown error'}",
                            'score': 0,
                            'reasoning': 'API Error',
                            'latency': latency
                        })
                        model_results.append(0)
                        print("❌")

                    time.sleep(0.5)

                results[test_id][model_name] = model_results

        return results

    def merge_into_main_csv(self):
        """Append new results to twinpeaks_v1_detailed_results.csv."""
        main_csv = 'twinpeaks_v1_detailed_results.csv'
        fieldnames = ['question_id', 'question', 'expected_answer', 'category',
                      'model', 'mode', 'trial', 'response', 'score', 'reasoning', 'latency']

        with open(main_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            for r in self.all_responses:
                writer.writerow({k: r[k] for k in fieldnames})

        print(f"✅ Appended {len(self.all_responses)} rows to {main_csv}")

    def recalculate_summary_csv(self):
        """Recalculate twinpeaks_v1_summary_results.csv from the full detailed CSV."""
        from collections import defaultdict

        rows = []
        with open('twinpeaks_v1_detailed_results.csv', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                if row['question_id'] != 'unknown':
                    rows.append(row)

        # Group by model + mode
        groups = defaultdict(list)
        for r in rows:
            groups[(r['model'], r['mode'])].append(r)

        summary_rows = []
        for (model, mode), group_rows in sorted(groups.items()):
            # Group by question to calculate pass@1 and pass@3
            by_question = defaultdict(list)
            for r in group_rows:
                by_question[r['question_id']].append(r)

            pass1_scores, pass3_scores, all_scores = [], [], []
            for q_rows in by_question.values():
                q_rows_sorted = sorted(q_rows, key=lambda x: int(x['trial']))
                scores = [int(r['score']) for r in q_rows_sorted]
                pass1_scores.append(scores[0] if scores else 0)
                pass3_scores.append(1 if any(scores) else 0)
                all_scores.extend(scores)

            n = len(pass1_scores)
            pass1 = round(sum(pass1_scores) / n * 100, 2) if n else 0
            pass3 = round(sum(pass3_scores) / n * 100, 2) if n else 0
            accuracy = round(sum(all_scores) / len(all_scores) * 100, 2) if all_scores else 0

            summary_rows.append({'model': model, 'mode': mode,
                                  'pass@1': pass1, 'pass@3': pass3, 'accuracy': accuracy})

        with open('twinpeaks_v1_summary_results.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['model', 'mode', 'pass@1', 'pass@3', 'accuracy'])
            writer.writeheader()
            writer.writerows(summary_rows)

        print(f"✅ Recalculated summary: {len(summary_rows)} model/mode rows")
        for r in summary_rows:
            if r['model'] in MODELS:
                print(f"   {r['model']:20s} {r['mode']:12s}  pass@1={r['pass@1']}%  pass@3={r['pass@3']}%  accuracy={r['accuracy']}%")

    def run(self, eval_file='eval_set_v1.json', num_trials=3):
        with open(eval_file) as f:
            eval_data = json.load(f)

        print("\n" + "="*70)
        print(f"GPT-5.4 / GPT-5.4-mini / GPT-5.4-nano Benchmark")
        print(f"RUN ID: {self.run_id}")
        print("="*70)
        print(f"Questions:  {len(eval_data['test_cases'])}")
        print(f"Models:     {', '.join(MODELS)}")
        print(f"Trials:     {num_trials}")
        print(f"Modes:      NO SEARCH + WITH SEARCH")
        print("="*70)

        self.run_single_mode(eval_data, num_trials, use_search=False)
        self.run_single_mode(eval_data, num_trials, use_search=True)

        print("\n\n" + "="*70)
        print("MERGING INTO MAIN CSV")
        print("="*70)
        self.merge_into_main_csv()
        self.recalculate_summary_csv()


if __name__ == "__main__":
    runner = GPT54Runner()
    runner.run(eval_file='eval_set_v1.json', num_trials=3)

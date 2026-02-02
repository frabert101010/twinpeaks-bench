import anthropic
import openai
from google import generativeai as genai
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import time
from eval_logger import EvalLogger
import csv
import sqlite3
import statistics

load_dotenv()

class DryRunBenchmark:
    def __init__(self):
        self.logger = EvalLogger()
        
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        google_key = os.getenv('GOOGLE_API_KEY')
        
        self.clients = {}
        
        if anthropic_key:
            self.clients['anthropic'] = anthropic.Anthropic(api_key=anthropic_key)
        if openai_key:
            self.clients['openai'] = openai.OpenAI(api_key=openai_key)
        if google_key:
            genai.configure(api_key=google_key)
            self.clients['google'] = True
        
        self.all_responses = []
        self.run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def call_model(self, model_name, question, use_search=False):
        try:
            if model_name == "Claude Sonnet 4.5":
                if use_search:
                    response = self.clients['anthropic'].messages.create(
                        model="claude-sonnet-4-5-20250929",
                        max_tokens=500,
                        messages=[{"role": "user", "content": question}],
                        tools=[{"type": "web_search_20250305", "name": "web_search"}]
                    )
                else:
                    response = self.clients['anthropic'].messages.create(
                        model="claude-sonnet-4-5-20250929",
                        max_tokens=500,
                        messages=[{"role": "user", "content": question}]
                    )
                text_parts = [block.text for block in response.content if hasattr(block, 'text')]
                return ' '.join(text_parts), None
            
            elif model_name == "Claude Opus 4.5":
                if use_search:
                    response = self.clients['anthropic'].messages.create(
                        model="claude-opus-4-5-20251101",
                        max_tokens=500,
                        messages=[{"role": "user", "content": question}],
                        tools=[{"type": "web_search_20250305", "name": "web_search"}]
                    )
                else:
                    response = self.clients['anthropic'].messages.create(
                        model="claude-opus-4-5-20251101",
                        max_tokens=500,
                        messages=[{"role": "user", "content": question}]
                    )
                text_parts = [block.text for block in response.content if hasattr(block, 'text')]
                return ' '.join(text_parts), None
            
            elif model_name == "GPT-5.2":
                response = self.clients['openai'].chat.completions.create(
                    model="gpt-5.2",
                    messages=[{"role": "user", "content": question}],
                    max_completion_tokens=500
                )
                return response.choices[0].message.content, None
            
            elif model_name == "Gemini 3":
                if use_search:
                    model = genai.GenerativeModel(
                        'gemini-3-pro-preview',
                        tools='google_search'
                    )
                else:
                    model = genai.GenerativeModel('gemini-3-pro-preview')
                
                response = model.generate_content(question)
                return response.text, None
            
        except Exception as e:
            return None, str(e)
        
        return None, "Unknown model"
    
    def judge_response(self, question, expected_answer, response):
        if 'anthropic' not in self.clients:
            return None, "No judge available"
        
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
    
    def run_single_mode(self, question, expected, test_id, category, models, num_trials, use_search=False):
        mode_name = "WITH SEARCH" if use_search else "NO SEARCH"
        
        print(f"\n{'='*70}")
        print(f"MODE: {mode_name}")
        print(f"{'='*70}\n")
        
        results = {}
        
        print(f"📝 Testing: {test_id}")
        print(f"Question: {question}")
        print(f"Expected: {expected}")
        print("-" * 70)
        
        eval_name = f"DRY RUN ({mode_name}) - RUN_{self.run_id}"
        eval_id = self.logger.log_evaluation(
            question=question,
            expected_answer=expected,
            category=category,
            eval_name=eval_name
        )
        
        for model_name in models:
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
                        'category': category,
                        'model': model_name,
                        'mode': mode_name,
                        'trial': trial + 1,
                        'response': response,
                        'score': score,
                        'reasoning': reasoning,
                        'latency': latency
                    })
                    
                    model_results.append(score)
                    status = "✅" if score == 1 else "❌"
                    print(f"{status}")
                    
                else:
                    self.logger.log_model_response(
                        eval_id=eval_id,
                        model_name=model_name,
                        response=None,
                        error=error if error else "Unknown error",
                        latency=latency
                    )
                    
                    self.all_responses.append({
                        'question_id': test_id,
                        'question': question,
                        'expected_answer': expected,
                        'category': category,
                        'model': model_name,
                        'mode': mode_name,
                        'trial': trial + 1,
                        'response': f"ERROR: {error if error else 'Unknown error'}",
                        'score': 0,
                        'reasoning': 'API Error',
                        'latency': latency
                    })
                    
                    print(f"❌")
                    model_results.append(0)
                
                time.sleep(0.5)
            
            results[model_name] = model_results
        
        return results
    
    def calculate_stats(self, results_no_search, results_with_search, num_trials):
        stats = {}
        models = list(results_no_search.keys())
        
        for model in models:
            stats[model] = {}
            
            for mode_name, results in [("No Search", results_no_search), ("With Search", results_with_search)]:
                scores = results[model]
                
                pass1 = scores[0] * 100
                passN = (1 if any(scores) else 0) * 100
                accuracy = statistics.mean(scores) * 100 if scores else 0
                
                stats[model][mode_name] = {
                    'pass@1': pass1,
                    f'pass@{num_trials}': passN,
                    'accuracy': accuracy
                }
        
        return stats
    
    def run_dry_run(self, num_trials=5):
        with open('eval_set.json', 'r') as f:
            eval_data = json.load(f)
        
        first_question = eval_data['test_cases'][0]
        question = first_question['prompt']
        expected = first_question['expected_answer']
        test_id = first_question['id']
        category = first_question.get('category', 'general')
        
        models = ["Claude Sonnet 4.5", "Claude Opus 4.5", "GPT-5.2", "Gemini 3"]
        
        print("\n" + "="*70)
        print("DRY RUN TEST - SINGLE QUESTION")
        print(f"RUN ID: {self.run_id}")
        print("="*70)
        print(f"Question: {question}")
        print(f"Models: {len(models)}")
        print(f"Trials per model: {num_trials}")
        print(f"Modes: No Search + With Search")
        print(f"Total tests: {len(models) * num_trials * 2}")
        print("="*70)
        
        results_no_search = self.run_single_mode(question, expected, test_id, category, models, num_trials, use_search=False)
        results_with_search = self.run_single_mode(question, expected, test_id, category, models, num_trials, use_search=True)
        
        stats = self.calculate_stats(results_no_search, results_with_search, num_trials)
        self.display_results(stats, num_trials)
        self.export_all(stats, num_trials)
        
        return {
            'no_search': results_no_search,
            'with_search': results_with_search,
            'stats': stats
        }
    
    def display_results(self, stats, num_trials):
        print("\n\n" + "="*70)
        print("DRY RUN RESULTS")
        print("="*70)
        
        print(f"\n📊 METRICS:")
        print("="*70)
        print(f"{'Model':<20} {'Mode':<15} {'Accuracy':<12} {'Pass@1':<12} {'Pass@' + str(num_trials):<10}")
        print("-" * 70)
        
        for model, mode_stats in stats.items():
            for mode, metrics in mode_stats.items():
                acc = metrics['accuracy']
                pass1 = metrics['pass@1']
                passN = metrics[f'pass@{num_trials}']
                
                print(f"{model:<20} {mode:<15} {acc:>6.1f}%      {pass1:>6.1f}%      {passN:>6.1f}%")
        
        print("\n" + "="*70)
    
    def export_all(self, stats, num_trials):
        summary_file = f"dryrun_summary_{self.run_id}.csv"
        
        with open(summary_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Model', 'Mode', 'Accuracy (%)', 'Pass@1 (%)', f'Pass@{num_trials} (%)'])
            
            for model, mode_stats in stats.items():
                for mode, metrics in mode_stats.items():
                    writer.writerow([
                        model,
                        mode,
                        f"{metrics['accuracy']:.1f}",
                        f"{metrics['pass@1']:.1f}",
                        f"{metrics[f'pass@{num_trials}']:.1f}"
                    ])
        
        print(f"\n📊 Summary exported to: {summary_file}")
        
        detailed_file = f"dryrun_detailed_{self.run_id}.csv"
        
        with open(detailed_file, 'w', newline='', encoding='utf-8') as f:
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
                'Latency (s)'
            ])
            
            for resp in self.all_responses:
                writer.writerow([
                    resp['question_id'],
                    resp['question'],
                    resp['expected_answer'],
                    resp['category'],
                    resp['model'],
                    resp['mode'],
                    resp['trial'],
                    resp['response'],
                    resp['score'],
                    'PASS' if resp['score'] == 1 else 'FAIL',
                    resp['reasoning'],
                    f"{resp['latency']:.2f}"
                ])
        
        print(f"📋 Detailed responses exported to: {detailed_file}")
        print("\n" + "="*70)
        print(f"✅ Dry run complete! RUN_ID: {self.run_id}")
        print("="*70)
        print("\nIf results look good, run the full benchmark:")
        print("  python3 run_full_benchmark.py")
        print("="*70)

if __name__ == "__main__":
    runner = DryRunBenchmark()
    runner.run_dry_run(num_trials=5)

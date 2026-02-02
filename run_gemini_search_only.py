import anthropic
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

class GeminiBenchmark:
    def __init__(self):
        self.logger = EvalLogger()
        
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        google_key = os.getenv('GOOGLE_API_KEY')
        
        self.clients = {}
        
        if anthropic_key:
            self.clients['anthropic'] = anthropic.Anthropic(api_key=anthropic_key)
        if google_key:
            genai.configure(api_key=google_key)
            self.clients['google'] = True
        
        self.all_responses = []
        self.run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def call_gemini(self, question):
        """Call Gemini with retry logic for intermittent errors"""
        model = genai.GenerativeModel('gemini-3-pro-preview')
        
        # Try up to 3 times to handle intermittent function call errors
        for attempt in range(3):
            try:
                # Don't mention "search" - just ask the question directly
                response = model.generate_content(question)
                
                # Check if we got text back
                if hasattr(response, 'text') and response.text:
                    return response.text, None
                else:
                    # No text - function call error likely
                    if attempt < 2:  # Try again
                        time.sleep(1)
                        continue
                    else:
                        return None, "Gemini returned no text after 3 attempts"
                        
            except Exception as e:
                error_msg = str(e)
                
                # If it's the function call error, try again
                if "finish_reason" in error_msg or "FunctionCall" in error_msg:
                    if attempt < 2:
                        time.sleep(1)  # Brief pause before retry
                        continue
                    else:
                        return None, f"Gemini function call error: {error_msg[:100]}"
                else:
                    # Other error - return immediately
                    return None, error_msg
        
        return None, "Gemini: Max retries reached"
    
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
    
    def run_benchmark(self, eval_file='eval_set.json', num_trials=3):
        with open(eval_file, 'r') as f:
            eval_data = json.load(f)
        
        test_cases = eval_data['test_cases']
        
        print("\n" + "="*70)
        print(f"GEMINI 3 BENCHMARK (NO SEARCH)")
        print(f"RUN ID: {self.run_id}")
        print("="*70)
        print(f"Questions: {len(test_cases)}")
        print(f"Model: Gemini 3")
        print(f"Trials per question: {num_trials}")
        print(f"Total tests: {len(test_cases) * num_trials}")
        print("="*70)
        
        results = {}
        
        for test_case in test_cases:
            test_id = test_case['id']
            question = test_case['prompt']
            expected = test_case['expected_answer']
            
            print(f"\n📝 Testing: {test_id}")
            print(f"Question: {question[:80]}...")
            print("-" * 70)
            
            eval_name = f"{eval_data.get('eval_name', 'benchmark')} (GEMINI NO SEARCH) - RUN_{self.run_id}"
            eval_id = self.logger.log_evaluation(
                question=question,
                expected_answer=expected,
                category=test_case.get('category', 'general'),
                eval_name=eval_name
            )
            
            model_results = []
            
            for trial in range(num_trials):
                print(f"  Trial {trial+1}/{num_trials}...", end=" ", flush=True)
                
                start_time = time.time()
                response, error = self.call_gemini(question)
                latency = time.time() - start_time
                
                if response:
                    score, reasoning = self.judge_response(question, expected, response)
                    
                    self.logger.log_model_response(
                        eval_id=eval_id,
                        model_name="Gemini 3",
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
                    ''', (score, reasoning, eval_id, "Gemini 3", response))
                    conn.commit()
                    conn.close()
                    
                    self.all_responses.append({
                        'question_id': test_id,
                        'question': question,
                        'expected_answer': expected,
                        'category': test_case.get('category', 'general'),
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
                        model_name="Gemini 3",
                        response=None,
                        error=error if error else "Unknown error",
                        latency=latency
                    )
                    
                    self.all_responses.append({
                        'question_id': test_id,
                        'question': question,
                        'expected_answer': expected,
                        'category': test_case.get('category', 'general'),
                        'trial': trial + 1,
                        'response': f"ERROR: {error if error else 'Unknown error'}",
                        'score': 0,
                        'reasoning': 'API Error',
                        'latency': latency
                    })
                    
                    print(f"❌")
                    model_results.append(0)
                
                time.sleep(0.5)
            
            results[test_id] = model_results
        
        self.display_results(results, num_trials)
        self.export_results(results, num_trials)
        
        return results
    
    def display_results(self, results, num_trials):
        print("\n\n" + "="*70)
        print("GEMINI 3 - RESULTS")
        print("="*70)
        
        # Calculate overall metrics
        all_pass1 = []
        all_passN = []
        all_scores = []
        
        for test_id, scores in results.items():
            all_pass1.append(scores[0] if scores else 0)
            all_passN.append(1 if any(scores) else 0)
            all_scores.extend(scores)
        
        pass1 = statistics.mean(all_pass1) * 100 if all_pass1 else 0
        passN = statistics.mean(all_passN) * 100 if all_passN else 0
        accuracy = statistics.mean(all_scores) * 100 if all_scores else 0
        
        print(f"\n📊 METRICS:")
        print("="*70)
        print(f"Accuracy:  {accuracy:>6.1f}%")
        print(f"Pass@1:    {pass1:>6.1f}%")
        print(f"Pass@{num_trials}:    {passN:>6.1f}%")
        print("="*70)
        
        print("\n📋 PER-QUESTION RESULTS:")
        print("-" * 70)
        for test_id, scores in results.items():
            success_rate = sum(scores) / len(scores) * 100 if scores else 0
            print(f"{test_id:<20}: {sum(scores)}/{len(scores)} correct ({success_rate:.1f}%)")
        
        print("\n" + "="*70)
    
    def export_results(self, results, num_trials):
        """Export results to CSV"""
        
        # Summary CSV
        summary_file = f"gemini_summary_{self.run_id}.csv"
        
        all_pass1 = []
        all_passN = []
        all_scores = []
        
        for test_id, scores in results.items():
            all_pass1.append(scores[0] if scores else 0)
            all_passN.append(1 if any(scores) else 0)
            all_scores.extend(scores)
        
        pass1 = statistics.mean(all_pass1) * 100 if all_pass1 else 0
        passN = statistics.mean(all_passN) * 100 if all_passN else 0
        accuracy = statistics.mean(all_scores) * 100 if all_scores else 0
        
        with open(summary_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Model', 'Mode', 'Accuracy (%)', 'Pass@1 (%)', f'Pass@{num_trials} (%)'])
            writer.writerow(['Gemini 3', 'No Search', f"{accuracy:.1f}", f"{pass1:.1f}", f"{passN:.1f}"])
        
        print(f"\n📊 Summary exported to: {summary_file}")
        
        # Detailed CSV
        detailed_file = f"gemini_detailed_{self.run_id}.csv"
        
        with open(detailed_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Question ID',
                'Question',
                'Expected Answer',
                'Category',
                'Trial',
                'Response',
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
                    resp['trial'],
                    resp['response'],
                    resp['score'],
                    'PASS' if resp['score'] == 1 else 'FAIL',
                    resp['reasoning'],
                    f"{resp['latency']:.2f}"
                ])
        
        print(f"📋 Detailed responses exported to: {detailed_file}")
        print("\n" + "="*70)
        print(f"✅ Gemini results exported with RUN_ID: {self.run_id}")
        print("="*70)

if __name__ == "__main__":
    runner = GeminiBenchmark()
    runner.run_benchmark(num_trials=3)

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

load_dotenv()

class SingleQuestionRerun:
    def __init__(self, question_id):
        self.question_id = question_id
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
                model = genai.GenerativeModel('gemini-3-pro-preview')
                
                for attempt in range(3):
                    try:
                        response = model.generate_content(question)
                        
                        if hasattr(response, 'text') and response.text:
                            return response.text, None
                        else:
                            if attempt < 2:
                                time.sleep(1)
                                continue
                            else:
                                return None, "Gemini returned no text after 3 attempts"
                                
                    except Exception as e:
                        error_msg = str(e)
                        
                        if "finish_reason" in error_msg or "FunctionCall" in error_msg:
                            if attempt < 2:
                                time.sleep(1)
                                continue
                            else:
                                return None, f"Gemini function call error: {error_msg[:100]}"
                        else:
                            return None, error_msg
                
                return None, "Gemini: Max retries reached"
            
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
    
    def run_retest(self, eval_file='eval_set.json', num_trials=3):
        with open(eval_file, 'r') as f:
            eval_data = json.load(f)
        
        # Find the specific question
        test_case = None
        for tc in eval_data['test_cases']:
            if tc['id'] == self.question_id:
                test_case = tc
                break
        
        if not test_case:
            print(f"❌ Question {self.question_id} not found!")
            return
        
        question = test_case['prompt']
        expected = test_case['expected_answer']
        
        models = ["Claude Sonnet 4.5", "Claude Opus 4.5", "GPT-5.2", "Gemini 3"]
        modes = [("NO SEARCH", False), ("WITH SEARCH", True)]
        
        print("\n" + "="*70)
        print(f"RERUNNING SINGLE QUESTION: {self.question_id}")
        print(f"RUN ID: {self.run_id}")
        print("="*70)
        print(f"Question: {question}")
        print(f"Expected: {expected}")
        print(f"Models: {len(models)}")
        print(f"Modes: 2 (No Search + With Search)")
        print(f"Trials: {num_trials}")
        print(f"Total tests: {len(models) * 2 * num_trials} (24)")
        print("="*70)
        
        results = {}
        
        for mode_name, use_search in modes:
            print(f"\n{'='*70}")
            print(f"MODE: {mode_name}")
            print(f"{'='*70}\n")
            
            eval_name = f"RERUN {self.question_id} ({mode_name}) - RUN_{self.run_id}"
            eval_id = self.logger.log_evaluation(
                question=question,
                expected_answer=expected,
                category=test_case.get('category', 'general'),
                eval_name=eval_name
            )
            
            for model_name in models:
                print(f"\n  {model_name}:")
                
                if model_name not in results:
                    results[model_name] = {}
                results[model_name][mode_name] = []
                
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
                            'question_id': self.question_id,
                            'question': question,
                            'expected_answer': expected,
                            'model': model_name,
                            'mode': mode_name,
                            'trial': trial + 1,
                            'response': response,
                            'score': score,
                            'reasoning': reasoning,
                            'latency': latency
                        })
                        
                        results[model_name][mode_name].append(score)
                        status = "✅" if score == 1 else "❌"
                        print(f"{status}")
                        
                    else:
                        print(f"❌ Error: {error[:50]}")
                        results[model_name][mode_name].append(0)
                    
                    time.sleep(0.5)
        
        self.display_results(results, num_trials)
        self.export_results(results)
    
    def display_results(self, results, num_trials):
        print("\n\n" + "="*70)
        print(f"RERUN RESULTS FOR {self.question_id}")
        print("="*70)
        
        print(f"\n{'Model':<25} {'No Search':<15} {'With Search':<15}")
        print("-" * 70)
        
        for model in results:
            no_search = results[model].get('NO SEARCH', [])
            with_search = results[model].get('WITH SEARCH', [])
            
            no_search_result = f"{sum(no_search)}/{len(no_search)}"
            with_search_result = f"{sum(with_search)}/{len(with_search)}"
            
            print(f"{model:<25} {no_search_result:<15} {with_search_result:<15}")
        
        print("\n" + "="*70)
    
    def export_results(self, results):
        output_file = f"rerun_{self.question_id}_{self.run_id}.csv"
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Question ID',
                'Question',
                'Expected Answer',
                'Model',
                'Mode',
                'Trial',
                'Response',
                'Score',
                'Pass/Fail',
                'Judge Reasoning',
                'Latency'
            ])
            
            for resp in self.all_responses:
                writer.writerow([
                    resp['question_id'],
                    resp['question'],
                    resp['expected_answer'],
                    resp['model'],
                    resp['mode'],
                    resp['trial'],
                    resp['response'],
                    resp['score'],
                    'PASS' if resp['score'] == 1 else 'FAIL',
                    resp['reasoning'],
                    f"{resp['latency']:.2f}"
                ])
        
        print(f"\n📊 Results exported to: {output_file}")
        print("="*70)

if __name__ == "__main__":
    rerunner = SingleQuestionRerun("twin_peaks_016")
    rerunner.run_retest(num_trials=3)

import anthropic
import openai
from google import generativeai as genai
import json
import os
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm
import time

# Load environment variables
load_dotenv()

class LLMEvaluator:
    def __init__(self):
        """Initialize API clients with keys from .env file"""
        # Load API keys
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        google_key = os.getenv('GOOGLE_API_KEY')
        
        # Validate keys exist
        if not all([anthropic_key, openai_key, google_key]):
            missing = []
            if not anthropic_key: missing.append('ANTHROPIC_API_KEY')
            if not openai_key: missing.append('OPENAI_API_KEY')
            if not google_key: missing.append('GOOGLE_API_KEY')
            raise ValueError(f"Missing API keys in .env file: {', '.join(missing)}")
        
        # Initialize clients
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
        self.openai_client = openai.OpenAI(api_key=openai_key)
        genai.configure(api_key=google_key)
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("✓ All API clients initialized successfully!")
        
    def call_claude(self, prompt, model="claude-sonnet-4-20250514"):
        """Call Claude API"""
        try:
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error calling Claude: {e}")
            return f"ERROR: {str(e)}"
    
    def call_chatgpt(self, prompt, model="gpt-4o-mini"):
        """Call ChatGPT API"""
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling ChatGPT: {e}")
            return f"ERROR: {str(e)}"
    
    def call_gemini(self, prompt):
        """Call Gemini API"""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return f"ERROR: {str(e)}"
    
    def evaluate_response(self, response, test_case):
        """Evaluate a single response based on the test case criteria"""
        
        # Check for API errors
        if response.startswith("ERROR:"):
            return 0, "API Error"
        
        criteria = test_case.get('evaluation_criteria', {})
        eval_type = criteria.get('type', 'llm_judge')
        
        if eval_type == 'exact_match':
            acceptable = criteria.get('acceptable_answers', [])
            response_clean = response.strip().lower()
            is_correct = any(response_clean == ans.lower() for ans in acceptable)
            return (1, "Exact match") if is_correct else (0, "No match")
        
        elif eval_type == 'contains':
            required = criteria.get('must_contain', [])
            response_lower = response.lower()
            found = [keyword for keyword in required if keyword.lower() in response_lower]
            score = len(found) / len(required) if required else 0
            return (1 if score == 1 else 0, f"Found {len(found)}/{len(required)} keywords")
        
        elif eval_type == 'numerical':
            try:
                # Extract numbers from response
                import re
                numbers = re.findall(r'-?\d+\.?\d*', response)
                if numbers:
                    extracted = float(numbers[0])
                    correct = criteria['correct_value']
                    tolerance = criteria.get('tolerance', 0)
                    is_correct = abs(extracted - correct) <= tolerance
                    return (1, f"Extracted: {extracted}") if is_correct else (0, f"Expected {correct}, got {extracted}")
                else:
                    return (0, "No number found in response")
            except Exception as e:
                return (0, f"Error parsing number: {e}")
        
        elif eval_type == 'llm_judge':
            score, reasoning = self.llm_as_judge(response, test_case)
            return (score, reasoning)
        
        return (0, "Unknown evaluation type")
    
    def llm_as_judge(self, response, test_case):
        """Use Claude as a judge to evaluate responses"""
        
        expected = test_case.get('expected_answer', '')
        rubric = test_case.get('rubric', {})
        
        judge_prompt = f"""You are evaluating an AI response. Score it as 1 (correct/good) or 0 (incorrect/poor).

QUESTION: {test_case['prompt']}

EXPECTED ANSWER/CRITERIA: {expected if expected else json.dumps(rubric, indent=2)}

ACTUAL RESPONSE TO EVALUATE:
{response}

Evaluate based on:
- Accuracy: Is the information correct?
- Completeness: Does it address all parts of the question?
- Clarity: Is it well-explained?

Respond with ONLY a JSON object in this exact format:
{{"score": 0, "reasoning": "brief explanation"}}
or
{{"score": 1, "reasoning": "brief explanation"}}"""
        
        try:
            judge_response = self.call_claude(judge_prompt, model="claude-haiku-4-5-20251001")
            # Try to parse JSON
            judge_response_clean = judge_response.strip()
            if judge_response_clean.startswith('```'):
                # Remove markdown code blocks
                judge_response_clean = judge_response_clean.split('```')[1]
                if judge_response_clean.startswith('json'):
                    judge_response_clean = judge_response_clean[4:]
            
            result = json.loads(judge_response_clean)
            return result['score'], result['reasoning']
        except Exception as e:
            print(f"Judge parsing error: {e}")
            # Fallback: simple keyword check
            if 'correct' in judge_response.lower() or 'good' in judge_response.lower():
                return 1, "Fallback: positive keywords found"
            return 0, f"Fallback: parsing failed - {str(e)[:50]}"
    
    def run_evaluation(self, eval_data, models_to_test=None):
        """Run full evaluation across all models"""
        
        if models_to_test is None:
            models_to_test = ['claude', 'chatgpt', 'gemini']
        
        results = []
        test_cases = eval_data['test_cases']
        
        print(f"\n{'='*60}")
        print(f"Running evaluation: {eval_data.get('eval_name', 'Unnamed Eval')}")
        print(f"Total test cases: {len(test_cases)}")
        print(f"Models to test: {', '.join(models_to_test)}")
        print(f"{'='*60}\n")
        
        for test_case in tqdm(test_cases, desc="Processing test cases"):
            test_id = test_case['id']
            prompt = test_case['prompt']
            category = test_case.get('category', 'general')
            
            # Get responses from selected models
            responses = {}
            if 'claude' in models_to_test:
                print(f"\n  Testing Claude on {test_id}...")
                responses['claude'] = self.call_claude(prompt)
                time.sleep(0.5)  # Rate limiting
            
            if 'chatgpt' in models_to_test:
                print(f"  Testing ChatGPT on {test_id}...")
                responses['chatgpt'] = self.call_chatgpt(prompt)
                time.sleep(0.5)
            
            if 'gemini' in models_to_test:
                print(f"  Testing Gemini on {test_id}...")
                responses['gemini'] = self.call_gemini(prompt)
                time.sleep(0.5)
            
            # Evaluate each response
            for model_name, response in responses.items():
                score, reasoning = self.evaluate_response(response, test_case)
                
                results.append({
                    'timestamp': datetime.now().isoformat(),
                    'test_id': test_id,
                    'category': category,
                    'model': model_name,
                    'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt,
                    'response': response[:500] + '...' if len(response) > 500 else response,
                    'score': score,
                    'reasoning': reasoning
                })
        
        return pd.DataFrame(results)
    
    def calculate_metrics(self, results_df):
        """Calculate summary metrics from results"""
        
        metrics = {
            'overall_completion_rate': results_df.groupby('model')['score'].mean() * 100,
            'category_breakdown': results_df.groupby(['model', 'category'])['score'].mean() * 100,
            'total_tests': results_df.groupby('model').size(),
            'passed_tests': results_df[results_df['score'] == 1].groupby('model').size(),
            'failed_tests': results_df[results_df['score'] == 0].groupby('model').size()
        }
        
        return metrics
    
    def print_summary(self, results_df):
        """Print a summary of the evaluation results"""
        
        metrics = self.calculate_metrics(results_df)
        
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        
        print("\nOverall Completion Rates:")
        print("-" * 40)
        for model, rate in metrics['overall_completion_rate'].items():
            passed = metrics['passed_tests'].get(model, 0)
            total = metrics['total_tests'].get(model, 0)
            print(f"{model:12s}: {rate:5.1f}% ({passed}/{total} passed)")
        
        print("\nBy Category:")
        print("-" * 40)
        for (model, category), rate in metrics['category_breakdown'].items():
            print(f"{model:12s} - {category:15s}: {rate:5.1f}%")
        
        # Show failures
        failures = results_df[results_df['score'] == 0]
        if len(failures) > 0:
            print(f"\nFailed Tests: {len(failures)}")
            print("-" * 40)
            for _, row in failures.iterrows():
                print(f"{row['model']:12s} - {row['test_id']:10s}: {row['reasoning']}")
        
        print("\n" + "="*60)


def main():
    """Main execution function"""
    
    # Initialize evaluator
    evaluator = LLMEvaluator()
    
    # Load evaluation set
    print("\nLoading evaluation set...")
    with open('eval_set.json', 'r') as f:
        eval_data = json.load(f)
    
    # Run evaluation
    results_df = evaluator.run_evaluation(eval_data)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"results_{timestamp}.csv"
    results_df.to_csv(results_file, index=False)
    print(f"\n✓ Results saved to: {results_file}")
    
    # Print summary
    evaluator.print_summary(results_df)
    
    # Save summary to JSON
    metrics = evaluator.calculate_metrics(results_df)
    summary_file = f"summary_{timestamp}.json"
    with open(summary_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'overall_rates': metrics['overall_completion_rate'].to_dict(),
            'category_breakdown': {f"{m}_{c}": v for (m,c), v in metrics['category_breakdown'].items()},
            'test_counts': metrics['total_tests'].to_dict()
        }, f, indent=2)
    print(f"✓ Summary saved to: {summary_file}")


if __name__ == "__main__":
    main()

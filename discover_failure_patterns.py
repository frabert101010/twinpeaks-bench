import csv
import json
from collections import defaultdict, Counter
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

class FailurePatternDiscovery:
    def __init__(self, csv_files):
        self.csv_files = csv_files if isinstance(csv_files, list) else [csv_files]
        self.data = []
        self.failures = []
        self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
    def normalize_row(self, row):
        """Normalize column names across different CSV formats"""
        normalized = {}
        
        # Try different possible column names
        normalized['question_id'] = row.get('Question ID', row.get('question_id', ''))
        normalized['question'] = row.get('Question', row.get('question', ''))
        normalized['expected'] = row.get('Expected Answer', row.get('expected', ''))
        normalized['category'] = row.get('Category', row.get('category', ''))
        normalized['model'] = row.get('Model', row.get('model', ''))
        normalized['mode'] = row.get('Mode', row.get('mode', ''))
        normalized['trial'] = row.get('Trial', row.get('trial', ''))
        normalized['response'] = row.get('Model Response', row.get('Response', row.get('response', '')))
        normalized['pass_fail'] = row.get('Pass/Fail', row.get('pass_fail', ''))
        normalized['judge_reasoning'] = row.get('Judge Reasoning', row.get('judge_reasoning', ''))
        
        return normalized
        
    def load_data(self):
        """Load all CSV files"""
        print("📂 Loading results from all files...")
        
        for csv_file in self.csv_files:
            print(f"  Loading {csv_file}...")
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                raw_data = list(reader)
                
                # Normalize all rows
                normalized_data = [self.normalize_row(row) for row in raw_data]
                self.data.extend(normalized_data)
        
        # Filter failures
        self.failures = [row for row in self.data if row['pass_fail'] == 'FAIL']
        
        print(f"\n✅ Loaded {len(self.data)} total responses")
        print(f"❌ Found {len(self.failures)} failures to analyze\n")
    
    def discover_patterns(self):
        """Step 1: Use Claude to discover common failure patterns from actual data"""
        
        print("🔍 STEP 1: Discovering failure patterns from data...\n")
        
        # Sample failures for pattern discovery (max 20 to keep prompt manageable)
        sample_size = min(20, len(self.failures))
        sample_failures = self.failures[:sample_size]
        
        # Build prompt with actual failures
        failure_examples = ""
        for i, failure in enumerate(sample_failures, 1):
            failure_examples += f"""
FAILURE {i}:
Question: {failure['question']}
Expected: {failure['expected']}
Model Response: {failure['response'][:200]}
Judge Reason: {failure['judge_reasoning']}
---
"""
        
        discovery_prompt = f"""Analyze these {sample_size} actual LLM failures and identify 5-7 common FAILURE PATTERNS.

Look for recurring themes in WHY the models failed. These patterns should be:
- Data-driven (based on what you see)
- Distinct from each other
- Actionable (help identify what to fix)

{failure_examples}

Respond with ONLY a JSON array of patterns:
[
  {{"pattern_name": "SHORT_NAME", "description": "what this pattern means", "indicators": ["sign 1", "sign 2"]}},
  ...
]

Pattern names should be UPPERCASE_WITH_UNDERSCORES."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1000,
                messages=[{"role": "user", "content": discovery_prompt}]
            )
            
            text = response.content[0].text.strip()
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
                text = text.strip()
            
            patterns = json.loads(text)
            
            print("📋 DISCOVERED PATTERNS:")
            print("="*70)
            for p in patterns:
                print(f"\n{p['pattern_name']}")
                print(f"  {p['description']}")
                print(f"  Indicators: {', '.join(p['indicators'][:3])}")
            print("\n" + "="*70)
            
            return patterns
            
        except Exception as e:
            print(f"❌ Pattern discovery error: {e}")
            return []
    
    def categorize_with_patterns(self, patterns):
        """Step 2: Categorize all failures using discovered patterns"""
        
        print("\n🏷️  STEP 2: Categorizing all failures with discovered patterns...\n")
        
        # Build pattern list for prompt
        pattern_list = ""
        for p in patterns:
            pattern_list += f"- {p['pattern_name']}: {p['description']}\n"
        
        categorized = []
        
        for i, failure in enumerate(self.failures, 1):
            print(f"Categorizing {i}/{len(self.failures)}...", end="\r")
            
            categorize_prompt = f"""Given these failure patterns:

{pattern_list}

Categorize this failure into the MOST appropriate pattern:

Question: {failure['question']}
Expected: {failure['expected']}
Model Response: {failure['response'][:300]}
Judge Reasoning: {failure['judge_reasoning']}

Respond with ONLY a JSON object:
{{"pattern": "PATTERN_NAME", "confidence": "high/medium/low", "explanation": "why this pattern"}}"""

            try:
                response = self.client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=150,
                    messages=[{"role": "user", "content": categorize_prompt}]
                )
                
                text = response.content[0].text.strip()
                if text.startswith('```'):
                    text = text.split('```')[1]
                    if text.startswith('json'):
                        text = text[4:]
                    text = text.strip()
                
                result = json.loads(text)
                pattern = result['pattern']
                explanation = result['explanation']
                confidence = result.get('confidence', 'medium')
                
            except Exception as e:
                pattern = "UNCATEGORIZED"
                explanation = str(e)
                confidence = "low"
            
            categorized.append({
                'question_id': failure['question_id'],
                'question': failure['question'],
                'category': failure['category'],
                'model': failure['model'],
                'mode': failure['mode'],
                'trial': failure['trial'],
                'expected': failure['expected'],
                'response': failure['response'],
                'judge_reasoning': failure['judge_reasoning'],
                'pattern': pattern,
                'confidence': confidence,
                'explanation': explanation
            })
        
        print("\n✅ Categorization complete!\n")
        return categorized
    
    def generate_analysis(self, patterns, categorized):
        """Step 3: Generate comprehensive analysis"""
        
        print("\n" + "="*70)
        print("FAILURE ANALYSIS REPORT (DATA-DRIVEN)")
        print("="*70)
        
        # Overall stats
        total_tests = len(self.data)
        total_failures = len(self.failures)
        failure_rate = (total_failures / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL STATISTICS:")
        print("-"*70)
        print(f"Total Tests: {total_tests}")
        print(f"Total Failures: {total_failures}")
        print(f"Failure Rate: {failure_rate:.1f}%")
        
        # Pattern distribution
        print(f"\n\n🏷️  FAILURE PATTERN DISTRIBUTION:")
        print("-"*70)
        pattern_counts = Counter(item['pattern'] for item in categorized)
        
        for pattern, count in pattern_counts.most_common():
            pct = (count / len(categorized) * 100) if categorized else 0
            
            # Find pattern description
            pattern_desc = next((p['description'] for p in patterns if p['pattern_name'] == pattern), "Unknown")
            
            print(f"\n{pattern} ({count} failures, {pct:.1f}%)")
            print(f"  → {pattern_desc}")
        
        # Model analysis
        print(f"\n\n🤖 FAILURES BY MODEL:")
        print("-"*70)
        model_data = defaultdict(lambda: defaultdict(int))
        
        for item in categorized:
            model_data[item['model']][item['pattern']] += 1
        
        for model in sorted(model_data.keys()):
            patterns_for_model = model_data[model]
            total_model_failures = sum(patterns_for_model.values())
            
            print(f"\n{model} ({total_model_failures} failures):")
            for pattern, count in sorted(patterns_for_model.items(), key=lambda x: x[1], reverse=True):
                pct = (count / total_model_failures * 100) if total_model_failures > 0 else 0
                print(f"  {pattern:<30} {count:>3} ({pct:>5.1f}%)")
        
        # Mode analysis
        print(f"\n\n🔍 FAILURES BY MODE (Search On/Off):")
        print("-"*70)
        mode_data = defaultdict(lambda: defaultdict(int))
        
        for item in categorized:
            mode_data[item['mode']][item['pattern']] += 1
        
        for mode in sorted(mode_data.keys()):
            patterns_for_mode = mode_data[mode]
            total_mode_failures = sum(patterns_for_mode.values())
            
            print(f"\n{mode} ({total_mode_failures} failures):")
            for pattern, count in sorted(patterns_for_mode.items(), key=lambda x: x[1], reverse=True):
                pct = (count / total_mode_failures * 100) if total_mode_failures > 0 else 0
                print(f"  {pattern:<30} {count:>3} ({pct:>5.1f}%)")
        
        # Question analysis
        print(f"\n\n❗ MOST PROBLEMATIC QUESTIONS:")
        print("-"*70)
        question_failures = defaultdict(list)
        for item in categorized:
            key = (item['question_id'], item['question'])
            question_failures[key].append(item)
        
        sorted_questions = sorted(question_failures.items(), key=lambda x: len(x[1]), reverse=True)[:5]
        
        for (qid, question), failures in sorted_questions:
            print(f"\n{qid} ({len(failures)} failures)")
            print(f"  Q: {question[:70]}...")
            
            # Show pattern breakdown
            patterns = Counter(f['pattern'] for f in failures)
            for pattern, count in patterns.most_common(3):
                print(f"    • {pattern}: {count}")
        
        # Examples
        print(f"\n\n📝 EXAMPLE FAILURES BY PATTERN:")
        print("="*70)
        
        for pattern in pattern_counts.most_common():
            pattern_name = pattern[0]
            examples = [item for item in categorized if item['pattern'] == pattern_name][:2]
            
            if examples:
                pattern_desc = next((p['description'] for p in patterns if p['pattern_name'] == pattern_name), "")
                print(f"\n{pattern_name}")
                print(f"Description: {pattern_desc}")
                print("-"*70)
                
                for ex in examples:
                    print(f"Model: {ex['model']} | Mode: {ex['mode']}")
                    print(f"Q: {ex['question'][:60]}...")
                    print(f"Expected: {ex['expected']}")
                    print(f"Got: {ex['response'][:100]}...")
                    print(f"Analysis: {ex['explanation']}")
                    print()
        
        print("="*70)
        
        return {
            'total_tests': total_tests,
            'total_failures': total_failures,
            'failure_rate': failure_rate,
            'pattern_counts': dict(pattern_counts),
            'model_data': {k: dict(v) for k, v in model_data.items()},
            'mode_data': {k: dict(v) for k, v in mode_data.items()}
        }
    
    def export_results(self, patterns, categorized, stats):
        """Export analysis results"""
        
        # 1. Export patterns
        patterns_file = 'discovered_patterns.json'
        with open(patterns_file, 'w', encoding='utf-8') as f:
            json.dump(patterns, f, indent=2)
        print(f"\n📋 Discovered patterns saved to: {patterns_file}")
        
        # 2. Export categorized failures
        categorized_file = 'failures_categorized.csv'
        with open(categorized_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Question ID', 'Question', 'Category', 'Expected Answer', 
                'Model', 'Mode', 'Trial', 'Model Response', 
                'Failure Pattern', 'Confidence', 'Pattern Explanation', 'Judge Reasoning'
            ])
            
            for item in categorized:
                writer.writerow([
                    item['question_id'],
                    item['question'],
                    item['category'],
                    item['expected'],
                    item['model'],
                    item['mode'],
                    item['trial'],
                    item['response'],
                    item['pattern'],
                    item['confidence'],
                    item['explanation'],
                    item['judge_reasoning']
                ])
        
        print(f"📊 Categorized failures exported to: {categorized_file}")
        
        # 3. Export summary
        summary_file = 'failure_summary.csv'
        with open(summary_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Tests', stats['total_tests']])
            writer.writerow(['Total Failures', stats['total_failures']])
            writer.writerow(['Failure Rate (%)', f"{stats['failure_rate']:.1f}"])
            writer.writerow([])
            writer.writerow(['Failure Pattern', 'Count', 'Percentage'])
            
            total_categorized = sum(stats['pattern_counts'].values())
            for pattern, count in sorted(stats['pattern_counts'].items(), key=lambda x: x[1], reverse=True):
                pct = (count / total_categorized * 100) if total_categorized > 0 else 0
                writer.writerow([pattern, count, f"{pct:.1f}"])
        
        print(f"📈 Summary statistics exported to: {summary_file}")
    
    def run(self):
        """Run the complete discovery and analysis pipeline"""
        self.load_data()
        
        if not self.failures:
            print("🎉 No failures to analyze!")
            return
        
        # Step 1: Discover patterns
        patterns = self.discover_patterns()
        
        if not patterns:
            print("❌ Could not discover patterns")
            return
        
        # Step 2: Categorize all failures
        categorized = self.categorize_with_patterns(patterns)
        
        # Step 3: Generate analysis
        stats = self.generate_analysis(patterns, categorized)
        
        # Step 4: Export results
        self.export_results(patterns, categorized, stats)
        
        print("\n" + "="*70)
        print("✅ Analysis complete!")
        print("="*70)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 discover_failure_patterns.py <file1.csv> [file2.csv] ...")
        print("\nExample:")
        print("  python3 discover_failure_patterns.py results_detailed_*.csv")
        sys.exit(1)
    
    csv_files = sys.argv[1:]
    analyzer = FailurePatternDiscovery(csv_files)
    analyzer.run()

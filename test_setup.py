#!/usr/bin/env python3
"""
Quick test script to verify your setup is working
"""

import os
import sys
from dotenv import load_dotenv

def test_imports():
    """Test that all required packages are installed"""
    print("Testing package imports...")
    
    packages = {
        'anthropic': 'Anthropic',
        'openai': 'OpenAI',
        'google.generativeai': 'Google Generative AI',
        'pandas': 'Pandas',
        'plotly': 'Plotly',
        'dotenv': 'Python-dotenv',
        'tqdm': 'TQDM'
    }
    
    failed = []
    for package, name in packages.items():
        try:
            if '.' in package:
                parts = package.split('.')
                mod = __import__(parts[0])
                for part in parts[1:]:
                    mod = getattr(mod, part)
            else:
                __import__(package)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - NOT INSTALLED")
            failed.append(package)
    
    if failed:
        print(f"\n❌ Missing packages: {', '.join(failed)}")
        print("   Install with: pip install -r requirements.txt")
        return False
    
    print("\n✅ All packages installed correctly!\n")
    return True

def test_env_file():
    """Test that .env file exists and has keys"""
    print("Testing .env configuration...")
    
    if not os.path.exists('.env'):
        print("  ✗ .env file not found")
        print("\n❌ Please create .env file with your API keys")
        print("   Run: python setup.py")
        return False
    
    print("  ✓ .env file exists")
    
    load_dotenv()
    
    keys = {
        'ANTHROPIC_API_KEY': 'Anthropic',
        'OPENAI_API_KEY': 'OpenAI',
        'GOOGLE_API_KEY': 'Google'
    }
    
    found_keys = []
    missing_keys = []
    
    for key_name, service in keys.items():
        value = os.getenv(key_name)
        if value and not value.startswith('your_'):
            print(f"  ✓ {service} API key found")
            found_keys.append(service)
        else:
            print(f"  ✗ {service} API key not set")
            missing_keys.append(service)
    
    if not found_keys:
        print("\n❌ No API keys configured")
        print("   Run: python setup.py")
        return False
    
    if missing_keys:
        print(f"\n⚠️  Warning: Missing keys for {', '.join(missing_keys)}")
        print("   You can still test with the configured models")
    
    print(f"\n✅ API keys configured for: {', '.join(found_keys)}\n")
    return True

def test_api_connections():
    """Test that we can actually connect to the APIs"""
    print("Testing API connections...")
    
    load_dotenv()
    
    # Test Anthropic
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if anthropic_key and not anthropic_key.startswith('your_'):
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            print("  ✓ Anthropic API connection successful")
        except Exception as e:
            print(f"  ✗ Anthropic API error: {str(e)[:50]}...")
    
    # Test OpenAI
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and not openai_key.startswith('your_'):
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            print("  ✓ OpenAI API connection successful")
        except Exception as e:
            print(f"  ✗ OpenAI API error: {str(e)[:50]}...")
    
    # Test Google
    google_key = os.getenv('GOOGLE_API_KEY')
    if google_key and not google_key.startswith('your_'):
        try:
            import google.generativeai as genai
            genai.configure(api_key=google_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Hi")
            print("  ✓ Google API connection successful")
        except Exception as e:
            print(f"  ✗ Google API error: {str(e)[:50]}...")
    
    print("\n✅ API connection tests complete!\n")

def test_eval_file():
    """Test that eval_set.json exists and is valid"""
    print("Testing evaluation set...")
    
    if not os.path.exists('eval_set.json'):
        print("  ✗ eval_set.json not found")
        return False
    
    print("  ✓ eval_set.json exists")
    
    try:
        import json
        with open('eval_set.json', 'r') as f:
            data = json.load(f)
        
        if 'test_cases' not in data:
            print("  ✗ No test_cases found in eval_set.json")
            return False
        
        num_tests = len(data['test_cases'])
        print(f"  ✓ Found {num_tests} test cases")
        
        # Check test case structure
        required_fields = ['id', 'prompt']
        for i, test in enumerate(data['test_cases'][:3]):  # Check first 3
            missing = [f for f in required_fields if f not in test]
            if missing:
                print(f"  ✗ Test {i+1} missing fields: {missing}")
                return False
        
        print("  ✓ Test cases are properly formatted")
        
    except json.JSONDecodeError as e:
        print(f"  ✗ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error reading file: {e}")
        return False
    
    print("\n✅ Evaluation set is valid!\n")
    return True

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("LLM Evaluation Pipeline - System Test")
    print("="*60 + "\n")
    
    all_passed = True
    
    # Run tests
    if not test_imports():
        all_passed = False
    
    if not test_env_file():
        all_passed = False
    else:
        # Only test connections if .env is configured
        test_api_connections()
    
    if not test_eval_file():
        all_passed = False
    
    # Final summary
    print("="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nYou're ready to run evaluations!")
        print("\nNext steps:")
        print("  1. Run: python evaluator.py")
        print("  2. Wait for results")
        print("  3. Run: python visualize.py")
        print("  4. Open evaluation_report.html in your browser")
    else:
        print("❌ SOME TESTS FAILED")
        print("="*60)
        print("\nPlease fix the issues above before running evaluations.")
        print("\nCommon fixes:")
        print("  • Missing packages: pip install -r requirements.txt")
        print("  • Missing .env: python setup.py")
        print("  • API errors: Check your API keys and credits")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

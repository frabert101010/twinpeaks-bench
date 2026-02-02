#!/usr/bin/env python3
"""
Setup helper for LLM Evaluation Pipeline
This script helps you configure your API keys interactively
"""

import os
from pathlib import Path

def create_env_file():
    """Interactive setup for .env file"""
    
    print("="*60)
    print("LLM Evaluation Pipeline - Setup")
    print("="*60)
    print("\nThis script will help you set up your API keys.")
    print("You'll need keys from:")
    print("  • Anthropic (Claude): https://console.anthropic.com")
    print("  • OpenAI (ChatGPT): https://platform.openai.com/api-keys")
    print("  • Google (Gemini): https://ai.google.dev")
    print("\n" + "="*60 + "\n")
    
    # Check if .env already exists
    if Path('.env').exists():
        response = input(".env file already exists. Overwrite? (y/n): ").lower()
        if response != 'y':
            print("Setup cancelled. Existing .env file preserved.")
            return
    
    # Get API keys
    print("Enter your API keys (press Enter to skip):\n")
    
    anthropic_key = input("Anthropic API Key: ").strip()
    openai_key = input("OpenAI API Key: ").strip()
    google_key = input("Google API Key: ").strip()
    
    # Validate at least one key is provided
    if not any([anthropic_key, openai_key, google_key]):
        print("\n❌ Error: You must provide at least one API key!")
        return
    
    # Create .env file
    env_content = f"""# LLM Evaluation Pipeline - API Keys
# Generated: {os.popen('date').read().strip()}

ANTHROPIC_API_KEY={anthropic_key if anthropic_key else 'your_anthropic_api_key_here'}
OPENAI_API_KEY={openai_key if openai_key else 'your_openai_api_key_here'}
GOOGLE_API_KEY={google_key if google_key else 'your_google_api_key_here'}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n" + "="*60)
    print("✅ Setup complete!")
    print("="*60)
    print("\n.env file created successfully!")
    
    # Show which keys were set
    print("\nConfigured keys:")
    if anthropic_key:
        print(f"  ✓ Anthropic (Claude): {anthropic_key[:10]}...")
    else:
        print("  ✗ Anthropic (Claude): Not set")
    
    if openai_key:
        print(f"  ✓ OpenAI (ChatGPT): {openai_key[:10]}...")
    else:
        print("  ✗ OpenAI (ChatGPT): Not set")
    
    if google_key:
        print(f"  ✓ Google (Gemini): {google_key[:10]}...")
    else:
        print("  ✗ Google (Gemini): Not set")
    
    print("\n" + "="*60)
    print("Next steps:")
    print("  1. Review your .env file to ensure keys are correct")
    print("  2. Run: python evaluator.py")
    print("="*60)

def verify_setup():
    """Verify that setup is complete"""
    
    print("\n" + "="*60)
    print("Verification Check")
    print("="*60 + "\n")
    
    # Check if .env exists
    if not Path('.env').exists():
        print("❌ .env file not found!")
        print("   Run this setup script first or copy .env.example to .env")
        return False
    
    # Check if required packages are installed
    required_packages = [
        'anthropic',
        'openai',
        'google.generativeai',
        'pandas',
        'plotly',
        'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('.', '-'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n   Install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    
    # Try to load .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        google_key = os.getenv('GOOGLE_API_KEY')
        
        keys_found = []
        if anthropic_key and not anthropic_key.startswith('your_'):
            keys_found.append('Anthropic')
        if openai_key and not openai_key.startswith('your_'):
            keys_found.append('OpenAI')
        if google_key and not google_key.startswith('your_'):
            keys_found.append('Google')
        
        if keys_found:
            print(f"✅ API keys found: {', '.join(keys_found)}")
        else:
            print("❌ No valid API keys found in .env file")
            print("   Edit .env and add your API keys")
            return False
        
    except Exception as e:
        print(f"❌ Error loading .env file: {e}")
        return False
    
    print("\n✅ Setup verification complete!")
    print("   You're ready to run evaluations!")
    return True

def main():
    """Main setup function"""
    
    print("\n🤖 LLM Evaluation Pipeline Setup\n")
    print("Choose an option:")
    print("  1. Configure API keys (create/update .env)")
    print("  2. Verify setup")
    print("  3. View current configuration")
    print("  4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        create_env_file()
    elif choice == '2':
        verify_setup()
    elif choice == '3':
        if Path('.env').exists():
            print("\nCurrent .env contents:")
            print("="*60)
            with open('.env', 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        value = value.strip()
                        if value and not value.startswith('your_'):
                            print(f"{key}={value[:15]}..." if len(value) > 15 else f"{key}={value}")
                        else:
                            print(f"{key}=(not set)")
            print("="*60)
        else:
            print("\n❌ .env file not found. Run setup first (option 1).")
    elif choice == '4':
        print("\nGoodbye! 👋")
    else:
        print("\n❌ Invalid choice. Please run again.")

if __name__ == "__main__":
    main()

import anthropic
import openai
from google import genai  # New google-genai library for Gemini 3
from google.genai import types as genai_types
import os
from dotenv import load_dotenv
import time
import json

load_dotenv()

class SearchVerificationTest:
    def __init__(self):
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        google_key = os.getenv('GOOGLE_API_KEY')

        self.clients = {}

        if anthropic_key:
            self.clients['anthropic'] = anthropic.Anthropic(api_key=anthropic_key)
        if openai_key:
            self.clients['openai'] = openai.OpenAI(api_key=openai_key)
        if google_key:
            # Use new google-genai client for Gemini 3
            self.clients['google'] = genai.Client(api_key=google_key)

    def test_claude_sonnet(self, question, use_search=False):
        """Test Claude Sonnet 4.5"""
        print(f"\n{'='*70}")
        print(f"🔍 Claude Sonnet 4.5 - {'WITH SEARCH' if use_search else 'NO SEARCH'}")
        print(f"{'='*70}")

        try:
            if use_search:
                print("✓ Adding web_search_20250305 tool to API call")
                response = self.clients['anthropic'].messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=500,
                    messages=[{"role": "user", "content": question}],
                    tools=[{"type": "web_search_20250305", "name": "web_search"}]
                )
            else:
                print("✓ Calling without search tools")
                response = self.clients['anthropic'].messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=500,
                    messages=[{"role": "user", "content": question}]
                )

            # Check for tool use in response
            has_tool_use = any(block.type == 'tool_use' for block in response.content)
            if has_tool_use:
                print("✅ VERIFIED: Model used search tool!")
                tool_uses = [block for block in response.content if block.type == 'tool_use']
                for tool in tool_uses:
                    print(f"   - Tool: {tool.name}")
            else:
                print("⚠️  No tool use detected in response")

            text_parts = [block.text for block in response.content if hasattr(block, 'text')]
            answer = ' '.join(text_parts)

            print(f"\n📝 Response: {answer[:300]}...")
            return answer, None

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return None, str(e)

    def test_gpt(self, model_name, api_model, question, use_search=False):
        """Test GPT models"""
        print(f"\n{'='*70}")
        print(f"🔍 {model_name} - {'WITH SEARCH' if use_search else 'NO SEARCH'}")
        print(f"{'='*70}")

        try:
            if use_search:
                print("✓ Using Responses API with web_search tool")
                response = self.clients['openai'].responses.create(
                    model=api_model,
                    tools=[{"type": "web_search"}],
                    tool_choice="auto",
                    input=question
                )

                # Check for search usage
                if hasattr(response, 'search_results') or hasattr(response, 'tool_calls'):
                    print("✅ VERIFIED: Model used search tool!")
                else:
                    print("⚠️  No explicit search indicator in response (but may have been used)")

                answer = response.output_text
                print(f"\n📝 Response: {answer[:300]}...")
                return answer, None
            else:
                print("✓ Using Chat Completions API without search tools")
                response = self.clients['openai'].chat.completions.create(
                    model=api_model,
                    messages=[{"role": "user", "content": question}],
                    max_completion_tokens=500
                )
                answer = response.choices[0].message.content
                print(f"\n📝 Response: {answer[:300]}...")
                return answer, None

        except Exception as e:
            error_msg = str(e)
            print(f"❌ ERROR: {error_msg}")

            # If it's an invalid tool error, the API doesn't support this format
            if "tools" in error_msg.lower() or "web_search" in error_msg.lower():
                print("⚠️  NOTE: This model may not support web_search tool in this format")

            return None, error_msg

    def test_gemini(self, model_name, api_model, question, use_search=False):
        """Test Gemini models using new google-genai library"""
        print(f"\n{'='*70}")
        print(f"🔍 {model_name} - {'WITH SEARCH' if use_search else 'NO SEARCH'}")
        print(f"{'='*70}")

        try:
            # Try up to 3 times
            for attempt in range(3):
                try:
                    if use_search:
                        print("✓ Using new google-genai API with google_search tool")
                        response = self.clients['google'].models.generate_content(
                            model=api_model,
                            contents=question,
                            config={'tools': [{'google_search': {}}]}
                        )
                    else:
                        print("✓ Using new google-genai API without search tools")
                        response = self.clients['google'].models.generate_content(
                            model=api_model,
                            contents=question
                        )

                    if hasattr(response, 'text') and response.text:
                        # Check for grounding metadata
                        if hasattr(response, 'grounding_metadata') and response.grounding_metadata:
                            print("✅ VERIFIED: Response has grounding metadata (search used)!")
                            if hasattr(response.grounding_metadata, 'web_search_queries'):
                                queries = response.grounding_metadata.web_search_queries
                                if queries:
                                    print(f"   - Search queries executed: {len(queries)}")
                            if hasattr(response.grounding_metadata, 'grounding_chunks'):
                                chunks = response.grounding_metadata.grounding_chunks
                                if chunks:
                                    print(f"   - Found {len(chunks)} grounding chunks (sources)")
                        else:
                            print("⚠️  No grounding metadata found")

                        answer = response.text
                        print(f"\n📝 Response: {answer[:300]}...")
                        return answer, None
                    else:
                        if attempt < 2:
                            time.sleep(1)
                            continue
                        else:
                            print(f"❌ ERROR: No text returned after 3 attempts")
                            return None, "No text after retries"

                except Exception as e:
                    error_msg = str(e)
                    if "finish_reason" in error_msg or "FunctionCall" in error_msg:
                        if attempt < 2:
                            time.sleep(1)
                            continue
                        else:
                            print(f"❌ ERROR: {error_msg[:150]}")
                            return None, error_msg
                    else:
                        print(f"❌ ERROR: {error_msg}")
                        return None, error_msg

            return None, "Max retries reached"

        except Exception as e:
            error_msg = str(e)
            print(f"❌ ERROR: {error_msg}")
            return None, error_msg

    def run_full_test(self):
        """Run complete search verification test"""

        # Use a question that requires recent/real-time information
        test_question = "Who won the 2024 World Series?"

        print("\n" + "="*70)
        print("🧪 SEARCH VERIFICATION TEST")
        print("="*70)
        print(f"\nTest Question: {test_question}")
        print("This question requires recent information to answer correctly.")
        print("\nExpected behavior:")
        print("  - WITHOUT search: Model may not know or give outdated answer")
        print("  - WITH search: Model should find current answer via web search")
        print("\n" + "="*70)

        results = []

        # Test each model in both modes
        models_to_test = [
            ("Claude Sonnet 4.5", "claude-sonnet-4-5-20250929", "claude"),
            ("Claude Opus 4.5", "claude-opus-4-5-20251101", "claude"),
            ("GPT-5.1", "gpt-5.1", "gpt"),
            ("GPT-5.2", "gpt-5.2", "gpt"),
            ("Gemini 3", "gemini-3-pro-preview", "gemini"),
            ("Gemini 3 Flash", "gemini-3-flash-preview", "gemini")
        ]

        for model_name, api_model, model_type in models_to_test:
            # Test WITHOUT search
            if model_type == "claude":
                if model_name == "Claude Sonnet 4.5":
                    answer_no_search, error = self.test_claude_sonnet(test_question, use_search=False)
                else:
                    # For Claude Opus, use similar logic
                    print(f"\n{'='*70}")
                    print(f"🔍 {model_name} - NO SEARCH")
                    print(f"{'='*70}")
                    try:
                        print("✓ Calling without search tools")
                        response = self.clients['anthropic'].messages.create(
                            model=api_model,
                            max_tokens=500,
                            messages=[{"role": "user", "content": test_question}]
                        )
                        text_parts = [block.text for block in response.content if hasattr(block, 'text')]
                        answer_no_search = ' '.join(text_parts)
                        error = None
                        print(f"\n📝 Response: {answer_no_search[:300]}...")
                    except Exception as e:
                        answer_no_search = None
                        error = str(e)
                        print(f"❌ ERROR: {error}")
            elif model_type == "gpt":
                answer_no_search, error = self.test_gpt(model_name, api_model, test_question, use_search=False)
            else:  # gemini
                answer_no_search, error = self.test_gemini(model_name, api_model, test_question, use_search=False)

            time.sleep(1)

            # Test WITH search
            if model_type == "claude":
                if model_name == "Claude Sonnet 4.5":
                    answer_with_search, error = self.test_claude_sonnet(test_question, use_search=True)
                else:
                    # For Claude Opus
                    print(f"\n{'='*70}")
                    print(f"🔍 {model_name} - WITH SEARCH")
                    print(f"{'='*70}")
                    try:
                        print("✓ Adding web_search_20250305 tool to API call")
                        response = self.clients['anthropic'].messages.create(
                            model=api_model,
                            max_tokens=500,
                            messages=[{"role": "user", "content": test_question}],
                            tools=[{"type": "web_search_20250305", "name": "web_search"}]
                        )
                        has_tool_use = any(block.type == 'tool_use' for block in response.content)
                        if has_tool_use:
                            print("✅ VERIFIED: Model used search tool!")
                        else:
                            print("⚠️  No tool use detected in response")
                        text_parts = [block.text for block in response.content if hasattr(block, 'text')]
                        answer_with_search = ' '.join(text_parts)
                        error = None
                        print(f"\n📝 Response: {answer_with_search[:300]}...")
                    except Exception as e:
                        answer_with_search = None
                        error = str(e)
                        print(f"❌ ERROR: {error}")
            elif model_type == "gpt":
                answer_with_search, error = self.test_gpt(model_name, api_model, test_question, use_search=True)
            else:  # gemini
                answer_with_search, error = self.test_gemini(model_name, api_model, test_question, use_search=True)

            results.append({
                'model': model_name,
                'no_search': answer_no_search if answer_no_search else f"ERROR: {error}",
                'with_search': answer_with_search if answer_with_search else f"ERROR: {error}"
            })

            time.sleep(1)

        # Print summary
        print("\n\n" + "="*70)
        print("📊 SUMMARY - SEARCH VERIFICATION RESULTS")
        print("="*70)

        for result in results:
            print(f"\n{result['model']}:")
            print(f"  Without Search: {result['no_search'][:100]}...")
            print(f"  With Search:    {result['with_search'][:100]}...")

            # Simple comparison
            if "ERROR" in result['with_search']:
                print(f"  ⚠️  Status: Search implementation may need adjustment")
            elif result['no_search'] != result['with_search']:
                print(f"  ✅ Status: Responses differ (search likely working)")
            else:
                print(f"  ⚠️  Status: Responses identical (search may not be active)")

        print("\n" + "="*70)
        print("✅ Test Complete!")
        print("="*70)

        # Save results
        import json
        from datetime import datetime

        output_file = f"search_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump({
                'test_question': test_question,
                'timestamp': datetime.now().isoformat(),
                'results': results
            }, f, indent=2)

        print(f"\n📄 Detailed results saved to: {output_file}")

if __name__ == "__main__":
    tester = SearchVerificationTest()
    tester.run_full_test()

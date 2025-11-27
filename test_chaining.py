"""
Quick test script to verify multi-quiz chaining works
"""
import requests
import json

# Test endpoint
API_URL = "http://localhost:8000/quiz"

# Test payload
payload = {
    "email": "test@example.com",
    "secret": "my-quiz-secret-2025",
    "url": "https://tds-llm-analysis.s-anand.net/demo"  # Use the demo URL
}

print("Testing multi-quiz chaining...")
print(f"Request URL: {API_URL}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("\n" + "="*60)

try:
    response = requests.post(API_URL, json=payload, timeout=120)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ SUCCESS!")
        print(f"Quizzes Solved: {result.get('quizzes_solved', 1)}")
        print(f"Time Taken: {result.get('time_taken', 0):.2f}s")
        print(f"Chain Complete: {result.get('chain_complete', True)}")
        print(f"Message: {result.get('message', 'N/A')}")
        
        # Show chain steps
        print(f"\n--- Chain Steps ---")
        for i, step in enumerate(result.get('steps', []), 1):
            step_name = step.get('step', 'unknown')
            if 'chain_continue' in step_name:
                print(f"{i}. {step_name} → Next URL: {step.get('next_url', 'N/A')}")
            elif 'load_quiz' in step_name:
                print(f"{i}. {step_name} → {step.get('url', 'N/A')}")
            else:
                print(f"{i}. {step_name}")
    else:
        print(f"\n✗ FAILED")
        print(f"Response: {response.text}")

except requests.exceptions.Timeout:
    print("\n✗ TIMEOUT - Request took too long")
except requests.exceptions.ConnectionError:
    print("\n✗ CONNECTION ERROR - Is the server running?")
    print("Start the server with: cd backend && python main.py")
except Exception as e:
    print(f"\n✗ ERROR: {e}")

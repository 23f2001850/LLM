"""
Complete Multi-Quiz Chaining Test
Tests the bot's ability to automatically follow quiz chains
"""
import subprocess
import time
import requests
import json
import sys

print("="*70)
print("MULTI-QUIZ CHAINING TEST")
print("="*70)

# Step 1: Start mock quiz server
print("\n[1/4] Starting mock quiz server...")
try:
    server_process = subprocess.Popen(
        ['python', 'mock_quiz_server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd='c:\\Krishna_Jain\\LLM'
    )
    print("✓ Mock server starting on http://localhost:3001")
    time.sleep(3)  # Wait for server to start
except Exception as e:
    print(f"✗ Failed to start mock server: {e}")
    sys.exit(1)

# Step 2: Verify mock server is running
print("\n[2/4] Verifying mock server...")
try:
    response = requests.get('http://localhost:3001/', timeout=5)
    if response.status_code == 200:
        print("✓ Mock server is running")
    else:
        print(f"✗ Mock server returned status {response.status_code}")
        server_process.kill()
        sys.exit(1)
except Exception as e:
    print(f"✗ Cannot connect to mock server: {e}")
    server_process.kill()
    sys.exit(1)

# Step 3: Test bot with quiz chain
print("\n[3/4] Testing bot with 3-quiz chain...")
print("     This should automatically solve all 3 quizzes")

payload = {
    "email": "test@example.com",
    "secret": "my-quiz-secret-2025",
    "url": "http://localhost:3001/quiz/1"
}

try:
    print(f"\nSending request to bot...")
    response = requests.post(
        'http://localhost:8000/quiz',
        json=payload,
        timeout=180
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n" + "="*70)
        print("RESULTS")
        print("="*70)
        
        quizzes_solved = result.get('quizzes_solved', 0)
        chain_complete = result.get('chain_complete', False)
        time_taken = result.get('time_taken', 0)
        
        print(f"\n✓ Status: {result.get('status', 'unknown')}")
        print(f"✓ Quizzes Solved: {quizzes_solved}")
        print(f"✓ Time Taken: {time_taken:.2f}s")
        print(f"✓ Chain Complete: {chain_complete}")
        print(f"✓ Message: {result.get('message', 'N/A')}")
        
        # Analyze steps
        print("\n--- CHAIN PROGRESSION ---")
        steps = result.get('steps', [])
        quiz_loads = [s for s in steps if 'load_quiz' in s.get('step', '')]
        chain_continues = [s for s in steps if 'chain_continue' in s.get('step', '')]
        
        print(f"Quiz loads: {len(quiz_loads)}")
        for step in quiz_loads:
            print(f"  • {step.get('step')}: {step.get('url', 'N/A')}")
        
        print(f"\nChain continuations: {len(chain_continues)}")
        for step in chain_continues:
            print(f"  • {step.get('step')}: → {step.get('next_url', 'N/A')}")
        
        # Final verdict
        print("\n" + "="*70)
        if quizzes_solved >= 3:
            print("✅ SUCCESS! Bot automatically solved all 3 quizzes in the chain!")
            print("✅ Multi-quiz chaining is working correctly!")
        elif quizzes_solved > 1:
            print(f"⚠️  PARTIAL: Bot solved {quizzes_solved} quizzes but stopped early")
            print("    Check if timeout or incorrect answer stopped the chain")
        else:
            print("❌ FAILED: Bot only solved 1 quiz - chaining not working")
            print("    Check next_url extraction in submitter.py")
        print("="*70)
        
    else:
        print(f"\n✗ Bot returned status {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("\n✗ TIMEOUT - Request took longer than 180 seconds")
except requests.exceptions.ConnectionError:
    print("\n✗ CONNECTION ERROR - Is your bot running on http://localhost:8000?")
    print("   Start it with: cd backend && python main.py")
except Exception as e:
    print(f"\n✗ ERROR: {e}")

# Step 4: Cleanup
print("\n[4/4] Cleaning up...")
try:
    server_process.kill()
    server_process.wait()
    print("✓ Mock server stopped")
except:
    print("⚠  Could not stop mock server cleanly")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)

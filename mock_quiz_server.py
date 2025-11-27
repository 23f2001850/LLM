"""
Mock Quiz Server for Testing Multi-Quiz Chaining
This simulates the actual evaluation server behavior
"""
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Quiz chain state
quiz_data = {
    1: {
        "question": "Calculate the sum of sales",
        "correct_answer": 1420,
        "next_quiz": 2
    },
    2: {
        "question": "Calculate the average temperature", 
        "correct_answer": 23.46,
        "next_quiz": 3
    },
    3: {
        "question": "Find the maximum score",
        "correct_answer": 98,
        "next_quiz": None  # End of chain
    }
}

@app.route('/quiz/<int:quiz_num>', methods=['GET'])
def get_quiz(quiz_num):
    """Serve quiz HTML"""
    if quiz_num not in quiz_data:
        return "Quiz not found", 404
    
    quiz = quiz_data[quiz_num]
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Quiz {quiz_num}</title>
    </head>
    <body>
        <h1>Quiz {quiz_num} of 3</h1>
        <p>{quiz['question']}</p>
        <a href="data:text/csv;base64,UHJvZHVjdCxTYWxlcwpMYXB0b3AsODUwCk1vdXNlLDI1CktleWJvYXJkLDc1Ck1vbml0b3IsMzUwCldlYmNhbSwxMjA=">Download Data</a>
        <form action="/submit/{quiz_num}" method="POST">
            <input type="email" name="email" required>
            <input type="text" name="answer" required>
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    """
    return html

@app.route('/submit/<int:quiz_num>', methods=['POST'])
def submit_answer(quiz_num):
    """Handle answer submission"""
    if quiz_num not in quiz_data:
        return jsonify({"error": "Quiz not found"}), 404
    
    quiz = quiz_data[quiz_num]
    
    # Get answer from request
    data = request.get_json() if request.is_json else request.form
    email = data.get('email', '')
    answer = data.get('answer', '')
    
    # Try to parse answer
    try:
        submitted = float(answer) if '.' in str(answer) else int(answer)
    except:
        submitted = str(answer)
    
    # Check if correct
    is_correct = submitted == quiz['correct_answer']
    
    response = {
        "correct": is_correct,
        "message": f"Quiz {quiz_num} {'correct' if is_correct else 'incorrect'}",
        "quiz_number": quiz_num,
        "email": email
    }
    
    # Add next URL if correct and not last quiz
    if is_correct and quiz['next_quiz']:
        next_url = f"http://localhost:3001/quiz/{quiz['next_quiz']}"
        response["next_url"] = next_url
        response["url"] = next_url
        print(f"✓ Quiz {quiz_num} correct! Next URL: {next_url}")
    elif is_correct:
        print(f"✓ Quiz {quiz_num} correct! Chain complete!")
    else:
        print(f"✗ Quiz {quiz_num} incorrect")
    
    return jsonify(response)

@app.route('/')
def index():
    return """
    <h1>Mock Quiz Server</h1>
    <p>Test multi-quiz chaining:</p>
    <ul>
        <li><a href="/quiz/1">Start Quiz Chain</a></li>
    </ul>
    <p>Or test with your bot:</p>
    <pre>
curl -X POST http://localhost:8000/quiz \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "test@example.com",
    "secret": "my-quiz-secret-2025",
    "url": "http://localhost:3001/quiz/1"
  }'
    </pre>
    """

if __name__ == '__main__':
    print("="*60)
    print("Mock Quiz Server Starting...")
    print("="*60)
    print("Server: http://localhost:3001")
    print("Start chain: http://localhost:3001/quiz/1")
    print("\nTest with your bot:")
    print('  URL: "http://localhost:3001/quiz/1"')
    print("="*60)
    app.run(host='0.0.0.0', port=3001, debug=False)

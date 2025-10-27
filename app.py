#!/usr/bin/env python3
"""
Flask Quiz Application - Data Types in JavaScript
Includes retry mechanism for incorrectly answered questions
Supports multiple retries until all questions are answered correctly
Shuffles questions and answer options on each quiz start
Supports inline fill-in-the-blank questions
Supports multiple-answer questions (select all that apply)
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import uuid
from datetime import datetime
import random
import copy
import platform
import qrcode
from io import BytesIO
import base64
import socket

app = Flask(__name__)
# Generate a new secret key each time the app starts
app.secret_key = str(uuid.uuid4())

def get_local_ip():
    """Get the local IP address that can reach external networks"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return socket.gethostbyname(socket.gethostname())

def generate_qr_code(url):
    """Generate a QR code and return as base64 string"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

def print_qr_code_terminal(url):
    """Print QR code in terminal with OS-specific rendering"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_matrix = qr.modules

    is_mac = platform.system() == "Darwin"

    if is_mac:
        # macOS-safe mode
        for row in qr_matrix:
            print(''.join('██' if cell else '  ' for cell in row))
    else:
        # Fancy half-block mode for Linux/Windows
        for i in range(0, len(qr_matrix), 2):
            line = ""
            for j in range(len(qr_matrix[0])):
                top = qr_matrix[i][j]
                bottom = qr_matrix[i+1][j] if i+1 < len(qr_matrix) else False
                if top and bottom:
                    line += "█"
                elif top:
                    line += "▀"
                elif bottom:
                    line += "▄"
                else:
                    line += " "
            print(line)

def load_quiz_data(quiz_name=None):
    """Load quiz data from JSON file"""
    if quiz_name is None:
        quiz_name = 'quiz_data'
    
    filename = f'{quiz_name}.json'
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

def get_available_quizzes():
    """Get list of all available quiz JSON files"""
    quizzes = []
    for filename in os.listdir('.'):
        if filename.startswith('quiz_data') and filename.endswith('.json'):
            quiz_name = filename.replace('.json', '')
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    title = data.get('title', quiz_name)
                    quizzes.append({
                        'name': quiz_name,
                        'filename': filename,
                        'title': title
                    })
            except (json.JSONDecodeError, IOError):
                pass
    
    # Sort by name to ensure consistent ordering
    quizzes.sort(key=lambda x: x['name'])
    return quizzes

def has_inline_blank(question_text):
    """Check if question text contains inline blank marker"""
    return '___blank___' in question_text or '[blank]' in question_text

def is_true_false_question(options):
    """Check if question is a True/False question"""
    if not options or len(options) != 2:
        return False
    
    values = [str(v).lower().strip() for v in options.values()]
    return set(values) == {'true', 'false'}

def shuffle_quiz_data(quiz_data):
    """
    Create a shuffled copy of quiz data with:
    1. Questions shuffled
    2. Answer options shuffled (for multiple choice and multiple answer)
    Note: True/False questions are NOT shuffled to maintain True, False order
    """
    shuffled_data = copy.deepcopy(quiz_data)
    
    # Shuffle questions
    random.shuffle(shuffled_data['questions'])
    
    # Shuffle answer options within each multiple choice or multiple answer question
    for question in shuffled_data['questions']:
        if question.get('type') in ['multiple_choice', 'multiple_answer']:
            options = question.get('options', {})
            
            # Check if this is a True/False question - if so, don't shuffle
            if is_true_false_question(options):
                continue
            
            # Create a list of (key, value) pairs
            option_items = list(options.items())
            
            # Get correct answer(s)
            correct_answer = question.get('correct_answer')
            
            # For multiple_choice, find the correct answer text
            # For multiple_answer, find all correct answer texts
            if question.get('type') == 'multiple_choice':
                correct_answer_texts = [options.get(correct_answer)]
            else:  # multiple_answer
                if isinstance(correct_answer, list):
                    correct_answer_texts = [options.get(ans) for ans in correct_answer]
                else:
                    correct_answer_texts = [options.get(correct_answer)]
            
            # Shuffle the options
            random.shuffle(option_items)
            
            # Rebuild the options dict with new indices
            new_options = {}
            new_correct_indices = []
            for new_index, (old_key, value) in enumerate(option_items):
                new_options[str(new_index)] = value
                # Track the new index of correct answer(s)
                if value in correct_answer_texts:
                    new_correct_indices.append(str(new_index))
            
            # Update the question with shuffled options and new correct answer index/indices
            question['options'] = new_options
            if question.get('type') == 'multiple_choice':
                question['correct_answer'] = new_correct_indices[0] if new_correct_indices else None
            else:  # multiple_answer
                question['correct_answer'] = new_correct_indices
    
    return shuffled_data

@app.after_request
def after_request(response):
    """Add headers to prevent caching"""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
    response.headers['Expires'] = '0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['X-Version'] = str(uuid.uuid4())
    return response

@app.route('/')
def selector():
    """Quiz selector page"""
    available_quizzes = get_available_quizzes()
    if not available_quizzes:
        return render_template('error.html', 
                             error="No quizzes found. Please ensure at least one quiz_data*.json file exists.")
    return render_template('index.html', quizzes=available_quizzes)

@app.route('/quiz')
def quiz():
    """Main quiz page"""
    selected_quiz = session.get('selected_quiz')
    if not selected_quiz:
        return redirect(url_for('selector'))
    
    quiz_data = load_quiz_data(selected_quiz)
    if not quiz_data:
        return redirect(url_for('selector'))
    
    # Initialize session on first visit to this quiz
    if 'shuffled_quiz' not in session:
        session['current_question'] = 0
        session['score'] = 0
        session['answers'] = {}
        session['missed_questions'] = []
        session['retry_mode'] = False
        session['retry_round'] = 0
        session['start_time'] = datetime.now().isoformat()
        shuffled_quiz = shuffle_quiz_data(quiz_data)
        session['shuffled_quiz'] = shuffled_quiz
    else:
        shuffled_quiz = session['shuffled_quiz']
    
    # Check if quiz is complete
    total_questions = len(shuffled_quiz['questions'])
    current_q_num = session.get('current_question', 0)
    
    if current_q_num >= total_questions and not session.get('retry_mode'):
        missed = session.get('missed_questions', [])
        if missed:
            session['retry_mode'] = True
            session['retry_round'] = session.get('retry_round', 0) + 1
            session['current_question'] = 0
            session.modified = True
            return redirect(url_for('quiz'))
        else:
            return redirect(url_for('results'))
    
    # Handle retry mode logic
    if session.get('retry_mode'):
        missed = session.get('missed_questions', [])
        retry_q_num = session.get('current_question', 0)
        
        if retry_q_num >= len(missed):
            all_correct = all(session['answers'].get(str(q_idx), {}).get('is_correct') for q_idx in missed)
            if all_correct:
                return redirect(url_for('results'))
            else:
                session['retry_round'] = session.get('retry_round', 0) + 1
                session['current_question'] = 0
                session.modified = True
                return redirect(url_for('quiz'))
        
        q_index = missed[retry_q_num]
        current_q = shuffled_quiz['questions'][q_index]
        question_num = retry_q_num + 1
        display_total = len(missed)
        phase = f"Retry #{session['retry_round']}"
    else:
        q_index = current_q_num
        if q_index >= total_questions:
            return redirect(url_for('results'))
        current_q = shuffled_quiz['questions'][q_index]
        question_num = current_q_num + 1
        display_total = total_questions
        phase = "Main"
    
    # Determine if this is an inline fill-in-the-blank
    is_inline_blank = (current_q.get('type') == 'fill_in_the_blank' and 
                       has_inline_blank(current_q.get('question', '')))
    
    session.modified = True
    return render_template('quiz.html',
                         quiz_data=shuffled_quiz,
                         current_question=current_q,
                         question_num=question_num,
                         total_questions=display_total,
                         phase=phase,
                         question_type=current_q.get('type', 'multiple_choice'),
                         is_inline_blank=is_inline_blank)

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    """Handle answer submission"""
    selected_quiz = session.get('selected_quiz', 'quiz_data')
    quiz_data = load_quiz_data(selected_quiz)
    if not quiz_data:
        return jsonify({'error': 'Quiz data not found'})
    
    # Get shuffled quiz from session
    shuffled_quiz = session.get('shuffled_quiz', shuffle_quiz_data(quiz_data))
    
    selected_answer = request.json.get('answer')
    current_q_index = session.get('current_question', 0)
    is_retry = session.get('retry_mode', False)
    
    # Get the actual question index
    if is_retry:
        missed = session.get('missed_questions', [])
        if current_q_index >= len(missed):
            return jsonify({'error': 'Quiz already complete'})
        actual_q_index = missed[current_q_index]
    else:
        if current_q_index >= len(shuffled_quiz['questions']):
            return jsonify({'error': 'Quiz already complete'})
        actual_q_index = current_q_index
    
    current_q = shuffled_quiz['questions'][actual_q_index]
    correct_answer = current_q.get('correct_answer')
    question_type = current_q.get('type', 'multiple_choice')
    
    # Handle different answer types
    if question_type == 'multiple_answer':
        # For multiple answer, selected_answer should be a list
        if not isinstance(selected_answer, list):
            selected_answer = [selected_answer] if selected_answer else []
        if not isinstance(correct_answer, list):
            correct_answer = [correct_answer]
        
        # Check if sets match (order doesn't matter)
        is_correct = set(selected_answer) == set(correct_answer)
    elif isinstance(correct_answer, list):
        # For fill-in-the-blank with multiple acceptable answers
        is_correct = selected_answer in correct_answer
    else:
        # For single-answer multiple choice
        is_correct = selected_answer == correct_answer
    
    # Store answer
    if 'answers' not in session:
        session['answers'] = {}
    
    # Get correct answer text for display
    if question_type in ['multiple_choice', 'multiple_answer']:
        if question_type == 'multiple_answer':
            if isinstance(correct_answer, list):
                correct_text = ', '.join([current_q['options'][ans] for ans in correct_answer])
            else:
                correct_text = current_q['options'][correct_answer]
            
            if isinstance(selected_answer, list):
                selected_text = ', '.join([current_q['options'][ans] for ans in selected_answer]) if selected_answer else 'None selected'
            else:
                selected_text = current_q['options'][selected_answer] if selected_answer else 'None selected'
        else:
            correct_text = current_q['options'][correct_answer]
            selected_text = current_q['options'][selected_answer] if selected_answer else 'None selected'
    else:
        correct_text = correct_answer if isinstance(correct_answer, str) else ', '.join(correct_answer)
        selected_text = selected_answer
    
    # Get existing answer data if it exists
    existing_answer = session['answers'].get(str(actual_q_index), {})
    
    # Track if this was a retry attempt
    was_retried = existing_answer.get('was_retried', False) or is_retry
    
    # Store/update answer with retry information
    session['answers'][str(actual_q_index)] = {
        'selected': selected_text,
        'selected_key': selected_answer,
        'correct': correct_text,
        'correct_key': correct_answer,
        'is_correct': is_correct,
        'question': current_q['question'],
        'question_type': question_type,
        'was_retried': was_retried,
        'first_attempt_correct': existing_answer.get('first_attempt_correct', is_correct and not is_retry)
    }
    
    # Track score and missed questions
    if not is_retry:
        if is_correct:
            session['score'] = session.get('score', 0) + 1
        else:
            missed = session.get('missed_questions', [])
            if actual_q_index not in missed:
                missed.append(actual_q_index)
            session['missed_questions'] = missed
    else:
        # In retry mode, update missed questions list
        if is_correct:
            # Remove from missed questions if now correct
            missed = session.get('missed_questions', [])
            if actual_q_index in missed:
                missed.remove(actual_q_index)
            session['missed_questions'] = missed
    
    session.modified = True
    
    response_data = {
        'is_correct': is_correct,
        'correct_answer': correct_answer,
        'correct_answer_text': correct_text,
        'selected_answer_text': selected_text,
    }
    
    return jsonify(response_data)

@app.route('/next_question', methods=['POST'])
def next_question():
    """Move to next question"""
    session['current_question'] = session.get('current_question', 0) + 1
    session.modified = True
    return jsonify({'success': True})

@app.route('/results')
def results():
    """Show final results"""
    selected_quiz = session.get('selected_quiz')
    if not selected_quiz:
        return redirect(url_for('selector'))
    quiz_data = load_quiz_data(selected_quiz)
    
    # Get shuffled quiz from session
    shuffled_quiz = session.get('shuffled_quiz', shuffle_quiz_data(quiz_data))
    
    score = session.get('score', 0)
    total = len(shuffled_quiz['questions'])
    percentage = round((score / total) * 100, 1) if total > 0 else 0
    
    # Calculate time taken
    start_time = session.get('start_time')
    time_taken = None
    if start_time:
        try:
            start = datetime.fromisoformat(start_time)
            time_taken = datetime.now() - start
        except:
            pass
    
    # Convert string keys back to integers for template compatibility
    answers = session.get('answers', {})
    converted_answers = {}
    for key, value in answers.items():
        converted_answers[int(key) if str(key).isdigit() else key] = value
    
    return render_template('results.html',
                         quiz_data=shuffled_quiz,
                         score=score,
                         total=total,
                         percentage=percentage,
                         answers=converted_answers,
                         time_taken=time_taken,
                         retry_round=session.get('retry_round', 0))

@app.route('/restart')
def restart():
    """Restart the quiz"""
    # Save the selected quiz before clearing
    selected_quiz = session.get('selected_quiz')
    
    # Clear session
    session.clear()
    
    # Restore the selected quiz and reinitialize
    if selected_quiz:
        session['selected_quiz'] = selected_quiz  # ← Fixed this line
        session['current_question'] = 0
        session['score'] = 0
        session['answers'] = {}
        session['missed_questions'] = []
        session['retry_mode'] = False
        session['retry_round'] = 0
        session['start_time'] = datetime.now().isoformat()
        
        # Shuffle and store quiz data
        quiz_data = load_quiz_data(selected_quiz)
        if quiz_data:
            shuffled_quiz = shuffle_quiz_data(quiz_data)
            session['shuffled_quiz'] = shuffled_quiz
    
    return redirect(url_for('quiz'))

@app.route('/api/quiz_data')
def api_quiz_data():
    """API endpoint to get quiz data"""
    shuffled_quiz = session.get('shuffled_quiz')
    if shuffled_quiz:
        return jsonify(shuffled_quiz)
    else:
        selected_quiz = session.get('selected_quiz', 'quiz_data')
        quiz_data = load_quiz_data(selected_quiz)
        if quiz_data:
            shuffled = shuffle_quiz_data(quiz_data)
            return jsonify(shuffled)
        else:
            return jsonify({'error': 'No quiz data found'}), 404

@app.route('/select_quiz/<quiz_name>', methods=['POST'])
def select_quiz(quiz_name):
    """Select a quiz to start"""
    quiz_data = load_quiz_data(quiz_name)
    if not quiz_data:
        return jsonify({'error': 'Quiz not found'}), 404
    
    # Clear session and set selected quiz
    session.clear()
    session['selected_quiz'] = quiz_name
    session['current_question'] = 0
    session['score'] = 0
    session['answers'] = {}
    session['missed_questions'] = []
    session['retry_mode'] = False
    session['retry_round'] = 0
    session['start_time'] = datetime.now().isoformat()
    
    # Shuffle and store quiz data
    shuffled_quiz = shuffle_quiz_data(quiz_data)
    session['shuffled_quiz'] = shuffled_quiz
    
    return jsonify({'success': True})

def get_port():
    """Determine port based on system - 5001 for Mac, 5000 otherwise"""
    return 5001 if platform.system() == "Darwin" else 5000

if __name__ == '__main__':
    # Check if any quiz data exists
    available_quizzes = get_available_quizzes()
    if not available_quizzes:
        print("\n" + "="*60)
        print("ERROR: No quizzes found!")
        print("="*60)
        print("Please create at least one quiz_data*.json file.")
        print("Examples: quiz_data.json, quiz_data1.json, quiz_data2.json")
        print("="*60 + "\n")
        exit(1)
    
    # Determine port based on system
    port = get_port()
    
    print("\n" + "="*60)
    print("QUIZ SERVER STARTING")
    print("="*60)
    print(f"Available quizzes: {len(available_quizzes)}")
    for quiz in available_quizzes:
        print(f"  - {quiz['title']} ({quiz['filename']})")
    print("="*60)
    
    # Get local IP
    local_ip = get_local_ip()
    network_url = f"http://{local_ip}:{port}"
    
    # Generate and display QR code
    print("\n" + "="*60)
    print("📱 SCAN THIS QR CODE TO ACCESS ON YOUR PHONE:")
    print("="*60)
    
    print_qr_code_terminal(network_url)
    
    print("="*60)
    print(f"Network URL: {network_url}")
    print("="*60 + "\n")
    
    print("="*60)
    print(f"Quiz available at:")
    print(f"  Local:    http://localhost:{port}")
    print(f"  Network:  {network_url}")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from models import db, User, Subject, Chapter, Quiz, Question, Score
import os
from sqlalchemy import or_

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///models/quiz_master.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db.init_app(app)

# Create the models directory if it doesn't exist
if not os.path.exists('models'):
    os.makedirs('models')

with app.app_context():
    # Create all database tables
    db.create_all()
    
    # Create admin user if it doesn't exist
    admin = User.query.filter_by(email='admin@example.com').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            password=generate_password_hash('admin123'),
            full_name='Administrator',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")

def set_password(user, password):
    user.password = generate_password_hash(password)

def check_password(user, password):
    return check_password_hash(user.password, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password(user, password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
        
        flash('Invalid email or password', 'login')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        qualification = request.form.get('qualification')
        dob_str = request.form.get('dob')
        
        # Basic validation
        if not all([username, email, password, confirm_password, full_name]):
            flash('All required fields must be filled', 'register')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'register')
            return redirect(url_for('register'))
            
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'register')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'register')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            qualification=qualification,
            is_admin=False,
            password=generate_password_hash(password)
        )
        
        # Handle date of birth if provided
        if dob_str:
            try:
                user.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format for date of birth', 'register')
                return redirect(url_for('register'))
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'register')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'logout')
    return redirect(url_for('login'))

# Admin routes
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    subjects = Subject.query.all()
    quizzes = Quiz.query.all()
    return render_template('admin/admindash.html', subjects=subjects, quizzes=quizzes)

@app.route('/admin/subject/add', methods=['GET', 'POST'])
@login_required
def add_subject():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        subject = Subject(name=name, description=description)
        db.session.add(subject)
        db.session.commit()
        
        flash('Subject added successfully')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/add_subject.html')

@app.route('/admin/subject/<int:subject_id>/management')
@login_required
def subject_management(subject_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    subject = Subject.query.get_or_404(subject_id)
    return render_template('admin/subject_management.html', subject=subject)

@app.route('/admin/chapter/add', methods=['GET', 'POST'])
@login_required
def add_chapter():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        name = request.form.get('name')
        description = request.form.get('description')
        
        chapter = Chapter(subject_id=subject_id, name=name, description=description)
        db.session.add(chapter)
        db.session.commit()
        
        flash('Chapter added successfully')
        return redirect(url_for('admin_dashboard'))
    
    subjects = Subject.query.all()
    subject_id = request.args.get('subject_id')
    selected_subject = None
    
    if subject_id:
        selected_subject = Subject.query.get_or_404(subject_id)
    
    return render_template('admin/add_chapter.html', 
                         subjects=subjects,
                         selected_subject=selected_subject)

@app.route('/admin/quiz/add', methods=['GET', 'POST'])
@login_required
def add_quiz():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        try:
            # Validate date format
            date_str = request.form.get('date')
            if not date_str:
                flash('Date is required.', 'error')
                return redirect(url_for('add_quiz'))
            
            try:
                # Parse the date string
                date_of_quiz = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                # Validate the date is not in the past
                if date_of_quiz < datetime.now().date():
                    flash('Quiz date cannot be in the past.', 'error')
                    return redirect(url_for('add_quiz'))
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD format.', 'error')
                return redirect(url_for('add_quiz'))
            
            # Validate duration format
            duration = request.form.get('duration')
            if not duration:
                flash('Duration is required.', 'error')
                return redirect(url_for('add_quiz'))
            
            try:
                # Parse the duration string
                minutes, seconds = map(int, duration.split(':'))
                
                # Validate the duration values
                if not (0 <= minutes <= 59 and 0 <= seconds <= 59):
                    flash('Invalid duration values. Minutes and seconds must be between 0 and 59.', 'error')
                    return redirect(url_for('add_quiz'))
                
                # Format duration as MM:SS
                duration = f"{minutes:02d}:{seconds:02d}"
            except (ValueError, TypeError):
                flash('Invalid duration format. Please use MM:SS format (e.g., 30:00).', 'error')
                return redirect(url_for('add_quiz'))
            
            chapter_id = request.form.get('chapter_id')
            if not chapter_id:
                flash('Chapter is required.', 'error')
                return redirect(url_for('add_quiz'))
            
            # Create the quiz
            quiz = Quiz(
                chapter_id=chapter_id,
                date_of_quiz=date_of_quiz,
                time_duration=duration,
                remarks=request.form.get('remarks')
            )
            
            db.session.add(quiz)
            db.session.commit()
            
            flash('Quiz added successfully!', 'success')
            return redirect(url_for('edit_quiz', quiz_id=quiz.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding quiz: {str(e)}', 'error')
            return redirect(url_for('add_quiz'))
    
    # Get all chapters with their subjects
    chapters = Chapter.query.join(Subject).order_by(Subject.name, Chapter.name).all()
    
    # Get specific chapter if provided
    chapter_id = request.args.get('chapter_id')
    selected_chapter = None
    if chapter_id:
        selected_chapter = Chapter.query.get_or_404(chapter_id)
    
    return render_template('admin/add_quiz.html', 
                         chapters=chapters,
                         selected_chapter=selected_chapter)

@app.route('/admin/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_quiz(quiz_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        quiz.date_of_quiz = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        quiz.time_duration = request.form.get('duration')
        quiz.remarks = request.form.get('remarks')
        
        db.session.commit()
        flash('Quiz updated successfully')
        return redirect(url_for('chapter_management', chapter_id=quiz.chapter_id))
    
    return render_template('admin/edit_quiz.html', quiz=quiz)

@app.route('/admin/question/add/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def add_question(quiz_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        question = Question(
            quiz_id=quiz_id,
            question_statement=request.form.get('question_statement'),
            option1=request.form.get('option1'),
            option2=request.form.get('option2'),
            option3=request.form.get('option3'),
            option4=request.form.get('option4'),
            correct_option=int(request.form.get('correct_option'))
        )
        db.session.add(question)
        db.session.commit()
        
        flash('Question added successfully')
        return redirect(url_for('edit_quiz', quiz_id=quiz_id))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('admin/add_question.html', quiz=quiz)

@app.route('/admin/users')
@login_required
def user_management():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    # Get all non-admin users
    users = User.query.filter_by(is_admin=False).all()
    return render_template('admin/user_management.html', users=users)

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting admin users
    if user.is_admin:
        flash('Cannot delete admin users')
        return redirect(url_for('user_management'))
    
    # Delete user's scores first (due to foreign key constraint)
    Score.query.filter_by(user_id=user_id).delete()
    
    # Delete the user
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully')
    return redirect(url_for('user_management'))

# User routes
@app.route('/user/dashboard')
@login_required
def user_dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    # Get completed quiz IDs for the current user
    completed_quiz_ids = [score.quiz_id for score in Score.query.filter_by(user_id=current_user.id).all()]
    
    # Get current date for comparison
    today = datetime.now().date()
    
    # Get upcoming quizzes (today and future) that haven't been completed
    upcoming_quizzes = Quiz.query.join(Chapter).join(Subject)\
        .filter(Quiz.date_of_quiz >= today)\
        .filter(~Quiz.id.in_(completed_quiz_ids))\
        .order_by(Quiz.date_of_quiz).all()
    
    # Get past quizzes (including completed quizzes)
    past_quizzes = Quiz.query.join(Chapter).join(Subject)\
        .filter(or_(Quiz.date_of_quiz < today, Quiz.id.in_(completed_quiz_ids)))\
        .order_by(Quiz.date_of_quiz.desc()).all()
    
    # Get completed quizzes
    completed_quizzes = Quiz.query.join(Score).filter(Score.user_id == current_user.id).all()
    
    # Calculate average score and best score
    scores = Score.query.filter_by(user_id=current_user.id).all()
    avg_score = sum(score.total_scored for score in scores) / len(scores) if scores else 0
    best_score = max(score.total_scored for score in scores) if scores else 0
    
    return render_template('user/userdash.html',
                         upcoming_quizzes=upcoming_quizzes,
                         past_quizzes=past_quizzes,
                         completed_quizzes=completed_quizzes,
                         completed_quiz_ids=completed_quiz_ids,
                         avg_score=avg_score,
                         best_score=best_score)

@app.route('/quiz/<int:quiz_id>/save', methods=['POST'])
@login_required
def save_answer(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if user has already completed this quiz
    if Score.query.filter_by(quiz_id=quiz_id, user_id=current_user.id).first():
        flash('You have already completed this quiz!', 'warning')
        return redirect(url_for('user_dashboard'))
    
    # Get the answer from the form
    question_id = request.form.get('question_id')
    answer = request.form.get('answer')
    
    if not question_id or not answer:
        return jsonify({'status': 'error', 'message': 'Missing data'})
    
    # Save or update the answer in the session
    if 'saved_answers' not in session:
        session['saved_answers'] = {}
    
    session['saved_answers'][question_id] = answer
    session.modified = True
    
    return jsonify({'status': 'success', 'message': 'Answer saved'})

@app.route('/quiz/<int:quiz_id>', methods=['GET'])
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if user has already completed this quiz
    if Score.query.filter_by(quiz_id=quiz_id, user_id=current_user.id).first():
        flash('You have already completed this quiz!', 'warning')
        return redirect(url_for('user_dashboard'))
    
    # Get saved answers from session
    saved_answers = session.get('saved_answers', {})
    
    return render_template('quiz.html', quiz=quiz, saved_answers=saved_answers)

@app.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if user has already completed this quiz
    if Score.query.filter_by(quiz_id=quiz_id, user_id=current_user.id).first():
        flash('You have already completed this quiz!', 'warning')
        return redirect(url_for('user_dashboard'))
    
    total_questions = len(quiz.questions)
    correct_answers = 0
    
    # Calculate score
    for question in quiz.questions:
        user_answer = request.form.get(f'answer{question.id}')
        if user_answer == question.correct_answer:
            correct_answers += 1
    
    # Calculate percentage
    score_percentage = (correct_answers / total_questions) * 100
    
    # Save score to database
    quiz_score = Score(
        quiz_id=quiz_id,
        user_id=current_user.id,
        total_scored=score_percentage,
        time_stamp=datetime.now()
    )
    db.session.add(quiz_score)
    db.session.commit()
    
    # Clear saved answers from session
    if 'saved_answers' in session:
        del session['saved_answers']
    
    flash(f'Quiz submitted successfully! Your score: {score_percentage:.1f}%', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/admin/summary')
@login_required
def admin_summary():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    # Get basic statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_subjects = Subject.query.count()
    total_chapters = Chapter.query.count()
    total_quizzes = Quiz.query.count()
    total_questions = Question.query.count()
    upcoming_quizzes = Quiz.query.filter(Quiz.date_of_quiz >= datetime.now().date()).count()
    
    # Calculate average questions per quiz
    avg_questions_per_quiz = round(total_questions / total_quizzes if total_quizzes > 0 else 0, 1)
    
    # Get subject names and scores for charts
    subjects = Subject.query.all()
    subject_names = []
    subject_scores = []
    total_quizzes_by_subject = []
    completed_quizzes_by_subject = []
    
    for subject in subjects:
        subject_names.append(subject.name)
        
        # Get top score for each subject
        top_score = 0
        total_quizzes = 0
        completed_quizzes = 0
        
        for chapter in subject.chapters:
            for quiz in chapter.quizzes:
                total_quizzes += 1
                scores = [score.total_scored for score in quiz.scores]
                if scores:
                    completed_quizzes += 1
                    top_score = max(top_score, max(scores))
        
        subject_scores.append(top_score)
        total_quizzes_by_subject.append(total_quizzes)
        completed_quizzes_by_subject.append(completed_quizzes)
    
    # Get recent activity
    recent_activity = Score.query.order_by(Score.time_stamp.desc()).limit(10).all()
    
    return render_template('admin/admin_summary.html',
                         total_users=total_users,
                         active_users=active_users,
                         total_subjects=total_subjects,
                         total_chapters=total_chapters,
                         total_quizzes=total_quizzes,
                         total_questions=total_questions,
                         upcoming_quizzes=upcoming_quizzes,
                         avg_questions_per_quiz=avg_questions_per_quiz,
                         subject_names=subject_names,
                         subject_scores=subject_scores,
                         total_quizzes_by_subject=total_quizzes_by_subject,
                         completed_quizzes_by_subject=completed_quizzes_by_subject,
                         recent_activity=recent_activity)

@app.route('/scores')
@login_required
def scores():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.time_stamp.desc()).all()
    avg_score = sum(score.total_scored for score in scores) / len(scores) if scores else 0
    best_score = max(score.total_scored for score in scores) if scores else 0
    
    return render_template('user/scores.html', scores=scores, avg_score=avg_score, best_score=best_score)

@app.route('/quiz/<int:quiz_id>/view')
@login_required
def view_test(quiz_id):
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    score = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first()
    
    return render_template('user/viewtest.html', quiz=quiz, questions=questions, score=score, now=datetime.now().date())

@app.route('/user/summary')
@login_required
def user_summary():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    # Get all quizzes
    all_quizzes = Quiz.query.all()
    total_quizzes = len(all_quizzes)
    completed_quizzes = len([q for q in all_quizzes if any(s.user_id == current_user.id for s in q.scores)])
    upcoming_quizzes = len([q for q in all_quizzes if q.date_of_quiz > datetime.now().date()])
    past_quizzes = total_quizzes - upcoming_quizzes
    
    # Get scores
    scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.time_stamp.desc()).all()
    avg_score = sum(score.total_scored for score in scores) / len(scores) if scores else 0
    best_score = max(score.total_scored for score in scores) if scores else 0
    
    # Get subjects and chapters
    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    
    # Get user's quiz history
    recent_activity = Score.query.filter_by(user_id=current_user.id).order_by(Score.time_stamp.desc()).limit(10).all()
    
    # Format dates for the activities
    for activity in recent_activity:
        activity.formatted_date = activity.time_stamp.strftime('%Y-%m-%d')
    
    # Get subject performance data
    subject_performance = []
    subject_names = []
    
    for subject in subjects:
        subject_scores = []
        for chapter in subject.chapters:
            for quiz in chapter.quizzes:
                score = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz.id).first()
                if score:
                    subject_scores.append(score.total_scored)
        
        if subject_scores:
            avg_subject_score = sum(subject_scores) / len(subject_scores)
            best_subject_score = max(subject_scores)
            total_subject_quizzes = sum(len(chapter.quizzes) for chapter in subject.chapters)
            quizzes_taken = len(subject_scores)
            completion_rate = (quizzes_taken / total_subject_quizzes) * 100 if total_subject_quizzes > 0 else 0
        else:
            avg_subject_score = best_subject_score = 0
            total_subject_quizzes = sum(len(chapter.quizzes) for chapter in subject.chapters)
            quizzes_taken = 0
            completion_rate = 0
        
        subject_performance.append({
            'name': subject.name,
            'quizzes_taken': quizzes_taken,
            'total_quizzes': total_subject_quizzes,
            'avg_score': avg_subject_score,
            'best_score': best_subject_score,
            'completion_rate': completion_rate
        })
        
        subject_names.append(subject.name)
    
    return render_template('user/user_summary.html',
                         total_quizzes=total_quizzes,
                         completed_quizzes=completed_quizzes,
                         upcoming_quizzes=upcoming_quizzes,
                         past_quizzes=past_quizzes,
                         avg_score=avg_score,
                         best_score=best_score,
                         subjects=subjects,
                         chapters=chapters,
                         recent_activity=recent_activity,
                         subject_performance=subject_performance,
                         subject_names=subject_names)

@app.route('/admin/question/<int:question_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    question = Question.query.get_or_404(question_id)
    
    if request.method == 'POST':
        question.question_statement = request.form.get('question_statement')
        question.option1 = request.form.get('option1')
        question.option2 = request.form.get('option2')
        question.option3 = request.form.get('option3')
        question.option4 = request.form.get('option4')
        question.correct_option = int(request.form.get('correct_option'))
        
        db.session.commit()
        flash('Question updated successfully')
        return redirect(url_for('edit_quiz', quiz_id=question.quiz_id))
    
    return render_template('admin/edit_question.html', question=question)

@app.route('/admin/question/<int:question_id>/delete', methods=['POST'])
@login_required
def delete_question(question_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    
    try:
        db.session.delete(question)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
        flash('Question deleted successfully')
        return redirect(url_for('edit_quiz', quiz_id=quiz_id))
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)})
        flash('Error deleting question')
        return redirect(url_for('edit_quiz', quiz_id=quiz_id))

@app.route('/admin/quiz/<int:quiz_id>/delete', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    chapter_id = quiz.chapter_id
    
    # Delete all questions first
    Question.query.filter_by(quiz_id=quiz_id).delete()
    
    # Delete all scores
    Score.query.filter_by(quiz_id=quiz_id).delete()
    
    # Delete the quiz
    db.session.delete(quiz)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    flash('Quiz deleted successfully')
    return redirect(url_for('subject_management', subject_id=chapter_id))

@app.route('/admin/chapter/<int:chapter_id>/delete', methods=['POST'])
@login_required
def delete_chapter(chapter_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    chapter = Chapter.query.get_or_404(chapter_id)
    try:
        db.session.delete(chapter)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/subject/<int:subject_id>/delete', methods=['POST'])
@login_required
def delete_subject(subject_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    subject = Subject.query.get_or_404(subject_id)
    try:
        db.session.delete(subject)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/chapter/<int:chapter_id>/management')
@login_required
def chapter_management(chapter_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    return render_template('admin/chapter_management.html', chapter=chapter)

@app.route('/admin/chapter/<int:chapter_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_chapter(chapter_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'POST':
        try:
            chapter.name = request.form.get('name')
            chapter.description = request.form.get('description')
            
            db.session.commit()
            flash('Chapter updated successfully!', 'success')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True})
            return redirect(url_for('chapter_management', chapter_id=chapter.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating chapter: {str(e)}', 'error')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': str(e)})
            return redirect(url_for('edit_chapter', chapter_id=chapter.id))
    
    return render_template('admin/edit_chapter.html', chapter=chapter)

if __name__ == '__main__':
    app.run(debug=True) 
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(120))
    qualification = db.Column(db.String(120))
    dob = db.Column(db.Date)
    is_admin = db.Column(db.Boolean, default=False)
    scores = db.relationship('Score', backref='user', lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade='all, delete-orphan')

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade='all, delete-orphan')

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.String(5), nullable=False)  # Format: MM:SS
    remarks = db.Column(db.Text)
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    scores = db.relationship('Score', backref='quiz', lazy=True, cascade='all, delete-orphan')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)  # This is what's in the database
    option1 = db.Column(db.String(500), nullable=False)
    option2 = db.Column(db.String(500), nullable=False)
    option3 = db.Column(db.String(500), nullable=False)
    option4 = db.Column(db.String(500), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)  # 1, 2, 3, or 4

    @property
    def options(self):
        return [self.option1, self.option2, self.option3, self.option4]

    @property
    def correct_answer(self):
        return self.options[self.correct_option - 1]

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    total_scored = db.Column(db.Float, nullable=False)
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

__all__ = ['db', 'User', 'Subject', 'Chapter', 'Quiz', 'Question', 'Score'] 
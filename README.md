# Quiz Master

A comprehensive quiz management system built with Flask, designed for exam preparation across multiple courses. The application features a minimalist grey-themed UI and robust functionality for both administrators and users.

## Features

### Admin Features
- Complete subject and chapter management
- Quiz creation with multiple-choice questions
- User management and oversight
- Performance analytics and statistics
- Subject-wise quiz distribution tracking
- Recent activity monitoring

### User Features
- Personalized dashboard with upcoming and past quizzes
- Interactive quiz taking interface with timer
- Comprehensive performance summary
- Subject-wise progress tracking
- Score history and analytics
- Mobile-responsive interface

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Modern web browser (Chrome, Firefox, Safari, or Edge)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/23f3001361/quiz-master.git
cd quiz-master
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Access the application:
```
http://localhost:5000
```

## Default Admin Account

The application creates a default admin account on first run:
- Email: admin@example.com
- Password: admin123

**Important:** Change these credentials immediately after first login.

## Project Structure

```
quiz_master/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── models/
│   ├── __init__.py       # Database models and configuration
│   └── quiz_master.db    # SQLite database
├── static/
│   ├── style.css         # Custom styles
│   └── images/           # Static images
├── templates/
│   ├── index.html        # Landing page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── admin/
│   │   ├── admindash.html       # Admin dashboard
│   │   ├── admin_summary.html   # Admin analytics
│   │   ├── add_subject.html     # Subject management
│   │   ├── add_chapter.html     # Chapter management
│   │   └── user_management.html # User management
│   └── user/
│       ├── userdash.html        # User dashboard
│       ├── user_summary.html    # Performance summary
│       ├── quiz.html           # Quiz taking interface
│       └── viewtest.html       # Quiz review interface
└── view_db.py            # Database utility script
```

## Security Features

The application implements several security measures:
- Password hashing using Werkzeug's security functions
- User session management with Flask-Login
- Form validation and sanitization
- SQL injection prevention through SQLAlchemy
- Protected routes with login_required decorator
- Role-based access control (Admin/User)

## Key Functionalities

### Admin Panel
1. Subject Management
   - Create and manage subjects
   - Add and organize chapters
   - Track subject performance

2. Quiz Management
   - Create timed quizzes
   - Add multiple-choice questions
   - Set quiz duration and date

3. User Management
   - View all registered users
   - Monitor user performance
   - Track quiz completion rates

### User Interface
1. Quiz Taking
   - Timer-based quiz interface
   - Automatic submission
   - Immediate score display

2. Performance Tracking
   - Subject-wise progress
   - Score history
   - Performance analytics

## Database Schema

The application uses SQLAlchemy with the following models:
- User: User account information
- Subject: Course subjects
- Chapter: Subject chapters
- Quiz: Chapter quizzes
- Question: Quiz questions
- Score: User quiz scores

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License. 
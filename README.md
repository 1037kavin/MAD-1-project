# Quiz Master

A comprehensive web-based quiz management system built with Flask, designed for educational institutions to manage and conduct online quizzes.

## Features

### Admin Features
- User Management
  - View and manage user accounts
  - Delete user accounts
- Subject Management
  - Create, edit, and delete subjects
  - Manage chapters within subjects
- Quiz Management
  - Create and schedule quizzes
  - Add, edit, and delete questions
  - Set quiz duration and date
- Analytics Dashboard
  - View overall statistics
  - Track user performance
  - Monitor quiz completion rates

### User Features
- User Dashboard
  - View upcoming and past quizzes
  - Track personal performance
  - See average and best scores
- Quiz Taking
  - Take scheduled quizzes
  - Save answers during quiz
  - View results immediately
- Performance Analytics
  - View subject-wise performance
  - Track progress over time
  - Access detailed score history

## Prerequisites

- Python 3.x
- pip (Python package installer)
- SQLite3

## Installation

1. Clone the repository:
```bash
git clone https://github.com/23f3001361/MAD-1-project.git
cd MAD-1-project
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python app.py
```

## Default Admin Account

The system creates a default admin account on first run:
- Email: admin@example.com
- Password: admin123

**Important:** Change these credentials immediately in production.

## Project Structure

```
Quiz_Master/
├── app.py              # Main application file
├── models/
│   ├── __init__.py    # Database models
│   └── quiz_master.db # SQLite database
├── static/
│   ├── css/           # Stylesheets
└── templates/
    ├── admin/         # Admin interface templates
    └── user/          # User interface templates
```

## Security Notes

For production deployment:
1. Change the secret key in `app.py`
2. Enable CSRF protection
3. Use HTTPS
4. Implement password reset functionality
5. Add rate limiting for login attempts
6. Configure proper session handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask framework and its extensions
- SQLAlchemy ORM
- Bootstrap for UI components 

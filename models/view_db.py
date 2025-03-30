from app import app, db, User, Subject, Chapter, Quiz, Question, Score

def view_users():
    with app.app_context():
        users = User.query.all()
        print("\nUsers in database:")
        print("=" * 50)
        for user in users:
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Full Name: {user.full_name}")
            print(f"Password: {user.password}")
            print(f"Is Admin: {user.is_admin}")
            print("-" * 50)

if __name__ == "__main__":
    view_users() 
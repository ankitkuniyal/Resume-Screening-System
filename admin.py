from app import db, User, app  # Import the app instance
from werkzeug.security import generate_password_hash

# Ensure the app context is active
with app.app_context():
    # Check if the admin user already exists
    existing_admin = User.query.filter_by(username="admin").first()
    
    if not existing_admin:
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password=generate_password_hash("adminpassword"),  # ✅ Hash the password
            role="admin"
        )

        db.session.add(admin_user)
        db.session.commit()
        print("Admin user added successfully!")
    else:
        print("Admin user already exists.")


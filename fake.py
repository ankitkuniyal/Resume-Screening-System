from app import db, User, Applicant, Employer, app  # Import the app instance and models
from werkzeug.security import generate_password_hash
from faker import Faker
import random

# Initialize Faker
fake = Faker()

# Ensure the app context is active
with app.app_context():
    # Create 250 fake users
    for _ in range(250):
        # Generate fake user data
        username = fake.user_name()
        email = fake.email()
        phone = fake.phone_number()
        password = "password123"  # Use a common password for simplicity
        hashed_password = generate_password_hash(password)  # Hash the password
        role = random.choice(['applicant', 'employer'])  # Randomly assign role

        # Create a new user
        new_user = User(
            username=username,
            email=email,
            phone=phone,
            password=hashed_password,
            role=role
        )

        # Add the user to the session
        db.session.add(new_user)

        # Print the username and password for visibility
        print(f"Username: {username}, Password: {password}")

        # Commit the session every 50 users to avoid memory issues
        if _ % 50 == 0:
            db.session.commit()

    # Commit any remaining users
    db.session.commit()

    print("250 fake users added successfully!")

    # Optionally, create associated Applicant or Employer entries
    for user in User.query.all():
        if user.role == 'applicant':
            new_applicant = Applicant(
                user_id=user.id,
                dob=fake.date_of_birth(minimum_age=18, maximum_age=40),  # Random DOB for applicants
                gender=random.choice(['male', 'female', 'other']),
                address=fake.address(),
                highest_qualification=random.choice(['High School', 'Diploma', "Bachelor's", "Master's", "PhD"]),
                field_of_study=fake.word(),
                experience_years=random.randint(0, 10)  # Random experience years
            )
            db.session.add(new_applicant)

        elif user.role == 'employer':
            new_employer = Employer(
                user_id=user.id,
                industry=fake.word(),
                website=fake.url(),
                address=fake.address(),
                contact=phone,  # Use the same phone number for simplicity
                linkedin=fake.url()
            )
            db.session.add(new_employer)

    # Commit the session for applicants and employers
    db.session.commit()

    print("Associated Applicant and Employer entries added successfully!")
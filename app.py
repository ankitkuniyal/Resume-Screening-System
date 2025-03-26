
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re  # Import regex for validation
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resume_screening.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    phone = db.Column(db.String(15), nullable=True)  # For applicants
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum('admin', 'applicant', 'employer', name='user_roles'), nullable=False)

    employer = db.relationship('Employer', backref='user', uselist=False)
    applicant = db.relationship('Applicant', backref='user', uselist=False)

# Employer Model
class Employer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    industry = db.Column(db.String(50), nullable=False)
    website = db.Column(db.String(255), nullable=True)
    address = db.Column(db.String(255), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    linkedin = db.Column(db.String(255), nullable=True)
    company_logo = db.Column(db.String(255), nullable=True)  # Path to uploaded logo

    jobs = db.relationship('Job', backref='employer', lazy=True)

# Job Model
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    salary = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=False)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer.id'), nullable=False)

# Applicant Model
class Applicant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    highest_qualification = db.Column(db.String(50), nullable=False)
    field_of_study = db.Column(db.String(100), nullable=False)
    experience_years = db.Column(db.Integer, nullable=True, default=0)
    resume = db.Column(db.String(255), nullable=True)  # Path to uploaded resume
    
    skills = db.relationship('ApplicantSkill', backref='applicant', lazy=True)

class AppliedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicant.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # New status field

    applicant = db.relationship('Applicant', backref='applied_jobs')
    job = db.relationship('Job', backref='applicants')
# Skills Model
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(50), unique=True, nullable=False)

# Applicant Skills Model
class ApplicantSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicant.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)

@app.route('/')
def home():
    return render_template('homepage.html')
@app.route('/delete_database', methods=['POST'])
def delete_database():
        if 'user_id' in session and session['role'] == 'admin':
            try:
                db.drop_all()
                db.create_all()
                flash('Database has been reset successfully!', 'success')
            except Exception as e:
                flash(f'An error occurred while resetting the database: {str(e)}', 'danger')
        else:
            flash('Unauthorized access!', 'danger')
        return redirect(url_for('admin_dashboard'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Fetch user by username or email if it's an admin
        user = User.query.filter((User.username == username) | ((User.email == username))).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role

            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'applicant':
                return redirect(url_for('applicant_dashboard'))
            elif user.role == 'employer':
                return redirect(url_for('employer_dashboard'))
        else:
            flash('Invalid credentials!', 'danger')

    return render_template('login.html')


@app.route('/applicant/dashboard')
def applicant_dashboard():
    if 'user_id' not in session:
        flash('You need to log in first!', 'danger')
        return redirect(url_for('login'))

    # Fetch the applicant's information
    user = User.query.get(session['user_id'])
    applicant = Applicant.query.filter_by(user_id=user.id).first()

    if not applicant:
        flash('Applicant profile not found!', 'danger')
        return redirect(url_for('some_other_route'))  # Redirect to an appropriate route

    # Fetch recent job postings
    job_postings = Job.query.all()  # You can add filters or limits as needed

    # Fetch applied jobs
    applied_jobs = AppliedJob.query.filter_by(applicant_id=applicant.id).all()

    return render_template('applicant_dashboard.html', 
                           applicant_name=user.username, 
                           job_postings=job_postings, 
                           applied_jobs=applied_jobs)

@app.route('/employer')
def employer_dashboard():
    if 'user_id' in session and session['role'] == 'employer':
        # Fetch the employer's information
        user = User.query.get(session['user_id'])
        employer = Employer.query.filter_by(user_id=user.id).first()

        if not employer:
            flash('Employer profile not found!', 'danger')
            return redirect(url_for('login'))

        # Fetch jobs posted by the employer
        jobs_posted = Job.query.filter_by(employer_id=employer.id).all()

        return render_template('employer_dashboard.html', 
                               employer_name=employer.user.username,  # Use the username instead of email
                               jobs_posted=jobs_posted)

    flash('Unauthorized access!', 'danger')
    return redirect(url_for('login'))

@app.route('/admin')
def admin_dashboard():
    if 'user_id' in session and session['role'] == 'admin':
        users = User.query.all()
        employers = Employer.query.all()
        jobs = Job.query.all()
        applicants = Applicant.query.all()
        return render_template('admin.html', users=users, employers=employers, jobs=jobs, applicants=applicants)

    flash('Unauthorized access!', 'danger')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/register/applicant', methods=['GET', 'POST'])
def register_applicant():
    if request.method == 'POST':
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        dob = request.form['dob']
        gender = request.form['gender']
        address = request.form['address']
        highest_qualification = request.form['highest_qualification']
        field_of_study = request.form['field_of_study']
        experience_years = request.form.get('experience_years', 0)

        # Email validation using regex
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, email):
            flash('Invalid email format! Please enter a valid email.', 'danger')
            return redirect(url_for('register_applicant'))

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered!', 'danger')
            return redirect(url_for('register_applicant'))

        # Password validation
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return redirect(url_for('register_applicant'))

        # Date of Birth validation
        max_dob = (datetime.utcnow() - timedelta(days=18*365)).date()  # Calculate max DOB (18 years ago)
        dob_date = datetime.strptime(dob, '%Y-%m-%d').date()  # Convert string to date

        if dob_date > max_dob:
            flash('You must be at least 18 years old to register.', 'danger')
            return redirect(url_for('register_applicant'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create new user
        new_user = User(username=email, email=email, phone=phone, password=hashed_password, role='applicant')
        db.session.add(new_user)
        db.session.commit()

        # Create new applicant
        new_applicant = Applicant(user_id=new_user.id, dob=dob_date, gender=gender, address=address,
                                  highest_qualification=highest_qualification, field_of_study=field_of_study,
                                  experience_years=experience_years)
        db.session.add(new_applicant)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('applicant_register.html')
@app.route('/apply/<int:job_id>', methods=['POST'])
def apply_for_job(job_id):
    if 'user_id' not in session or session['role'] != 'applicant':
        flash('You need to log in as an applicant to apply for jobs!', 'danger')
        return redirect(url_for('login'))

    # Fetch the applicant's information
    applicant = Applicant.query.filter_by(user_id=session['user_id']).first()
    if not applicant:
        flash('Applicant profile not found!', 'danger')
        return redirect(url_for('applicant_dashboard'))

    # Check if the job exists
    job = Job.query.get(job_id)
    if not job:
        flash('Job not found!', 'danger')
        return redirect(url_for('applicant_dashboard'))

    # Check if the applicant has already applied for this job
    existing_application = AppliedJob.query.filter_by(applicant_id=applicant.id, job_id=job.id).first()
    if existing_application:
        flash('You have already applied for this job!', 'warning')
        return redirect(url_for('applicant_dashboard'))

    # Create a new application with default status 'pending'
    new_application = AppliedJob(applicant_id=applicant.id, job_id=job.id)
    db.session.add(new_application)
    db.session.commit()

    flash('Application submitted successfully!', 'success')
    return redirect(url_for('applicant_dashboard'))

# Update the applicant_dashboard.html template to include job application buttons

@app.route('/register/employer', methods=['GET', 'POST'])
def register_employer():
    if request.method == 'POST':
        
            # Get form data
            email = request.form['email']
            industry = request.form['industry']
            address = request.form['address']
            contact = request.form['contact']
            linkedin = request.form['linkedin']
            password = generate_password_hash(request.form['login_password'])  # Use the correct field name

            # Check if the email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already registered. Please use a different email.', 'danger')
                return redirect(url_for('register_employer'))

            # Create new user
            new_user = User(username=email, email=email, password=password, role='employer')
            db.session.add(new_user)
            db.session.commit()

            # Create new employer
            new_employer = Employer(user_id=new_user.id, industry=industry, address=address, contact=contact, linkedin=linkedin)
            db.session.add(new_employer)
            db.session.commit()

            flash('Employer registration successful!', 'success')
            return redirect(url_for('login'))

    return render_template('employer_register.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=3200)

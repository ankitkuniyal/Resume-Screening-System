from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0Password%40SQL@localhost/resume_screening'
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            
            if user.role == 'applicant':
                return redirect(url_for('applicant_dashboard'))
            elif user.role == 'employer':
                return redirect(url_for('employer_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    
    return render_template('login.html')

@app.route('/applicant')
def applicant_dashboard():
    if 'user_id' in session and session['role'] == 'applicant':
        return render_template('applicant_dashboard.html')
    flash('Unauthorized access!', 'danger')
    return redirect(url_for('login'))

@app.route('/employer')
def employer_dashboard():
    if 'user_id' in session and session['role'] == 'employer':
        return render_template('employer_dashboard.html')
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

# Applicant Registration
@app.route('/register/applicant', methods=['GET', 'POST'])
def register_applicant():
    if request.method == 'POST':
        email = request.form['email']
        phone = request.form['phone']
        password = generate_password_hash(request.form['password'])
        dob = request.form['dob']
        gender = request.form['gender']
        address = request.form['address']
        highest_qualification = request.form['highest_qualification']
        field_of_study = request.form['field_of_study']
        experience_years = request.form.get('experience_years', 0)

        new_user = User(username=email, email=email, phone=phone, password=password, role='applicant')
        db.session.add(new_user)
        db.session.commit()

        new_applicant = Applicant(user_id=new_user.id, dob=dob, gender=gender, address=address,
                                  highest_qualification=highest_qualification, field_of_study=field_of_study,
                                  experience_years=experience_years)
        db.session.add(new_applicant)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('applicant_register.html')

# Employer Registration
@app.route('/register/employer', methods=['GET', 'POST'])
def register_employer():
    if request.method == 'POST':
        email = request.form['email']
        industry = request.form['industry']
        address = request.form['address']
        contact = request.form['contact']
        linkedin = request.form['linkedin']
        password = generate_password_hash(request.form['password'])

        new_user = User(username=email, email=email, password=password, role='employer')
        db.session.add(new_user)
        db.session.commit()

        new_employer = Employer(user_id=new_user.id, industry=industry, address=address, contact=contact, linkedin=linkedin)
        db.session.add(new_employer)
        db.session.commit()

        flash('Employer registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register_employer.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=3000)

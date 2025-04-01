from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import re
import random

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resume_screening.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads/company_logos'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Initialize database
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    phone = db.Column(db.String(15), nullable=True)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'applicant', 'employer'

    employer = db.relationship('Employer', backref='user', uselist=False)
    applicant = db.relationship('Applicant', backref='user', uselist=False)

class Employer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    industry = db.Column(db.String(50), nullable=False)
    website = db.Column(db.String(255), nullable=True)
    address = db.Column(db.String(255), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    company_logo = db.Column(db.String(255), nullable=True)

    jobs = db.relationship('Job', backref='employer', lazy=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    salary = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=False)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer.id', ondelete='CASCADE'), nullable=False)
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    applicants = db.relationship('AppliedJob', backref='job', lazy=True, cascade='all, delete-orphan')
    required_skills= db.Column(db.JSON) 

class Applicant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    highest_qualification = db.Column(db.String(50), nullable=False)
    field_of_study = db.Column(db.String(100), nullable=False)
    experience_years = db.Column(db.Integer, nullable=True, default=0)
    resume = db.Column(db.String(255), nullable=True)

    skills = db.relationship('ApplicantSkill', backref='applicant', lazy=True)

class AppliedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicant.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id', ondelete='CASCADE'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(50), unique=True, nullable=False)

class ApplicantSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicant.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    skill = db.relationship('Skill')  # Add relationship for easier access

# Create directories
def create_dirs():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists('static/resumes'):
        os.makedirs('static/resumes')

# Initialize data
def initialize_data():
    # Create default admin
    if not User.query.filter_by(email='admin@resumescreening.com').first():
        admin_user = User(
            username='Admin',
            email='admin@resumescreening.com',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()

    # Create sample skills if none exist
    if not Skill.query.first():
        tech_skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'SQL',
            'HTML/CSS', 'React', 'Django', 'Flask', 'Git',
            'AWS', 'Docker', 'Machine Learning', 'Data Analysis'
        ]
        for skill_name in tech_skills:
            db.session.add(Skill(skill_name=skill_name))
        db.session.commit()

# Initialize database
with app.app_context():
    db.create_all()
    create_dirs()
    initialize_data()

# Home route
@app.route('/')
def home():
    return render_template('homepage.html')

# Auth routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            session['username'] = user.username

            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'applicant':
                return redirect(url_for('applicant_dashboard'))
            elif user.role == 'employer':
                return redirect(url_for('employer_dashboard'))
        else:
            flash('Invalid email or password!', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

# Registration routes
@app.route('/register/applicant', methods=['GET', 'POST'])
def register_applicant():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        dob = request.form['dob']
        gender = request.form['gender']
        address = request.form['address']
        highest_qualification = request.form['highest_qualification']
        field_of_study = request.form['field_of_study']
        experience_years = request.form.get('experience_years', 0)
        selected_skill_ids = request.form.getlist('skills')

        # Validation
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            flash('Invalid email!', 'danger')
            return redirect(url_for('register_applicant'))

        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('register_applicant'))

        if len(password) < 8:
            flash('Password too short!', 'danger')
            return redirect(url_for('register_applicant'))

        # Create user
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=name,
            email=email,
            phone=phone,
            password=hashed_password,
            role='applicant'
        )
        db.session.add(new_user)
        db.session.commit()

        # Create applicant
        new_applicant = Applicant(
            user_id=new_user.id,
            dob=datetime.strptime(dob, '%Y-%m-%d').date(),
            gender=gender,
            address=address,
            highest_qualification=highest_qualification,
            field_of_study=field_of_study,
            experience_years=experience_years
        )
        db.session.add(new_applicant)
        db.session.commit()

        # Add skills
        for skill_id in selected_skill_ids:
            skill = Skill.query.get(skill_id)
            if skill:
                applicant_skill = ApplicantSkill(
                    applicant_id=new_applicant.id,
                    skill_id=skill.id
                )
                db.session.add(applicant_skill)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    skills = Skill.query.all()
    return render_template('applicant_register.html', skills=skills)

@app.route('/register/employer', methods=['GET', 'POST'])
def register_employer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        industry = request.form['industry']
        address = request.form['address']
        contact = request.form['contact']
        password = request.form['login_password']

        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('register_employer'))

        # Create user
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=name,
            email=email,
            password=hashed_password,
            role='employer'
        )
        db.session.add(new_user)
        db.session.commit()

        # Create employer
        new_employer = Employer(
            user_id=new_user.id,
            industry=industry,
            address=address,
            contact=contact,
        )
        db.session.add(new_employer)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('employer_register.html')

# Dashboard routes
@app.route('/applicant/dashboard')
def applicant_dashboard():
    if 'user_id' not in session or session['role'] != 'applicant':
        flash('Unauthorized!', 'danger')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    applicant = Applicant.query.filter_by(user_id=user.id).first()

    if not applicant:
        flash('Profile not found!', 'danger')
        return redirect(url_for('login'))

    job_postings = Job.query.all()
    applied_jobs = AppliedJob.query.filter_by(applicant_id=applicant.id).all()

    return render_template('applicant_dashboard.html',
                         applicant_name=user.username,
                         job_postings=job_postings,
                         applied_jobs=applied_jobs)

@app.route('/employer/dashboard')
def employer_dashboard():
    if 'user_id' not in session or session['role'] != 'employer':
        flash('Unauthorized!', 'danger')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    employer = Employer.query.filter_by(user_id=user.id).first()

    if not employer:
        flash('Profile not found!', 'danger')
        return redirect(url_for('login'))

    jobs_posted = Job.query.filter_by(employer_id=employer.id).all()

    return render_template('employer_dashboard.html',
                         employer_name=user.username,
                         jobs_posted=jobs_posted)

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Unauthorized!', 'danger')
        return redirect(url_for('login'))

    users = User.query.all()
    employers = Employer.query.all()
    jobs = Job.query.all()
    applicants = Applicant.query.all()
    skills = Skill.query.all()
    applied_jobs = AppliedJob.query.all()
    applicant_skills = ApplicantSkill.query.all()

    return render_template('admin.html',
                         users=users,
                         employers=employers,
                         jobs=jobs,
                         applicants=applicants,
                         skills=skills,
                         applied_jobs=applied_jobs,
                         applicant_skills=applicant_skills)

# Job routes

@app.route('/apply/<int:job_id>', methods=['POST'])
def apply_for_job(job_id):
    if 'user_id' not in session or session['role'] != 'applicant':
        flash('Unauthorized!', 'danger')
        return redirect(url_for('login'))

    applicant = Applicant.query.filter_by(user_id=session['user_id']).first()
    job = Job.query.get(job_id)

    if not applicant or not job:
        flash('Invalid request!', 'danger')
        return redirect(url_for('applicant_dashboard'))

    if AppliedJob.query.filter_by(applicant_id=applicant.id, job_id=job.id).first():
        flash('Already applied!', 'warning')
        return redirect(url_for('applicant_dashboard'))

    new_application = AppliedJob(applicant_id=applicant.id, job_id=job.id)
    db.session.add(new_application)
    db.session.commit()

    flash('Application submitted!', 'success')
    return redirect(url_for('applicant_dashboard'))
@app.route('/employer/post-job', methods=['GET', 'POST'])
def post_job():
    # Authentication check
    if 'user_id' not in session or session['role'] != 'employer':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            # Get form data
            job_title = request.form['job_title']
            company = request.form['company']
            location = request.form['location']
            job_type = request.form['job_type']
            salary = request.form.get('salary', 'Not Specified')
            description = request.form['description']
            required_skill_names = request.form.getlist('required_skills')
            
            # Validation
            if not required_skill_names:
                flash('Please select at least one required skill', 'danger')
                return redirect(url_for('post_job'))

            employer = Employer.query.filter_by(user_id=session['user_id']).first()
            if not employer:
                flash('Employer profile not found!', 'danger')
                return redirect(url_for('employer_dashboard'))

            # Create new job with required skills (stored in lowercase)
            new_job = Job(
                job_title=job_title,
                company=company,
                location=location,
                job_type=job_type,
                salary=salary,
                description=description,
                employer_id=employer.id,
                required_skills=[skill.lower() for skill in required_skill_names]  # Store lowercase for consistent matching
            )

            db.session.add(new_job)
            db.session.commit()
            flash('Job posted successfully!', 'success')
            return redirect(url_for('employer_dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error posting job: {str(e)}', 'danger')
            app.logger.error(f"Error posting job: {str(e)}")

    # GET request - show form
    skills = Skill.query.all()
    return render_template('post_job.html', all_skills=skills)


@app.route('/employer/applicants/<int:job_id>')
def view_applicants(job_id):
    # Authentication check
    if 'user_id' not in session or session['role'] != 'employer':
        flash('Unauthorized!', 'danger')
        return redirect(url_for('login'))
    
    job = Job.query.get_or_404(job_id)
    employer = Employer.query.filter_by(user_id=session['user_id']).first()
    
    # Authorization check
    if job.employer_id != employer.id:
        flash('Unauthorized to view applicants for this job', 'danger')
        return redirect(url_for('employer_dashboard'))
    
    # Get all applications for this job with applicant details
    applications = (db.session.query(AppliedJob, Applicant, User)
                   .join(Applicant, AppliedJob.applicant_id == Applicant.id)
                   .join(User, Applicant.user_id == User.id)
                   .filter(AppliedJob.job_id == job_id)
                   .all())
    
    applicants_with_scores = []
    required_skills_lower = {skill.lower() for skill in (job.required_skills or [])}
    
    for application, applicant, user in applications:
        # Get applicant's skills (converted to lowercase)
        applicant_skills_lower = {skill.skill.skill_name.lower() for skill in applicant.skills}
        
        # Calculate exact matches
        exact_matches = required_skills_lower & applicant_skills_lower
        score = (len(exact_matches) / len(required_skills_lower) * 100) if required_skills_lower else 0
        
        # Get original skill names for display (from Skill table)
        matched_skill_objects = [skill for skill in applicant.skills 
                                if skill.skill.skill_name.lower() in exact_matches]
        
        applicants_with_scores.append({
            'application_id': application.id,
            'applicant_id': applicant.id,
            'name': user.username,
            'email': user.email,
            'phone': user.phone,
            'highest_qualification': applicant.highest_qualification,
            'experience_years': applicant.experience_years,
            'application_date': application.application_date,
            'status': application.status,
            'matched_skills': [skill.skill.skill_name for skill in matched_skill_objects],  # Original case
            'score': round(score, 2),
            'total_required_skills': len(required_skills_lower),
            'matched_skills_count': len(exact_matches),
            'resume_url': applicant.resume  # Corrected to use the existing attribute
        })
    
    # Sort by best matches first (highest score) by default
    sort_order = request.args.get('sort', 'desc')
    applicants_with_scores.sort(key=lambda x: x['score'], reverse=(sort_order == 'desc'))
    
    return render_template('applicant_screener.html',
                         job=job,
                         applicants=applicants_with_scores,
                         sort_order=sort_order,
                         now=datetime.utcnow())

@app.route('/application/update/<int:application_id>', methods=['POST'])
def update_application_status(application_id):
    if 'user_id' not in session or session['role'] != 'employer':
        flash('Unauthorized!', 'danger')
        return redirect(url_for('login'))
    
    application = AppliedJob.query.get_or_404(application_id)
    job = application.job
    
    # Verify the job belongs to this employer
    employer = Employer.query.filter_by(user_id=session['user_id']).first()
    if job.employer_id != employer.id:
        flash('Unauthorized to update this application', 'danger')
        return redirect(url_for('employer_dashboard'))
    
    new_status = request.form.get('status')
    if new_status not in ['pending', 'accepted', 'rejected']:
        flash('Invalid status', 'danger')
        return redirect(request.referrer or url_for('employer_dashboard'))
    
    application.status = new_status
    db.session.commit()
    
    flash(f'Application status updated to {new_status}', 'success')
    return redirect(request.referrer or url_for('employer_dashboard'))

# Skill management routes
@app.route('/manage_skill', methods=['POST'])
def manage_skill():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    skill_id = request.form.get('skill_id')
    skill_name = request.form.get('skill_name').strip()
    
    if not skill_name:
        flash('Skill name cannot be empty', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    try:
        if skill_id:  # Edit existing skill
            skill = Skill.query.get(skill_id)
            if not skill:
                flash('Skill not found', 'danger')
                return redirect(url_for('admin_dashboard'))
            
            # Check for duplicate name
            existing = Skill.query.filter(
                Skill.skill_name == skill_name,
                Skill.id != skill_id
            ).first()
            if existing:
                flash('Skill already exists', 'danger')
                return redirect(url_for('admin_dashboard'))
            
            skill.skill_name = skill_name
            db.session.commit()
            flash('Skill updated successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        
        else:  # Add new skill
            existing = Skill.query.filter_by(skill_name=skill_name).first()
            if existing:
                flash('Skill already exists', 'danger')
                return redirect(url_for('admin_dashboard'))
            
            new_skill = Skill(skill_name=skill_name)
            db.session.add(new_skill)
            db.session.commit()
            flash('Skill added successfully', 'success')
            return redirect(url_for('admin_dashboard'))
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/delete_skill/<int:skill_id>', methods=['DELETE'])
def delete_skill(skill_id):
    try:
        skill = Skill.query.get_or_404(skill_id)
        
        # First delete all ApplicantSkill associations
        ApplicantSkill.query.filter_by(skill_id=skill_id).delete()
        
        # Then delete the skill itself
        db.session.delete(skill)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Skill deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting skill: {str(e)}'
        }), 500

@app.route('/delete_applicant_skill/<int:applicant_skill_id>', methods=['DELETE'])
def delete_applicant_skill(applicant_skill_id):
    try:
        applicant_skill = ApplicantSkill.query.get_or_404(applicant_skill_id)
        db.session.delete(applicant_skill)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Applicant skill association deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting applicant skill: {str(e)}'
        }), 500

@app.route('/delete_database', methods=['POST'])
def delete_database():
    if 'user_id' in session and session['role'] == 'admin':
        try:
            db.drop_all()
            db.create_all()
            initialize_data()
            flash('Database reset successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    else:
        flash('Unauthorized!', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/applicant/resume/<int:applicant_id>')
def view_resume(applicant_id):
    if 'user_id' not in session or session['role'] != 'employer':
        flash('Unauthorized!', 'danger')
        return redirect(url_for('login'))
    
    applicant = Applicant.query.get_or_404(applicant_id)
    
    # Verify the employer has at least one job this applicant has applied to
    employer = Employer.query.filter_by(user_id=session['user_id']).first()
    if not employer:
        flash('Employer profile not found!', 'danger')
        return redirect(url_for('employer_dashboard'))
    
    has_application = AppliedJob.query.filter(
        AppliedJob.applicant_id == applicant.id,
        AppliedJob.job_id.in_([job.id for job in employer.jobs])
    ).first()
    
    if not has_application:
        flash('Unauthorized to view this resume', 'danger')
        return redirect(url_for('employer_dashboard'))
    
    if not applicant.resume:
        flash('Resume not uploaded by applicant', 'warning')
        return redirect(request.referrer or url_for('employer_dashboard'))
    
    return send_from_directory(os.path.join(app.root_path, 'static/resumes'), applicant.resume)

@app.route('/delete_job/<int:job_id>', methods=['GET','POST'])
def delete_job(job_id):
    # Authentication check
    if 'user_id' not in session or session['role'] != 'employer':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

    try:
        # Get the job and verify ownership
        job = Job.query.get_or_404(job_id)
        employer = Employer.query.filter_by(user_id=session['user_id']).first()
        
        if not employer or job.employer_id != employer.id:
            flash('You can only delete your own job postings', 'danger')
            return redirect(url_for('employer_dashboard'))

        # Delete all applications first (due to foreign key constraint)
        AppliedJob.query.filter_by(job_id=job_id).delete()
        
        # Then delete the job
        db.session.delete(job)
        db.session.commit()
        
        flash('Job posting deleted successfully', 'success')
        return redirect(url_for('employer_dashboard'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting job: {str(e)}', 'danger')
        app.logger.error(f"Error deleting job {job_id}: {str(e)}")
        return redirect(url_for('employer_dashboard'))
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=3200)
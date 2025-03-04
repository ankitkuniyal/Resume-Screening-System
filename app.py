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

# Employer Model
class Employer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(50), nullable=False)
    website = db.Column(db.String(255))
    address = db.Column(db.String(255), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(50), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    linkedin = db.Column(db.String(255))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    jobs = db.relationship('Job', backref='employer', lazy=True)

    def __repr__(self):
        return f"<Employer {self.company_name}>"

# Job Model
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    salary = db.Column(db.String(50))
    description = db.Column(db.Text, nullable=False)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer.id'), nullable=False)

    def __repr__(self):
        return f"<Job {self.job_title} at {self.company}>"

# Applicant Model
class Applicant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    experience_years = db.Column(db.Integer)
    resume_text = db.Column(db.Text, nullable=False)

    skills = db.relationship('ApplicantSkill', backref='applicant', lazy=True)

    def __repr__(self):
        return f"<Applicant {self.name}>"

# Skills Model
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<Skill {self.skill_name}>"

# Applicant Skills Model
class ApplicantSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicant.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)

    def __repr__(self):
        return f"<ApplicantSkill Applicant {self.applicant_id} - Skill {self.skill_id}>"

# Route for the homepage
@app.route('/')
def homepage():
    return render_template('homepage.html')

# Route for employer registration
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        company_name = request.form['company_name']
        industry = request.form['industry']
        website = request.form['website']
        address = request.form['address']
        fullname = request.form['fullname']
        designation = request.form['designation']
        contact = request.form['contact']
        linkedin = request.form['linkedin']
        email = request.form['email']
        password = generate_password_hash(request.form['login_password'])

        new_employer = Employer(company_name=company_name, industry=industry, website=website, address=address, 
                                fullname=fullname, designation=designation, contact=contact, linkedin=linkedin, 
                                email=email, password=password)
        
        db.session.add(new_employer)
        db.session.commit()  # Important to save changes
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('homepage'))
    
    return redirect(url_for('homepage'))

# Route for login
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = Employer.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        flash('Login successful!', 'success')
        return redirect(url_for('homepage'))
    else:
        flash('Invalid email or password', 'danger')
        return redirect(url_for('homepage'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created before running
    app.run(debug=True)

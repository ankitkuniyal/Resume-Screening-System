# populate_sample_data.py
from app import app, db
from app import User, Employer, Applicant, Job, Skill, ApplicantSkill, AppliedJob
from werkzeug.security import generate_password_hash
from datetime import datetime
import random

def create_sample_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Create sample skills
        tech_skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'SQL',
            'HTML/CSS', 'React', 'Django', 'Flask', 'Git',
            'AWS', 'Docker', 'Machine Learning', 'Data Analysis'
        ]
        
        skills = []
        for skill_name in tech_skills:
            skill = Skill(skill_name=skill_name)
            db.session.add(skill)
            skills.append(skill)
        db.session.commit()

        # Create admin user
        admin = User(
            username='Admin',
            email='admin@resumescreening.com',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)

        # Create sample employer
        employer_user = User(
            username='TechCorp',
            email='employer@techcorp.com',
            password=generate_password_hash('employer123'),
            role='employer'
        )
        db.session.add(employer_user)
        db.session.commit()

        employer = Employer(
            user_id=employer_user.id,
            industry='Technology',
            address='123 Tech Street',
            contact='555-1234',
            website='https://techcorp.com'
        )
        db.session.add(employer)
        db.session.commit()

        # Create sample jobs
        job_titles = [
            'Senior Python Developer',
            'Frontend React Developer',
            'DevOps Engineer',
            'Data Scientist',
            'Full Stack Developer'
        ]

        job_descriptions = [
            'We are looking for an experienced Python developer with Django/Flask experience.',
            'Join our frontend team to build amazing user interfaces with React.',
            'Help us improve our deployment pipeline and infrastructure.',
            'Work with our data team to build machine learning models.',
            'Full stack developer needed for our web applications.'
        ]

        jobs = []
        for i, title in enumerate(job_titles):
            # Assign 3-5 random skills to each job
            num_skills = random.randint(3, min(5, len(skills)))
            required_skills = random.sample(skills, num_skills)
            
            job = Job(
                job_title=title,
                company='TechCorp',
                location=random.choice(['Remote', 'New York', 'San Francisco', 'Austin']),
                job_type=random.choice(['Full-time', 'Contract', 'Part-time']),
                salary=f'${random.randint(80, 120)}k - ${random.randint(100, 150)}k',
                description=job_descriptions[i],
                employer_id=employer.id,
                required_skill_ids=[s.id for s in required_skills],
                posted_date=datetime.utcnow()
            )
            db.session.add(job)
            jobs.append(job)
        db.session.commit()

        # Create sample applicants
        applicant_names = [
            'Alice Johnson', 'Bob Smith', 'Charlie Brown', 
            'Diana Prince', 'Ethan Hunt', 'Fiona Green'
        ]

        applicants = []
        for i, name in enumerate(applicant_names):
            applicant_user = User(
                username=name,
                email=f'applicant{i+1}@example.com',
                password=generate_password_hash(f'applicant{i+1}'),
                role='applicant'
            )
            db.session.add(applicant_user)
            db.session.commit()

            applicant = Applicant(
                user_id=applicant_user.id,
                dob=datetime(1990 + i, 1, 1).date(),
                gender=random.choice(['Male', 'Female', 'Other']),
                address=f'{i+1} Main Street',
                highest_qualification=random.choice([
                    "High School", "Bachelor's", "Master's", "PhD"
                ]),
                field_of_study=random.choice([
                    'Computer Science', 'Engineering', 'Mathematics', 'Physics'
                ]),
                experience_years=random.randint(1, 10)
            )
            db.session.add(applicant)
            applicants.append(applicant)
        db.session.commit()

        # Assign skills to applicants
        for applicant in applicants:
            # Assign 3-5 random skills to each applicant
            num_skills = random.randint(3, min(5, len(skills)))
            assigned_skills = random.sample(skills, num_skills)
            
            for skill in assigned_skills:
                applicant_skill = ApplicantSkill(
                    applicant_id=applicant.id,
                    skill_id=skill.id
                )
                db.session.add(applicant_skill)
        db.session.commit()

        # Create some job applications
        for job in jobs:
            # Have 2-4 applicants apply for each job
            num_applicants = random.randint(2, min(4, len(applicants)))
            job_applicants = random.sample(applicants, num_applicants)
            
            for applicant in job_applicants:
                application = AppliedJob(
                    applicant_id=applicant.id,
                    job_id=job.id,
                    status=random.choice(['pending', 'accepted', 'rejected'])
                )
                db.session.add(application)
        db.session.commit()

        print("Successfully populated sample data!")
        print(f"Admin login: admin@resumescreening.com / admin123")
        print(f"Employer login: employer@techcorp.com / employer123")
        print(f"Applicant logins: applicant1@example.com / applicant1 (through applicant6)")

if __name__ == '__main__':
    create_sample_data()
# populate_sample_data.py
from app import app, db
from app import User, Employer, Applicant, Job, Skill, ApplicantSkill, AppliedJob
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random
from faker import Faker

fake = Faker()

def create_sample_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Create sample skills
        tech_skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Ruby', 'Go', 'Rust',
            'SQL', 'NoSQL', 'MongoDB', 'PostgreSQL', 'MySQL',
            'HTML/CSS', 'SASS', 'LESS', 'Bootstrap', 'Tailwind',
            'React', 'Angular', 'Vue.js', 'Svelte', 'jQuery',
            'Django', 'Flask', 'FastAPI', 'Spring', 'Laravel', 'Express',
            'Git', 'GitHub', 'GitLab', 'Bitbucket',
            'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes',
            'Machine Learning', 'Deep Learning', 'Data Analysis', 'Data Science',
            'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy',
            'Linux', 'Bash', 'Shell Scripting', 'PowerShell',
            'REST API', 'GraphQL', 'WebSockets', 'gRPC',
            'CI/CD', 'Jenkins', 'CircleCI', 'TravisCI',
            'TypeScript', 'Node.js', 'Deno', 'WebAssembly',
            'Blockchain', 'Solidity', 'Smart Contracts',
            'Cybersecurity', 'Ethical Hacking', 'Penetration Testing',
            'UI/UX Design', 'Figma', 'Adobe XD', 'Sketch',
            'Agile', 'Scrum', 'Kanban', 'DevOps', 'TDD', 'BDD'
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
            role='admin',
            phone=fake.phone_number()
        )
        db.session.add(admin)

        # Create sample employers (20 employers)
        industries = [
            'Technology', 'Finance', 'Healthcare', 'Education', 
            'Retail', 'Manufacturing', 'Entertainment', 'Telecommunications',
            'Automotive', 'Energy', 'Real Estate', 'Hospitality',
            'Aerospace', 'Defense', 'Biotechnology', 'Pharmaceutical',
            'E-commerce', 'Media', 'Consulting', 'Transportation'
        ]
        
        employers = []
        for i in range(20):
            employer_user = User(
                username=fake.company().replace(' ', '')[:20],
                email=f'employer{i+1}@example.com',
                password=generate_password_hash(f'employer{i+1}'),
                role='employer',
                phone=fake.phone_number()
            )
            db.session.add(employer_user)
            db.session.commit()

            employer = Employer(
                user_id=employer_user.id,
                industry=random.choice(industries),
                address=fake.address(),
                contact=fake.phone_number(),
                website=fake.url()
            )
            db.session.add(employer)
            employers.append(employer)
        db.session.commit()

        # Create sample jobs (100 jobs)
        job_titles = [
            'Senior Software Engineer', 'Junior Developer', 'DevOps Engineer', 
            'Data Scientist', 'Machine Learning Engineer', 'Frontend Developer',
            'Backend Developer', 'Full Stack Developer', 'Mobile Developer',
            'QA Engineer', 'Test Automation Engineer', 'Security Engineer',
            'Cloud Architect', 'Systems Administrator', 'Database Administrator',
            'Technical Lead', 'Engineering Manager', 'CTO', 'Product Manager',
            'UX Designer', 'UI Developer', 'Data Engineer', 'Business Analyst',
            'Scrum Master', 'Agile Coach', 'IT Consultant', 'Solutions Architect',
            'Network Engineer', 'Embedded Systems Engineer', 'Game Developer',
            'Blockchain Developer', 'AR/VR Developer', 'IoT Specialist',
            'AI Researcher', 'Big Data Engineer', 'Site Reliability Engineer',
            'Technical Writer', 'Support Engineer', 'Release Engineer'
        ]

        job_descriptions = [
            'We are looking for an experienced professional to join our team.',
            'Join our innovative team working on cutting-edge technologies.',
            'Help us build scalable and reliable software solutions.',
            'Work with a talented team to solve complex problems.',
            'We need someone passionate about technology and innovation.',
            'Opportunity to work on exciting projects with global impact.',
            'Be part of a fast-growing company with great culture.',
            'Collaborate with cross-functional teams to deliver great products.',
            'Work remotely with a distributed team of professionals.',
            'Help us transform our industry with technology solutions.'
        ]

        employment_types = ['Full-time', 'Part-time', 'Contract', 'Internship', 'Temporary']
        experience_levels = ['Entry-level', 'Mid-level', 'Senior', 'Executive']
        
        jobs = []
        for i in range(100):
            employer = random.choice(employers)
            posted_date = fake.date_time_between(start_date='-1y', end_date='now')
            
            # Generate a realistic salary range based on job title and experience
            base_salary = random.randint(40, 120)
            salary_range = f"${base_salary}k - ${base_salary + random.randint(20, 50)}k"
            
            # Assign 5-8 random skills to each job
            num_skills = random.randint(5, 8)
            required_skills = [skill.skill_name for skill in random.sample(skills, num_skills)]
            
            job = Job(
                job_title=f"{random.choice(experience_levels)} {random.choice(job_titles)}",
                company=employer.user.username,
                location=fake.city(),
                job_type=random.choice(employment_types),
                salary=salary_range,
                description=random.choice(job_descriptions),
                employer_id=employer.id,
                required_skills=required_skills,
                posted_date=posted_date
            )
            db.session.add(job)
            jobs.append(job)
        db.session.commit()

        # Create sample applicants (80 applicants)
        qualifications = [
            "High School Diploma", "Associate Degree", "Bachelor's Degree",
            "Master's Degree", "PhD", "Professional Certification"
        ]
        
        fields_of_study = [
            'Computer Science', 'Computer Engineering', 'Electrical Engineering',
            'Mechanical Engineering', 'Information Technology', 'Data Science',
            'Mathematics', 'Physics', 'Chemistry', 'Biology', 'Business',
            'Economics', 'Finance', 'Accounting', 'Marketing', 'Psychology',
            'Art and Design', 'Architecture', 'Civil Engineering', 'Medicine'
        ]
        
        applicants = []
        for i in range(80):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name}{last_name}{random.randint(10,99)}"
            
            applicant_user = User(
                username=username,
                email=f'applicant{i+1}@example.com',
                password=generate_password_hash(f'applicant{i+1}'),
                role='applicant',
                phone=fake.phone_number()
            )
            db.session.add(applicant_user)
            db.session.commit()

            years_exp = random.randint(0, 15)
            dob = fake.date_of_birth(minimum_age=18+years_exp, maximum_age=65)
            
            applicant = Applicant(
                user_id=applicant_user.id,
                dob=dob,
                gender=random.choice(['Male', 'Female', 'Other', 'Prefer not to say']),
                address=fake.address(),
                highest_qualification=random.choice(qualifications),
                field_of_study=random.choice(fields_of_study),
                experience_years=years_exp,
                resume_link=fake.url() if random.random() > 0.2 else None
            )
            db.session.add(applicant)
            applicants.append(applicant)
        db.session.commit()

        # Assign skills to applicants (3-10 skills each)
        for applicant in applicants:
            # More experienced applicants get more skills
            num_skills = min(len(skills), max(3, int(applicant.experience_years * 0.7)))
            assigned_skills = random.sample(skills, num_skills)
            
            for skill in assigned_skills:
                applicant_skill = ApplicantSkill(
                    applicant_id=applicant.id,
                    skill_id=skill.id
                )
                db.session.add(applicant_skill)
        db.session.commit()

        # Create job applications (3-10 applications per applicant)
        for applicant in applicants:
            # More experienced applicants apply to more jobs
            num_applications = min(len(jobs), max(3, int(applicant.experience_years * 0.8)))
            jobs_to_apply = random.sample(jobs, num_applications)
            
            for job in jobs_to_apply:
                # Check if applicant has at least 50% of required skills
                applicant_skills = {skill.skill.skill_name for skill in applicant.skills}
                required_skills = set(job.required_skills)
                matching_skills = applicant_skills.intersection(required_skills)
                
                # Higher chance of acceptance if more skills match
                if len(matching_skills) / len(required_skills) > 0.7:
                    status = random.choices(
                        ['accepted', 'pending', 'rejected'],
                        weights=[60, 30, 10]
                    )[0]
                else:
                    status = random.choices(
                        ['accepted', 'pending', 'rejected'],
                        weights=[10, 30, 60]
                    )[0]
                
                application_date = fake.date_time_between(
                    start_date=job.posted_date,
                    end_date='now'
                )
                
                application = AppliedJob(
                    applicant_id=applicant.id,
                    job_id=job.id,
                    status=status,
                    application_date=application_date
                )
                db.session.add(application)
        db.session.commit()

        print("Successfully populated sample data!")
        print(f"Admin login: admin@resumescreening.com / admin123")
        print(f"Employer logins: employer1@example.com / employer1 (through employer20)")
        print(f"Applicant logins: applicant1@example.com / applicant1 (through applicant80)")

if __name__ == '__main__':
    create_sample_data()
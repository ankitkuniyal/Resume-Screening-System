
# Resume Screening System

A Flask-based web application for employers to post jobs and screen applicants based on skill matching, with separate dashboards for applicants, employers, and administrators.

## Features

- **Three User Roles**:
  - Applicants: Can register, view jobs, and apply
  - Employers: Can post jobs and screen applicants
  - Admin: Manages users, skills, and system data

- **Skill-Based Matching**:
  - Jobs specify required skills by ID
  - Applicants' skills are matched against job requirements
  - Percentage match score calculated for each applicant

- **Application Tracking**:
  - Applicants can track their applications
  - Employers can update application status (pending/accepted/rejected)

- **Admin Tools**:
  - Manage skills database
  - View all system data
  - Reset database or populate sample data

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/resume-screening-system.git
   cd resume-screening-system
Set up a virtual environment (recommended):
bash
Copy
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
Install dependencies:
bash
Copy
pip install -r requirements.txt
Initialize the database:
bash
Copy
python app.py
(This will create the SQLite database with initial admin account)
Populate sample data (optional):
Log in as admin (admin@resumescreening.com / admin123)
Visit the admin dashboard
Click "Populate Sample Data" button
Configuration

Create a .env file for environment variables:

ini
Copy
SECRET_KEY=your-secret-key-here
Usage

Sample Accounts

Admin: admin@resumescreening.com / admin123
Employer: employer@techcorp.com / employer123
Applicants: applicant1@example.com / applicant1 (through applicant5)
Key Endpoints

/ - Homepage
/login - Login page
/register/applicant - Applicant registration
/register/employer - Employer registration
/admin/dashboard - Admin dashboard
/employer/post-job - Job posting form
/employer/applicants/<job_id> - View applicants for a job
Database Structure

Database Schema (Optional: Add an ER diagram image)

API Endpoints

POST /manage_skill - Add/edit skills (admin only)
DELETE /delete_skill/<int:skill_id> - Delete skill (admin only)
DELETE /delete_applicant_skill/<int:applicant_skill_id> - Remove skill from applicant
POST /application/update/<int:application_id> - Update application status
Project Structure

Copy
resume-screening-system/
├── app.py                 # Main application file
├── static/
│   ├── css/               # CSS files
│   ├── resumes/           # Uploaded resumes
│   └── uploads/           # Company logos
├── templates/             # Flask templates
├── requirements.txt       # Python dependencies
└── README.md              # This file
Dependencies

Python 3.8+
Flask
Flask-SQLAlchemy
Werkzeug (for password hashing)
License

This project is licensed under the MIT License - see the LICENSE file for details.

Screenshots

(Optional: Add screenshots of your application here)

Applicant Dashboard
Employer Job Posting
Admin Skill Management
Contributing

Fork the project
Create your feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request
Copy

### Additional Recommendations:

1. Create a `requirements.txt` file with:
Flask==2.0.1
Flask-SQLAlchemy==2.5.1
Werkzeug==2.0.1
python-dotenv==0.19.0

Copy

2. For a more professional README, consider adding:
   - Badges (build status, coverage, etc.)
   - More detailed screenshots
   - GIF demo of the application in action
   - Deployment instructions

3. You may want to create a `docs/` folder for:
   - Database schema diagram
   - More detailed documentation
   - Screenshots

This README provides a comprehensive overview of your project while remaining clear and accessible to potential users or contributors.
# Resume Screening System

A Flask-based web application for employers to post jobs and screen applicants based on skill matching, with separate dashboards for applicants, employers, and administrators.

## Features

- **Three User Roles**:
  - **Applicants**: Can register, view jobs, and apply.
  - **Employers**: Can post jobs and screen applicants.
  - **Admin**: Manages users, skills, and system data.

- **Skill-Based Matching**:
  - Jobs specify required skills by ID.
  - Applicants' skills are matched against job requirements.
  - Percentage match score calculated for each applicant.

- **Application Tracking**:
  - Applicants can track their applications.
  - Employers can update application status (pending/accepted/rejected).

- **Admin Tools**:
  - Manage skills database.
  - View all system data.
  - Reset database or populate sample data.

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/ankitkuniyal/resume-screening-system.git
cd resume-screening-system
```

### 2. Set Up a Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create a `.env` File for Configuration
Create a `.env` file in the root directory and add:
```
SECRET_KEY=your-secret-key-here
```

### 5. Initialize the Database
```bash
python app.py
```
(This will create the SQLite database with an initial admin account.)

### 6. Populate Sample Data (Optional)
1. Log in as admin (`admin@resumescreening.com / admin123`)
2. Visit the admin dashboard
3. Click the "Populate Sample Data" button

## Usage

### Sample Accounts
- **Admin**: `admin@resumescreening.com / admin123`
- **Employer**: `employer@techcorp.com / employer123`
- **Applicants**: `applicant1@example.com` through `applicant5@example.com`

### Key Endpoints
- `/` - Homepage
- `/login` - Login page
- `/register/applicant` - Applicant registration
- `/register/employer` - Employer registration
- `/admin/dashboard` - Admin dashboard
- `/employer/post-job` - Job posting form
- `/employer/applicants/<job_id>` - View applicants for a job

## Database Structure

The system uses **SQLite** as the database. Below are the key models:

### **User Model**
- `id`: Primary Key
- `email`: Unique identifier
- `password`: Hashed password
- `role`: (admin, employer, applicant)

### **Job Model**
- `id`: Primary Key
- `title`: Job title
- `description`: Job description
- `skills_required`: JSON of required skills
- `employer_id`: Foreign key (Employer)

### **Application Model**
- `id`: Primary Key
- `applicant_id`: Foreign key (Applicant)
- `job_id`: Foreign key (Job)
- `status`: Pending/Accepted/Rejected

## API Endpoints
- `POST /manage_skill` - Add/edit skills (admin only)
- `DELETE /delete_skill/<int:skill_id>` - Delete skill (admin only)
- `DELETE /delete_applicant_skill/<int:applicant_skill_id>` - Remove skill from applicant
- `POST /application/update/<int:application_id>` - Update application status

## Project Structure
```
resume-screening-system/
├── app.py                 # Main application file
├── static/
│   ├── css/               # CSS files
│   ├── resumes/           # Uploaded resumes
│   └── uploads/           # Company logos
├── templates/             # Flask templates
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── README.md              # This file
```

## Dependencies
```txt
Flask==2.2.5
Flask-SQLAlchemy==3.0.3
Werkzeug==2.2.3
python-dotenv==0.19.0
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Screenshots


## Contributing
1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Additional Recommendations
- Add **badges** (build status, coverage, etc.)
- Include **detailed screenshots**
- Provide a **GIF demo** of the application in action
- Expand **documentation** under a `docs/` folder
  - Database schema diagram
  - More detailed documentation
  - Additional screenshots

---

This README provides a comprehensive overview of the project, setup, and functionality while ensuring clarity and accessibility for developers and contributors. 🚀


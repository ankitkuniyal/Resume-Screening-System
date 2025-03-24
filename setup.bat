@echo off
echo Starting Flask + PostgreSQL Setup...

REM 1. Install necessary Python packages
echo Installing Python dependencies...
pip install -r requirements.txt

REM 2. Create PostgreSQL Database
echo Setting up PostgreSQL database...
psql -U postgres -c "CREATE DATABASE resume_screening;"
psql -U postgres -c "CREATE USER postgres WITH PASSWORD 'password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE resume_screening TO postgres;"

REM 3. Apply Flask Migrations
echo Applying Flask migrations...
set FLASK_APP=app.py
flask db upgrade

REM 4. Start the Flask App
echo Starting the Flask server...
flask run

echo Setup Complete
pause

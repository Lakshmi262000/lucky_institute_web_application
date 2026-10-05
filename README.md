# Lucky Institute

A Python-based web application for managing training institute operations, trainees, applications, and interview tracking.

## Features
- Role-based authentication for CEO, admins, and trainees
- Batch management with trainee assignment
- Trainee profile management and privacy controls
- Job application and interview tracking
- Dashboard analytics for management and trainees
- PostgreSQL-ready database configuration

## Tech stack
- Python + Flask
- PostgreSQL via SQLAlchemy and psycopg
- Flask-Login for authentication

## Setup
1. Create a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and update your PostgreSQL credentials.
4. Start PostgreSQL and create the `lucky_institute` database.
5. Run the app:
   ```bash
   python app.py
   ```

## Default login accounts
- CEO: `isha@luckyinstitute.com` / `Lucky@123`
- Teacher admin: `teacher@luckyinstitute.com` / `Admin@123`
- HR admin: `hr@luckyinstitute.com` / `Admin@123`
- Trainee: `sara@luckyinstitute.com` / `Trainee@123`

## Notes
The project defaults to PostgreSQL, but can fall back to SQLite when needed for local testing. Update the `DATABASE_URL` in `.env` for your production or development database.

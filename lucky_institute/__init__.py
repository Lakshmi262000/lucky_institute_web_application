from datetime import date

from flask import Flask, redirect, url_for
from flask_login import current_user
from werkzeug.security import generate_password_hash

from lucky_institute.admin_routes import bp as admin_bp
from lucky_institute.auth_routes import bp as auth_bp
from lucky_institute.config import Config
from lucky_institute.extensions import db, login_manager
from lucky_institute.models import Batch, Interview, JobApplication, TraineeProfile, User
from lucky_institute.trainee_routes import bp as trainee_bp


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(trainee_bp)

    @app.route("/")
    def index():
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if current_user.role == "trainee":
            return redirect(url_for("trainee.dashboard"))
        return redirect(url_for("admin.dashboard"))

    with app.app_context():
        db.create_all()
        seed_sample_data()

    return app


def seed_sample_data():
    if User.query.filter_by(email="isha@luckyinstitute.com").first():
        return

    ceo = User(full_name="Isha", email="isha@luckyinstitute.com", phone="+91 90000 11111", password_hash=generate_password_hash("Lucky@123"), role="ceo")
    teacher = User(full_name="Nisha Teacher", email="teacher@luckyinstitute.com", phone="+91 90000 22222", password_hash=generate_password_hash("Admin@123"), role="admin")
    hr = User(full_name="Ravi HR", email="hr@luckyinstitute.com", phone="+91 90000 33333", password_hash=generate_password_hash("Admin@123"), role="admin")

    db.session.add_all([ceo, teacher, hr])
    db.session.flush()

    batch1 = Batch(name="Batch 1", course_name="Python Full Stack", start_date=date(2025, 1, 15), end_date=date(2025, 7, 15))
    batch2 = Batch(name="Batch 2", course_name="Data Analytics", start_date=date(2025, 2, 1), end_date=date(2025, 8, 1))
    db.session.add_all([batch1, batch2])
    db.session.flush()

    trainees = [
        {
            "full_name": "Sara Khan",
            "email": "sara@luckyinstitute.com",
            "phone": "+91 90000 44444",
            "password": "Trainee@123",
            "trainee_id": "LI-101",
            "course": "Python Full Stack",
            "batch_id": batch1.id,
            "application_status": "Selected",
            "interview_status": "Selected",
        },
        {
            "full_name": "Aman Verma",
            "email": "aman@luckyinstitute.com",
            "phone": "+91 90000 55555",
            "password": "Trainee@123",
            "trainee_id": "LI-102",
            "course": "Python Full Stack",
            "batch_id": batch1.id,
            "application_status": "Rejected",
            "interview_status": "Rejected",
        },
        {
            "full_name": "Meera Iyer",
            "email": "meera@luckyinstitute.com",
            "phone": "+91 90000 66666",
            "password": "Trainee@123",
            "trainee_id": "LI-201",
            "course": "Data Analytics",
            "batch_id": batch2.id,
            "application_status": "Pending",
            "interview_status": "Scheduled",
        },
    ]

    for item in trainees:
        user = User(
            full_name=item["full_name"],
            email=item["email"],
            phone=item["phone"],
            password_hash=generate_password_hash(item["password"]),
            role="trainee",
        )
        db.session.add(user)
        db.session.flush()

        profile = TraineeProfile(
            user_id=user.id,
            trainee_id=item["trainee_id"],
            course=item["course"],
            batch_id=item["batch_id"],
            joining_date=date(2025, 1, 15),
            account_status="Active",
        )
        db.session.add(profile)
        db.session.flush()

        application = JobApplication(
            user_id=user.id,
            company_name="ABC Technologies" if item["application_status"] in {"Selected", "Rejected"} else "XYZ Systems",
            job_role="Python Developer" if item["course"] == "Python Full Stack" else "Data Analyst",
            application_date=date(2025, 3, 10),
            application_status=item["application_status"],
            hr_name="Mira Shah",
            hr_phone="+91 98765 12345",
            hr_email="mira@abc.com",
            notes="Application tracked through institute placement portal.",
        )
        db.session.add(application)
        db.session.flush()

        if item["interview_status"]:
            interview = Interview(
                user_id=user.id,
                job_application_id=application.id,
                company_name=application.company_name,
                job_role=application.job_role,
                interview_date=date(2025, 3, 20),
                interview_time="10:30 AM",
                interview_type="Online",
                interview_round="Round 1",
                interview_status=item["interview_status"],
                hr_name="Mira Shah",
                hr_phone="+91 98765 12345",
                hr_email="mira@abc.com",
                notes="Candidate profile reviewed and interview scheduled.",
            )
            db.session.add(interview)

    db.session.commit()

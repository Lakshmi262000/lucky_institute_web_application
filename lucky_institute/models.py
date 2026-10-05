from datetime import datetime

from flask_login import UserMixin

from lucky_institute.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="trainee")
    phone = db.Column(db.String(30), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship("TraineeProfile", back_populates="user", uselist=False)
    job_applications = db.relationship("JobApplication", back_populates="user", cascade="all, delete-orphan")
    interviews = db.relationship("Interview", back_populates="user", cascade="all, delete-orphan")

    @property
    def is_admin(self):
        return self.role in {"ceo", "admin"}


class Batch(db.Model):
    __tablename__ = "batches"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    course_name = db.Column(db.String(120), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    trainees = db.relationship("TraineeProfile", back_populates="batch")


class TraineeProfile(db.Model):
    __tablename__ = "trainee_profiles"

    id = db.Column(db.Integer, primary_key=True)
    trainee_id = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    course = db.Column(db.String(120), nullable=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=True)
    joining_date = db.Column(db.Date, nullable=True)
    skills = db.Column(db.Text, nullable=True)
    education = db.Column(db.Text, nullable=True)
    resume = db.Column(db.String(255), nullable=True)
    profile_photo = db.Column(db.String(255), nullable=True)
    account_status = db.Column(db.String(30), default="Active")

    user = db.relationship("User", back_populates="profile")
    batch = db.relationship("Batch", back_populates="trainees")


class JobApplication(db.Model):
    __tablename__ = "job_applications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    company_name = db.Column(db.String(120), nullable=False)
    job_role = db.Column(db.String(120), nullable=False)
    application_date = db.Column(db.Date, nullable=False)
    application_status = db.Column(db.String(40), default="Pending")
    hr_name = db.Column(db.String(120), nullable=True)
    hr_phone = db.Column(db.String(30), nullable=True)
    hr_email = db.Column(db.String(120), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="job_applications")
    interviews = db.relationship("Interview", back_populates="job_application", cascade="all, delete-orphan")


class Interview(db.Model):
    __tablename__ = "interviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_application_id = db.Column(db.Integer, db.ForeignKey("job_applications.id"), nullable=False)
    company_name = db.Column(db.String(120), nullable=False)
    job_role = db.Column(db.String(120), nullable=False)
    interview_date = db.Column(db.Date, nullable=False)
    interview_time = db.Column(db.String(20), nullable=True)
    interview_type = db.Column(db.String(30), nullable=False)
    interview_round = db.Column(db.String(30), nullable=False)
    interview_status = db.Column(db.String(40), default="Scheduled")
    hr_name = db.Column(db.String(120), nullable=True)
    hr_phone = db.Column(db.String(30), nullable=True)
    hr_email = db.Column(db.String(120), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="interviews")
    job_application = db.relationship("JobApplication", back_populates="interviews")

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash

from lucky_institute.extensions import db
from lucky_institute.models import Interview, JobApplication, TraineeProfile
from lucky_institute.utils import get_dashboard_stats_for_trainee, safe_date

bp = Blueprint("trainee", __name__)


def ensure_own_record(fn):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "trainee":
            flash("This page is only available to trainees.", "danger")
            return redirect(url_for("index"))
        return fn(*args, **kwargs)

    wrapper.__name__ = fn.__name__
    return wrapper


@bp.route("/trainee")
@login_required
@ensure_own_record
def dashboard():
    stats = get_dashboard_stats_for_trainee(current_user)
    applications = JobApplication.query.filter_by(user_id=current_user.id).order_by(JobApplication.application_date.desc()).all()
    interviews = Interview.query.filter_by(user_id=current_user.id).order_by(Interview.interview_date.desc()).all()
    return render_template("trainee/dashboard.html", stats=stats, applications=applications, interviews=interviews)


@bp.route("/trainee/profile", methods=["GET", "POST"])
@login_required
@ensure_own_record
def profile():
    profile = current_user.profile
    if request.method == "POST":
        if not profile:
            profile = TraineeProfile(user_id=current_user.id, trainee_id=current_user.email.split("@")[0].upper())
            db.session.add(profile)
        profile.date_of_birth = safe_date(request.form.get("date_of_birth"))
        profile.gender = request.form.get("gender")
        profile.address = request.form.get("address")
        profile.course = request.form.get("course")
        profile.skills = request.form.get("skills")
        profile.education = request.form.get("education")
        profile.account_status = request.form.get("account_status") or profile.account_status
        current_user.full_name = request.form.get("full_name") or current_user.full_name
        current_user.phone = request.form.get("phone") or current_user.phone
        db.session.commit()
        flash("Your profile was updated successfully.", "success")
        return redirect(url_for("trainee.profile"))

    return render_template("trainee/profile.html", profile=profile)


@bp.route("/trainee/applications", methods=["GET", "POST"])
@login_required
@ensure_own_record
def applications():
    if request.method == "POST":
        application = JobApplication(
            user_id=current_user.id,
            company_name=request.form.get("company_name"),
            job_role=request.form.get("job_role"),
            application_date=safe_date(request.form.get("application_date")),
            application_status=request.form.get("application_status") or "Pending",
            hr_name=request.form.get("hr_name"),
            hr_phone=request.form.get("hr_phone"),
            hr_email=request.form.get("hr_email"),
            notes=request.form.get("notes"),
        )
        db.session.add(application)
        db.session.commit()
        flash("Company application saved successfully.", "success")
        return redirect(url_for("trainee.applications"))

    applications_list = JobApplication.query.filter_by(user_id=current_user.id).order_by(JobApplication.application_date.desc()).all()
    return render_template("trainee/applications.html", applications=applications_list)


@bp.route("/trainee/interviews", methods=["GET", "POST"])
@login_required
@ensure_own_record
def interviews():
    if request.method == "POST":
        application_id = request.form.get("job_application_id")
        application = JobApplication.query.filter_by(id=application_id, user_id=current_user.id).first()
        if not application:
            flash("Invalid application selected.", "danger")
            return redirect(url_for("trainee.interviews"))

        interview = Interview(
            user_id=current_user.id,
            job_application_id=application.id,
            company_name=application.company_name,
            job_role=application.job_role,
            interview_date=safe_date(request.form.get("interview_date")),
            interview_time=request.form.get("interview_time"),
            interview_type=request.form.get("interview_type") or "Online",
            interview_round=request.form.get("interview_round") or "Round 1",
            interview_status=request.form.get("interview_status") or "Scheduled",
            hr_name=request.form.get("hr_name") or application.hr_name,
            hr_phone=request.form.get("hr_phone") or application.hr_phone,
            hr_email=request.form.get("hr_email") or application.hr_email,
            notes=request.form.get("notes"),
        )
        db.session.add(interview)
        db.session.commit()
        flash("Interview entry saved successfully.", "success")
        return redirect(url_for("trainee.interviews"))

    applications = JobApplication.query.filter_by(user_id=current_user.id).all()
    interviews_list = Interview.query.filter_by(user_id=current_user.id).order_by(Interview.interview_date.desc()).all()
    return render_template("trainee/interviews.html", applications=applications, interviews=interviews_list)

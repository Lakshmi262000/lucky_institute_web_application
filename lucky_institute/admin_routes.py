from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash

from lucky_institute.extensions import db
from lucky_institute.models import Batch, TraineeProfile, User
from lucky_institute.utils import get_admin_dashboard_stats, safe_date

bp = Blueprint("admin", __name__)


def role_required(*allowed_roles):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.role not in allowed_roles:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for("index"))
            return fn(*args, **kwargs)

        wrapper.__name__ = fn.__name__
        return wrapper

    return decorator


@bp.route("/admin")
@login_required
@role_required("ceo", "admin")
def dashboard():
    stats = get_admin_dashboard_stats()
    trainees = []
    for user in User.query.filter_by(role="trainee").order_by(User.full_name.asc()).all():
        trainees.append({
            "user": user,
            "profile": user.profile,
        })
    batches = Batch.query.order_by(Batch.name.asc()).all()
    return render_template("admin/dashboard.html", stats=stats, trainees=trainees, batches=batches)


@bp.route("/admin/trainees")
@login_required
@role_required("ceo", "admin")
def trainees():
    query = User.query.filter_by(role="trainee")
    batch_id = request.args.get("batch_id")
    course = request.args.get("course", "")
    name = request.args.get("name", "")
    trainee_id = request.args.get("trainee_id", "")

    if batch_id:
        query = query.join(TraineeProfile).filter(TraineeProfile.batch_id == int(batch_id))
    if course:
        query = query.join(TraineeProfile).filter(TraineeProfile.course.ilike(f"%{course}%"))
    if name:
        query = query.filter(User.full_name.ilike(f"%{name}%"))
    if trainee_id:
        query = query.join(TraineeProfile).filter(TraineeProfile.trainee_id.ilike(f"%{trainee_id}%"))

    trainees = query.order_by(User.full_name.asc()).all()
    batches = Batch.query.order_by(Batch.name.asc()).all()
    return render_template("admin/trainees.html", trainees=trainees, batches=batches)


@bp.route("/admin/trainees/<int:user_id>")
@login_required
@role_required("ceo", "admin")
def trainee_detail(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("admin/trainee_detail.html", user=user)


@bp.route("/admin/batches", methods=["GET", "POST"])
@login_required
@role_required("ceo", "admin")
def batches():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        course_name = request.form.get("course_name", "").strip()
        start_date = safe_date(request.form.get("start_date"))
        end_date = safe_date(request.form.get("end_date"))

        if not all([name, course_name, start_date, end_date]):
            flash("Please fill every batch field.", "danger")
        else:
            batch = Batch(name=name, course_name=course_name, start_date=start_date, end_date=end_date)
            db.session.add(batch)
            db.session.commit()
            flash("Batch created successfully.", "success")
            return redirect(url_for("admin.batches"))

    batch_list = Batch.query.order_by(Batch.name.asc()).all()
    return render_template("admin/batches.html", batches=batch_list)


@bp.route("/admin/trainees/add", methods=["POST"])
@login_required
@role_required("ceo", "admin")
def add_trainee():
    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    phone = request.form.get("phone", "").strip()
    trainee_id = request.form.get("trainee_id", "").strip()
    course = request.form.get("course", "").strip()
    batch_id = request.form.get("batch_id")
    password = request.form.get("password", "") or "Trainee@123"

    if not all([full_name, email, trainee_id, course]):
        flash("Please provide all required trainee details.", "danger")
        return redirect(url_for("admin.dashboard"))

    if User.query.filter_by(email=email).first():
        flash("A user with this email already exists.", "danger")
        return redirect(url_for("admin.dashboard"))

    user = User(full_name=full_name, email=email, phone=phone, password_hash=generate_password_hash(password), role="trainee")
    db.session.add(user)
    db.session.flush()

    profile = TraineeProfile(
        user_id=user.id,
        trainee_id=trainee_id,
        course=course,
        batch_id=int(batch_id) if batch_id else None,
        joining_date=datetime.utcnow().date(),
        account_status="Active",
    )
    db.session.add(profile)
    db.session.commit()
    flash("Trainee added successfully.", "success")
    return redirect(url_for("admin.trainees"))


@bp.route("/admin/users/add-admin", methods=["POST"])
@login_required
@role_required("ceo")
def add_admin():
    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    role = request.form.get("role", "admin")
    password = request.form.get("password", "") or "Admin@123"

    if not all([full_name, email]):
        flash("Please provide the admin name and email.", "danger")
        return redirect(url_for("admin.dashboard"))

    if User.query.filter_by(email=email).first():
        flash("An account with this email already exists.", "danger")
        return redirect(url_for("admin.dashboard"))

    user = User(full_name=full_name, email=email, password_hash=generate_password_hash(password), role=role if role in {"ceo", "admin"} else "admin")
    db.session.add(user)
    db.session.commit()
    flash("Admin account created successfully.", "success")
    return redirect(url_for("admin.dashboard"))

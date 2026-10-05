from datetime import datetime

from lucky_institute.models import Interview, JobApplication


def safe_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def get_dashboard_stats_for_trainee(user):
    applications = JobApplication.query.filter_by(user_id=user.id).all()
    interview_rows = Interview.query.filter_by(user_id=user.id).all()

    total_applied = len(applications)
    total_interviews = len(interview_rows)
    interviews_completed = sum(1 for row in interview_rows if row.interview_status.lower() in {"attended", "selected", "rejected"})
    selected_companies = sum(1 for item in applications if item.application_status.lower() in {"selected", "job offered"})
    rejected_applications = sum(1 for item in applications if item.application_status.lower() in {"rejected", "not selected"})
    pending_applications = sum(1 for item in applications if item.application_status.lower() in {"pending", "on hold"})

    return {
        "total_applied": total_applied,
        "interview_calls": total_interviews,
        "interviews_completed": interviews_completed,
        "selected_companies": selected_companies,
        "rejected_applications": rejected_applications,
        "pending_applications": pending_applications,
    }


def get_admin_dashboard_stats():
    from lucky_institute.models import Batch, TraineeProfile, User

    trainees = User.query.filter_by(role="trainee").count()
    batches = Batch.query.count()
    total_applications = JobApplication.query.count()
    total_interviews = Interview.query.count()
    selected_trainees = JobApplication.query.filter(JobApplication.application_status.in_(["Selected", "Job Offered"])).count()
    rejected_trainees = JobApplication.query.filter(JobApplication.application_status.in_(["Rejected", "Not Selected"])).count()
    pending_interviews = Interview.query.filter(Interview.interview_status.in_(["Scheduled", "Pending"])).count()
    batch_counts = []
    for batch in Batch.query.order_by(Batch.name).all():
        counts = TraineeProfile.query.filter_by(batch_id=batch.id).count()
        batch_counts.append({"name": batch.name, "course": batch.course_name, "count": counts})

    return {
        "total_trainees": trainees,
        "total_batches": batches,
        "total_companies_applied": total_applications,
        "total_interviews": total_interviews,
        "total_selected_trainees": selected_trainees,
        "total_rejected_trainees": rejected_trainees,
        "pending_interviews": pending_interviews,
        "batch_counts": batch_counts,
    }
